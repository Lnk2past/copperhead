import os
import re

from .__version__ import __version__ as version
from .templates.basic_wrapper import template


def parse_template(full_type):
    template_type_re = re.compile('<(.*)>')
    return template_type_re.search(full_type).group(1)


to_python_list_template = r'''
        PyObject* return_value_list = PyList_New(return_value_raw.size());
        if (!return_value_list) PyErr_SetString({block_name}Error, "Could not allocate a new Python list!");
        Py_ssize_t pos {{0}};
        for (auto & element : return_value_raw)
        {{
            PyList_SetItem(return_value_list, pos, {conversion}(element));
            ++pos;
        }}
        return return_value_list;
'''

from_python_list_template = r'''
        {arg_type} {name}_container;
        for (Py_ssize_t i {{0}}; i < PyList_Size({name}); i++)
        {{
            PyObject *value = PyList_GetItem({name}, i);
            {name}_container.{insertion_function}( PyLong_AsLong(value) );
        }}
'''


class TypeConversion:
    def __init__(self, cpp_type, format_unit, to_python_conversion_function, c_type=None, insertion_function=None ):
        self.cpp_type = cpp_type
        self.c_type = c_type if c_type else cpp_type
        self.format_unit = format_unit
        self.to_python_conversion_function = to_python_conversion_function
        self.insertion_function = insertion_function


basic_types = {
    'short': TypeConversion('short', 'h', 'PyLong_FromLong'),
    'int': TypeConversion('int', 'i', 'PyLong_FromLong'),
    'long': TypeConversion('long', 'l', 'PyLong_FromLong'),
    'long long': TypeConversion('long long', 'L', 'PyLong_FromLongLong'),
    'unsigned char': TypeConversion('unsigned char', 'b', 'PyLong_FromUnsignedLong'),
    'unsigned short': TypeConversion('unsigned short', 'H', 'PyLong_FromUnsignedLong'),
    'unsigned int': TypeConversion('unsigned int', 'I', 'PyLong_FromUnsignedLong'),
    'unsigned long': TypeConversion('unsigned long', 'k', 'PyLong_FromUnsignedLong'),
    'unsigned long long': TypeConversion('unsigned long long', 'K', 'PyLong_FromLongUnsignedLong'),
    'float': TypeConversion('float', 'f', 'PyFloat_FromDouble'),
    'double': TypeConversion('double', 'd', 'PyFloat_FromDouble'),
    'std::string': TypeConversion('std::string', 's', 'PyUnicode_FromString', c_type='char*'),
}


cpp_types = {
    'std::list': TypeConversion('std::list', 'O', to_python_list_template, c_type='PyObject*', insertion_function='push_back'),
    'std::vector': TypeConversion('std::vector', 'O', to_python_list_template, c_type='PyObject*', insertion_function='push_back'),
    'std::queue': TypeConversion('std::queue', 'O', to_python_list_template, c_type='PyObject*', insertion_function='push'),
    'std::deque': TypeConversion('std::deque', 'O', to_python_list_template, c_type='PyObject*', insertion_function='push_back'),
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
                        conversion_args.append((chr(arg_name), arg_type, cpp_type))
                        break

            wrapper_body += '        {} {};\n'.format(python_type, chr(arg_name))

            args.append(chr(arg_name))
            arg_name += 1

        args_str = ', '.join(['&{}'.format(arg) for arg in args])
        wrapper_body += '        if (!PyArg_ParseTuple(args, "{}", {})) return NULL;\n'.format(format_str, args_str)

        for conversion_arg in conversion_args:
            name, arg_type, cpp_type = conversion_arg
            insertion_function = cpp_types[cpp_type].insertion_function
            wrapper_body += from_python_list_template.format(arg_type=arg_type, name=name, insertion_function=insertion_function)
            args[args.index(name)] = '{name}_container'.format(name=name)

    return_value = ''
    if return_type != 'void':
        return_value = '{} return_value_raw = '.format(return_type)

    wrapper_body += '        {}{}({});\n'.format(return_value, block_name, ','.join(args))

    if return_type == 'void':
        wrapper_body += '        Py_RETURN_NONE;'
    else:
        if return_type in basic_types:
            wrapper_body += '        return {}(return_value_raw);'.format(basic_types[return_type].to_python_conversion_function)
        elif return_type == 'std::string':
            wrapper_body += '        return {}(return_value_raw.c_str());'.format(cpp_types[return_type].to_python_conversion_function)
        else:
            template_type = parse_template(return_type)
            while template_type not in basic_types:
                template_type = parse_template(template_type)
            wrapper_body += to_python_list_template.format(block_name=block_name, conversion=basic_types[template_type].to_python_conversion_function)

    return wrapper_body

def create(filename, block_name, block_signature, block):
    source = os.path.join(filename)
    with open(source, 'w') as sf:
        block_wrapper_body = _make_wrapper(block_name, block_signature)
        sf.write(template.format(block_name=block_name, block=block, block_wrapper_body=block_wrapper_body, version=version))

