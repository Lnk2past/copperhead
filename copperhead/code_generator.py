import re
from copperhead.__version__ import __version__ as version
from copperhead.templates.basic_wrapper import template
from copperhead.templates.container_conversions import \
    to_python_list_template, \
    to_python_list_intermediate_template, \
    to_python_list_intermediate_template_2, \
    to_python_list_inner_template, \
    from_python_list_template, \
    from_python_list_intermediate_template, \
    from_python_list_inner_template

import copperhead.templates.cpp_types as cpp_types


def _indent_block(block, indent):
    return block.replace('\n', '\n' + '    '*indent)


def _parse_template(full_type):
    template_type_re = re.compile('(.*?)<(.*)>')
    searches = template_type_re.search(full_type)
    return (searches.group(1), searches.group(2))


def _convert_container_to_python(arg_type, layer_index, block=to_python_list_template):
    previous_layer_index = '' if (layer_index in ['', 1]) else layer_index-1
    next_layer_index = 1 if not layer_index else layer_index+1

    container, template_type = _parse_template(arg_type)
    variable = 'return_value_raw{}'.format(layer_index)
    get_size_function = cpp_types.container_types[container].get_size_function.format(variable=variable)

    block = block.format(**locals())
    block = block.replace('}', '}}').replace('{', '{{')

    if template_type not in cpp_types.basic_types:
        new_layer_type = to_python_list_intermediate_template.format(**locals())
        new_block = _indent_block(new_layer_type + to_python_list_template, next_layer_index)
        block = block.replace('<next_layer>', new_block)
        block = _convert_container_to_python(template_type, next_layer_index, block)
        block = block.replace('<finalize_set>', to_python_list_intermediate_template_2.format(**locals()))
    else:
        to_python_function = cpp_types.basic_types[template_type].to_python_function
        new_block = _indent_block(to_python_list_inner_template.format(**locals()), next_layer_index-1)
        block = block.replace('<next_layer>', new_block)
        block = block.replace('<finalize_set>', '', 1)
        return block

    return block


def _convert_container_from_python(name, arg_type, layer_index, block=from_python_list_template):
    next_layer_index = 1 if not layer_index else layer_index+1

    container, template_type = _parse_template(arg_type)
    if block == from_python_list_template and hasattr(cpp_types.container_types[container], 'from_python_list_template'):
        block = cpp_types.container_types[container].from_python_list_template

    variable = '{}_container{}'.format(name, layer_index)
    insertion_function = cpp_types.container_types[container].insertion_function.format(variable=variable)

    block = block.format(**locals())
    block = block.replace('}', '}}').replace('{', '{{')

    if template_type not in cpp_types.basic_types:
        t1 = from_python_list_intermediate_template
        if hasattr(cpp_types.container_types[container], 'from_python_list_intermediate_template'):
            t1 = cpp_types.container_types[container].from_python_list_intermediate_template

        t2 = from_python_list_template
        if hasattr(cpp_types.container_types[container], 'from_python_list_template'):
            t2 = cpp_types.container_types[container].from_python_list_template

        new_layer_type = t1.format(**locals())
        new_block = _indent_block(new_layer_type + t2, next_layer_index)
        block = block.replace('<next_layer>', new_block)
        block = _convert_container_from_python(name, template_type, next_layer_index, block)
    else:
        t3 = from_python_list_inner_template
        if hasattr(cpp_types.container_types[container], 'from_python_list_inner_template'):
            t3 = cpp_types.container_types[container].from_python_list_inner_template

        from_python_function = cpp_types.basic_types[template_type].from_python_function
        new_block = _indent_block(t3.format(**locals()), next_layer_index-1)
        block = block.replace('<next_layer>', new_block)
        return block

    return block


def _make_wrapper(block_name, block_signature):
    return_type_re = re.compile(r'(.*)\(')
    args_type_list_re = re.compile(r'.*\((.*)\)')
    arg_strippable_re = re.compile(r'const|volatile|&')

    return_type = return_type_re.search(block_signature).group(1).strip()
    args_type_list = [arg.strip() for arg in args_type_list_re.search(block_signature).group(1).split(',')]

    wrapper_body = ''
    args = []

    if args_type_list and args_type_list[0]:
        format_str = ''
        arg_name = 65
        conversion_args = []
        for arg_type in args_type_list:
            arg_type = re.sub(arg_strippable_re, '', arg_type)
            if arg_type in cpp_types.basic_types:
                format_str += cpp_types.basic_types[arg_type].format_unit
                python_type = cpp_types.basic_types[arg_type].c_type
            else:
                for cpp_type in cpp_types.container_types.keys():
                    if arg_type.startswith(cpp_type):
                        format_str += cpp_types.container_types[cpp_type].format_unit
                        python_type = cpp_types.container_types[cpp_type].c_type
                        conversion_args.append((chr(arg_name), arg_type))
                        break

            wrapper_body += '        {} {};\n'.format(python_type, chr(arg_name))

            args.append(chr(arg_name))
            arg_name += 1

        args_str = ', '.join(['&{}'.format(arg) for arg in args])
        wrapper_body += '        if (!PyArg_ParseTuple(args, "{}", {})) return nullptr;\n'.format(format_str, args_str)

        for conversion_arg in conversion_args:
            name, arg_type = conversion_arg

            block = '        {arg_type} {name}_container;\n'.format(arg_type=arg_type, name=name)
            block += _convert_container_from_python(name, arg_type, '')
            wrapper_body += block.format()
            
            args[args.index(name)] = '{name}_container'.format(name=name)

    return_value = ''
    if return_type != 'void':
        return_value = 'auto return_value_raw = '

    wrapper_body += '\n        {}{}({});\n'.format(return_value, block_name, ','.join(args))

    if return_type == 'void':
        wrapper_body += '        Py_RETURN_NONE;'
    else:
        if return_type in cpp_types.basic_types:
            wrapper_body += '        return {}(return_value_raw);'.format(cpp_types.basic_types[return_type].to_python_function)
        elif return_type == 'std::string':
            wrapper_body += '        return {}(return_value_raw.c_str());'.format(cpp_types.container_types[return_type].to_python_function)
        else:
            for cpp_type in cpp_types.container_types.keys():
                if return_type.startswith(cpp_type):
                    break

            get_size_function = cpp_types.container_types[cpp_type].get_size_function.format(variable='return_value_raw')
            block = '        PyObject* return_value_list = PyList_New({get_size_function});'.format(get_size_function=get_size_function)
            block += _convert_container_to_python(return_type, '')
            wrapper_body += block.format()
            wrapper_body += '        return return_value_list;'

    return wrapper_body


def create(filename, block_name, block_signature, block):
    with open(filename, 'w') as sf:
        block_wrapper_body = _make_wrapper(block_name, block_signature)
        sf.write(template.format(**locals(), version=version))
