import os
import re

from .__version__ import __version__ as version
from .templates.basic_wrapper import template


def parse_template(full_type):
    template_type_re = re.compile('(.*?)<(.*)>')
    return (template_type_re.search(full_type).group(1), template_type_re.search(full_type).group(2))


to_python_list_template = r'''
        Py_ssize_t pos{layer_index} {{0}};
        for (auto & return_value_raw{layer_index} : return_value_raw{previous_layer_index})
        {{
            <next_layer>
            <finalize_set>
            ++pos{layer_index};
        }}
'''


to_python_list_intermediate_template = r'''
        PyObject* return_value_list{next_layer_index} = PyList_New(return_value_raw{layer_index}.size());
'''

to_python_list_intermediate_template_2 = r'''
        PyList_SET_ITEM(return_value_list{layer_index}, pos{layer_index}, return_value_list{next_layer_index});
'''

to_python_list_inner_template = r'''
            PyObject *pyvalue = {to_python_function}(return_value_raw{layer_index});
            PyList_SET_ITEM(return_value_list{layer_index}, pos{layer_index}, pyvalue);
'''


def convert_container_to_python(arg_type, layer_index, block=to_python_list_template):
    previous_layer_index = '' if (layer_index in ['', 1]) else layer_index-1
    next_layer_index = 1 if not layer_index else layer_index+1

    container, template_type = parse_template(arg_type)
    insertion_function = cpp_types[container].insertion_function

    block = block.format(previous_layer_index=previous_layer_index, layer_index=layer_index, next_layer_index=next_layer_index, insertion_function=insertion_function)
    block = block.replace('}', '}}').replace('{', '{{')

    if template_type not in basic_types:
        new_layer_type = to_python_list_intermediate_template.format(layer_index=layer_index, next_layer_index=next_layer_index)
        block = block.replace('<next_layer>', new_layer_type + to_python_list_template)
        block = convert_container_to_python(template_type, next_layer_index, block)
        block = block.replace('<finalize_set>', to_python_list_intermediate_template_2.format(layer_index=layer_index, next_layer_index=next_layer_index))
    else:
        to_python_function = basic_types[template_type].to_python_function
        block = block.replace('<next_layer>', to_python_list_inner_template.format(layer_index=layer_index, next_layer_index=next_layer_index, to_python_function=to_python_function))
        block = block.replace('<finalize_set>', '', 1)
        return block

    return block


from_python_list_template = r'''
        // iterate across the list, current layer={layer_index} (empty means 1st)
        for (Py_ssize_t i{layer_index} {{0}}; i{layer_index} < PyList_Size({name}{layer_index}); i{layer_index}++)
        {{
            {name}_container{layer_index}.{insertion_function}();
            auto &{name}_container{next_layer_index} = {name}_container{layer_index}.back();
            <next_layer>
        }}
'''


from_python_list_intermediate_template = r'''
        PyObject* {name}{next_layer_index} = PyList_GetItem({name}{layer_index}, i{layer_index});
'''


from_python_list_inner_template = r'''
            PyObject *pyvalue = PyList_GetItem({name}{layer_index}, i{layer_index});
            {name}_container{next_layer_index} = {from_python_function}(pyvalue);
'''


def convert_container_from_python(name, arg_type, layer_index, block=from_python_list_template):
    next_layer_index = 1 if not layer_index else layer_index+1

    container, template_type = parse_template(arg_type)
    insertion_function = cpp_types[container].insertion_function

    block = block.format(name=name, layer_index=layer_index, next_layer_index=next_layer_index, insertion_function=insertion_function)
    block = block.replace('}', '}}').replace('{', '{{')

    if template_type not in basic_types:
        new_layer_type = from_python_list_intermediate_template.format(name=name, layer_index=layer_index, next_layer_index=next_layer_index)
        block = block.replace('<next_layer>', new_layer_type + from_python_list_template)
        block = convert_container_from_python(name, template_type, next_layer_index, block)
    else:
        from_python_function = basic_types[template_type].from_python_function
        block = block.replace('<next_layer>', from_python_list_inner_template.format(name=name, layer_index=layer_index, next_layer_index=next_layer_index, from_python_function=from_python_function))
        return block

    return block


