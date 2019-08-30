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


class TypeConversion:
    def __init__(self, cpp_type, format_unit, to_python_function=None, from_python_function=None, c_type=None, insertion_function=None, get_size_function=None):
        self.cpp_type = cpp_type
        self.c_type = c_type if c_type else cpp_type
        self.format_unit = format_unit
        self.to_python_function = to_python_function
        self.from_python_function = from_python_function
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function


basic_types = {
    'short': TypeConversion('short', 'h', 'PyLong_FromLong', 'PyLong_AsLong'),
    'int': TypeConversion('int', 'i', 'PyLong_FromLong', 'PyLong_AsLong'),
    'long': TypeConversion('long', 'l', 'PyLong_FromLong', 'PyLong_AsLong'),
    'long long': TypeConversion('long long', 'L', 'PyLong_FromLongLong', 'PyLong_AsLongLong'),
    'unsigned char': TypeConversion('unsigned char', 'b', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong'),
    'unsigned short': TypeConversion('unsigned short', 'H', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong'),
    'unsigned int': TypeConversion('unsigned int', 'I', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong'),
    'unsigned long': TypeConversion('unsigned long', 'k', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong'),
    'unsigned long long': TypeConversion('unsigned long long', 'K', 'PyLong_FromLongUnsignedLong', 'PyLong_AsUnsignedLongLong'),
    'float': TypeConversion('float', 'f', 'PyFloat_FromDouble', 'PyFloat_AsDouble'),
    'double': TypeConversion('double', 'd', 'PyFloat_FromDouble', 'PyFloat_AsDouble'),
    'std::string': TypeConversion('std::string', 's', 'PyUnicode_FromString', c_type='char*'),
}


container_types = {
    'std::vector': TypeConversion('std::vector', 'O', c_type='PyObject*', insertion_function='{variable}.emplace_back()', get_size_function='{variable}.size()'),
    'std::deque': TypeConversion('std::deque', 'O', c_type='PyObject*', insertion_function='{variable}.emplace_back()', get_size_function='{variable}.size()'),
    'std::list': TypeConversion('std::list', 'O', c_type='PyObject*', insertion_function='{variable}.emplace_back()', get_size_function='{variable}.size()'),
    'std::forward_list': TypeConversion('std::forward_list', 'O', c_type='PyObject*', insertion_function='{variable}.push_front()', get_size_function='{variable}.size()'),
    'std::stack': TypeConversion('std::stack', 'O', c_type='PyObject*', insertion_function='{variable}.emplace()', get_size_function='{variable}.size()'),
    'std::queue': TypeConversion('std::queue', 'O', c_type='PyObject*', insertion_function='{variable}.emplace()', get_size_function='{variable}.size()'),
    'std::priority_queue': TypeConversion('std::priority_queue', 'O', c_type='PyObject*', insertion_function='{variable}.emplace()', get_size_function='{variable}.size()'),
}


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
    get_size_function = container_types[container].get_size_function.format(variable=variable)

    block = block.format(**locals())
    block = block.replace('}', '}}').replace('{', '{{')

    if template_type not in basic_types:
        new_layer_type = to_python_list_intermediate_template.format(**locals())
        new_block = _indent_block(new_layer_type + to_python_list_template, next_layer_index)
        block = block.replace('<next_layer>', new_block)
        block = _convert_container_to_python(template_type, next_layer_index, block)
        block = block.replace('<finalize_set>', to_python_list_intermediate_template_2.format(**locals()))
    else:
        to_python_function = basic_types[template_type].to_python_function
        new_block = _indent_block(to_python_list_inner_template.format(**locals()), next_layer_index-1)
        block = block.replace('<next_layer>', new_block)
        block = block.replace('<finalize_set>', '', 1)
        return block

    return block


def _convert_container_from_python(name, arg_type, layer_index, block=from_python_list_template):
    next_layer_index = 1 if not layer_index else layer_index+1

    container, template_type = _parse_template(arg_type)
    variable = '{}_container{}'.format(name, layer_index)
    insertion_function = container_types[container].insertion_function.format(variable=variable)

    block = block.format(**locals())
    block = block.replace('}', '}}').replace('{', '{{')

    if template_type not in basic_types:
        new_layer_type = from_python_list_intermediate_template.format(**locals())
        new_block = _indent_block(new_layer_type + from_python_list_template, next_layer_index)
        block = block.replace('<next_layer>', new_block)
        block = _convert_container_from_python(name, template_type, next_layer_index, block)
    else:
        from_python_function = basic_types[template_type].from_python_function
        new_block = _indent_block(from_python_list_inner_template.format(**locals()), next_layer_index-1)
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
            if arg_type in basic_types:
                format_str += basic_types[arg_type].format_unit
                python_type = basic_types[arg_type].c_type
            else:
                for cpp_type in container_types.keys():
                    if arg_type.startswith(cpp_type):
                        format_str += container_types[cpp_type].format_unit
                        python_type = container_types[cpp_type].c_type
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
        if return_type in basic_types:
            wrapper_body += '        return {}(return_value_raw);'.format(basic_types[return_type].to_python_function)
        elif return_type == 'std::string':
            wrapper_body += '        return {}(return_value_raw.c_str());'.format(container_types[return_type].to_python_function)
        else:
            for cpp_type in container_types.keys():
                if return_type.startswith(cpp_type):
                    break

            block = '        PyObject* return_value_list = PyList_New(return_value_raw.size());'
            block += _convert_container_to_python(return_type, '')
            wrapper_body += block.format()
            wrapper_body += '        return return_value_list;'

    return wrapper_body


def create(filename, block_name, block_signature, block):
    with open(filename, 'w') as sf:
        block_wrapper_body = _make_wrapper(block_name, block_signature)
        sf.write(template.format(**locals(), version=version))
