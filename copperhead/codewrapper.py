import os
import re

from .__version__ import __version__ as version
from .templates.basic_wrapper import template


def parse_template(full_type):
    template_type_re = re.compile('(.*?)<(.*)>')
    return (template_type_re.search(full_type).group(1), template_type_re.search(full_type).group(2))


to_python_list_template = r'''
        PyObject* return_value_list = PyList_New(return_value_raw.size());
        if (!return_value_list)
        {{
            PyErr_SetString({block_name}Error, "Could not allocate a new Python list!");
            return nullptr;
        }}
        Py_ssize_t pos {{0}};
        for (auto & element : return_value_raw)
        {{
            PyList_SET_ITEM(return_value_list, pos, {conversion}(element));
            ++pos;
        }}
        return return_value_list;
'''


from_python_list_template = r'''
        for (Py_ssize_t i{idx} {{0}}; i{idx} < PyList_Size({name}{idx}); i{idx}++)
        {{
            {name}_container{idx}.{insertion_function}();
            auto &{name}_container{nidx} = {name}_container{idx}.back();
            nest
        }}
'''


from_python_list_inner_template = r'''
            PyObject *pyvalue = PyList_GetItem({name}{idx}, i{idx});
            {name}_container{nidx} = {from_python_function}(pyvalue);
'''


def convert_container_from_python(name, arg_type, cpp_type, idx, block=from_python_list_template):
    container, template_type = parse_template(arg_type)
    insertion_function = cpp_types[container].insertion_function

    pidx = '' if (idx==1 or idx == '') else idx-1
    nidx = 1 if idx == '' else idx+1

    block = block.format(arg_type=arg_type, name=name, idx=idx, nidx=nidx, insertion_function=insertion_function)
    block = block.replace('}', '}}').replace('{', '{{')

    preblock = '        {arg_type} {name}_container{pidx};\n'.format(arg_type=arg_type, name=name, pidx=pidx) if not idx else ''

    if template_type not in basic_types:
        blockbody = 'PyObject* {name}{nidx} = PyList_GetItem({name}{idx}, i{idx});\n'.format(name=name, idx=idx, pidx=pidx, nidx=nidx)
        idx = nidx

        block = preblock + block.replace('nest', blockbody + from_python_list_template)
        block = convert_container_from_python(name, template_type, container, nidx, block)
    else:
        from_python_function = basic_types[template_type].from_python_function
        block = preblock + block.replace('nest', from_python_list_inner_template.format(name=name, idx=idx, nidx=nidx, pidx=pidx, from_python_function=from_python_function))
        return block

    print('=========\n{}\n========='.format(block))
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
                        conversion_args.append((chr(arg_name), arg_type, cpp_type))
                        break

            wrapper_body += '        {} {};\n'.format(python_type, chr(arg_name))

            args.append(chr(arg_name))
            arg_name += 1

        args_str = ', '.join(['&{}'.format(arg) for arg in args])
        wrapper_body += '        if (!PyArg_ParseTuple(args, "{}", {})) return NULL;\n'.format(format_str, args_str)

        for conversion_arg in conversion_args:
            name, arg_type, cpp_type = conversion_arg

            block = convert_container_from_python(name, arg_type, cpp_type, '')
            wrapper_body += block.format()

            print(block)

            args[args.index(name)] = '{name}_container'.format(name=name)

    return_value = ''
    if return_type != 'void':
        return_value = '{} return_value_raw = '.format(return_type)

    wrapper_body += '        {}{}({});\n'.format(return_value, block_name, ','.join(args))

    if return_type == 'void':
        wrapper_body += '        Py_RETURN_NONE;'
    else:
        if return_type in basic_types:
            wrapper_body += '        return {}(return_value_raw);'.format(basic_types[return_type].to_python_function)
        elif return_type == 'std::string':
            wrapper_body += '        return {}(return_value_raw.c_str());'.format(cpp_types[return_type].to_python_function)
        else:
            # what about nested containers?!
            container, template_type = parse_template(return_type)
            while template_type not in basic_types:
                container, template_type = parse_template(template_type)
            to_python_function = basic_types[template_type].to_python_function

            wrapper_body += to_python_list_template.format(block_name=block_name, conversion=to_python_function)

    return wrapper_body

def create(filename, block_name, block_signature, block):
    source = os.path.join(filename)
    with open(source, 'w') as sf:
        block_wrapper_body = _make_wrapper(block_name, block_signature)
        sf.write(template.format(block_name=block_name, block=block, block_wrapper_body=block_wrapper_body, version=version))