class TypeConversion:
    def __init__(self, cpp_type, format_unit, to_python_function=None, from_python_function=None, c_type=None, insertion_function=None, reserve=None ):
        self.cpp_type = cpp_type
        self.c_type = c_type if c_type else cpp_type
        self.format_unit = format_unit
        self.to_python_function = to_python_function
        self.from_python_function = from_python_function
        self.insertion_function = insertion_function
        self.reserve = reserve


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


cpp_types = {
    'std::list': TypeConversion('std::list', 'O', c_type='PyObject*', insertion_function='emplace_back'),
    'std::vector': TypeConversion('std::vector', 'O', c_type='PyObject*', insertion_function='emplace_back', reserve='reserve'),
    'std::queue': TypeConversion('std::queue', 'O', c_type='PyObject*', insertion_function='emplace'),
    'std::deque': TypeConversion('std::deque', 'O', c_type='PyObject*', insertion_function='emplace_back'),
}


def _make_wrapper(block_name, block_signature):
    return_type_re = re.compile(r'(.*)\(')
    args_type_list_re = re.compile(r'.*\((.*)\)')

    return_type = return_type_re.search(block_signature).group(1).strip()
    args_type_list = [arg.strip() for arg in args_type_list_re.search(block_signature).group(1).split(',')]

    wrapper_body = ''
    args = []

    if args_type_list and args_type_list[0]:
        format_str = ''
        arg_name = 65
        conversion_args = []
        for arg_type in args_type_list:
            if arg_type in basic_types:
                format_str += basic_types[arg_type].format_unit
                python_type = basic_types[arg_type].c_type
            else:
                for cpp_type in cpp_types.keys():
                    if arg_type.startswith(cpp_type):
                        format_str += cpp_types[cpp_type].format_unit
                        python_type = cpp_types[cpp_type].c_type
                        conversion_args.append((chr(arg_name), arg_type))
                        break

            wrapper_body += '        {} {};\n'.format(python_type, chr(arg_name))

            args.append(chr(arg_name))
            arg_name += 1

        args_str = ', '.join(['&{}'.format(arg) for arg in args])
        wrapper_body += '        if (!PyArg_ParseTuple(args, "{}", {})) return NULL;\n'.format(format_str, args_str)

        for conversion_arg in conversion_args:
            name, arg_type = conversion_arg

            block = '        {arg_type} {name}_container;\n'.format(arg_type=arg_type, name=name)
            block += convert_container_from_python(name, arg_type, '')
            wrapper_body += block.format()

            args[args.index(name)] = '{name}_container'.format(name=name)

    return_value = ''
    if return_type != 'void':
        return_value = 'auto return_value_raw = '

    wrapper_body += '        {}{}({});\n'.format(return_value, block_name, ','.join(args))

    if return_type == 'void':
        wrapper_body += '        Py_RETURN_NONE;'
    else:
        if return_type in basic_types:
            wrapper_body += '        return {}(return_value_raw);'.format(basic_types[return_type].to_python_function)
        elif return_type == 'std::string':
            wrapper_body += '        return {}(return_value_raw.c_str());'.format(cpp_types[return_type].to_python_function)
        else:
            for cpp_type in cpp_types.keys():
                if return_type.startswith(cpp_type):
                    break

            block = '        PyObject* return_value_list = PyList_New(return_value_raw.size());'
            block += convert_container_to_python(return_type, '')
            wrapper_body += block.format()
            wrapper_body += '        return return_value_list;'

    return wrapper_body

def create(filename, block_name, block_signature, block):
    source = os.path.join(filename)
    with open(source, 'w') as sf:
        block_wrapper_body = _make_wrapper(block_name, block_signature)
        sf.write(template.format(block_name=block_name, block=block, block_wrapper_body=block_wrapper_body, version=version))

