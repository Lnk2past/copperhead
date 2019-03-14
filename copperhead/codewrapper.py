import os
import re

from .__version__ import __version__ as version
from .templates.basic_wrapper import template

type_map = {
    'std::string': 's',
    'char*': 's',
    'unsigned char': 'b',
    'short': 'h',
    'unsigned short': 'H',
    'int': 'i',
    'unsigned int': 'I',
    'long': 'l',
    'unsigned long': 'k',
    'long long': 'L',
    'unsigned long long': 'K',
    'float': 'f',
    'double': 'd',
}

c_subtype_mapping = {
    'std::string': 'char*'
}

def make_wrapper(block_name, block_signature):
    return_type_re = re.compile(r'(.*)\(')
    args_type_list_re = re.compile(r'.*\((.*)\)')

    return_type = return_type_re.search(block_signature).group(1).strip()
    args_type_list = [arg.strip() for arg in args_type_list_re.search(block_signature).group(1).split(',')]

    wrapper_body = ''
    args = []

    if args_type_list and args_type_list[0]:
        format_str = ''
        arg_name = 65
        for arg_type in args_type_list:
            arg_type = c_subtype_mapping.get(arg_type, arg_type)
            wrapper_body += '        {} {};\n'.format(arg_type, chr(arg_name))
            format_str += type_map[arg_type]
            args.append(chr(arg_name))
            arg_name += 1

        args_str = ', '.join(['&{}'.format(arg) for arg in args])
        wrapper_body += '        if (!PyArg_ParseTuple(args, "{}", {})) return NULL;\n'.format(format_str, args_str)

    return_value = ''
    if return_type != 'void':
        return_value = '{} return_value_raw = '.format(return_type)

    wrapper_body += '        {}{}({});\n'.format(return_value, block_name, ','.join(args))

    if return_type == 'void':
        wrapper_body += '        Py_RETURN_NONE;'
    else:
        if return_type in ['short', 'int', 'long']:
            wrapper_body += '        return PyLong_FromLong(return_value_raw);'
        elif return_type == 'long long':
            wrapper_body += '        return PyLong_FromLongLong(return_value_raw);'
        if return_type in ['unsigned char', 'unsigned short', 'unsigned int', 'unsigned long']:
            wrapper_body += '        return PyLong_FromUnsignedLong(return_value_raw);'
        elif return_type == 'unsigned long long':
            wrapper_body += '        return PyLong_FromUnsignedLongLong(return_value_raw);'
        elif return_type in ['float', 'double']:
            wrapper_body += '        return PyFloat_FromDouble(return_value_raw);'
        elif return_type in ['std::string']:
            wrapper_body += '        return PyUnicode_FromString(return_value_raw.c_str());'

    return wrapper_body

def create(filename, block_name, block_signature, block):
    source = os.path.join(filename)
    with open(source, 'w') as sf:
        block_wrapper_body = make_wrapper(block_name, block_signature)
        sf.write(template.format(block_name=block_name, block=block, block_wrapper_body=block_wrapper_body, version=version))

