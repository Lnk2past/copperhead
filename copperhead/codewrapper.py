import os
import re
import version

module_template = '''// this code is automatically generated from cooperhead {version}
#include <Python.h>
#include <iostream>
#include <stdexcept>

static PyObject *{block_name}Error;

//**************************************
// this is the start injected code block
{block}
//**************************************

// this method is the primary wrapper for the code block
PyObject* py_{block_name}(PyObject*, PyObject* args)
{{
    try
    {{
{block_wrapper_body}
    }}
    catch (std::runtime_error &e)
    {{
        PyErr_SetString({block_name}Error, e.what());
        return nullptr;
    }}
    catch (...)
    {{
        PyErr_SetString({block_name}Error, "Unknown error");
        return nullptr;
    }}
}}

// create the methods array
static PyMethodDef {block_name}Methods[]
{{
    {{"{block_name}",  py_{block_name}, METH_VARARGS, nullptr}},
    {{nullptr, nullptr, 0, nullptr}}
}};

// create the module
static PyModuleDef {block_name}module
{{
    PyModuleDef_HEAD_INIT,
    "{block_name}",
    nullptr,
    -1,
    {block_name}Methods
}};

// initialize the module
PyMODINIT_FUNC PyInit_{block_name}(void)
{{
    PyObject *m = PyModule_Create(&{block_name}module);
    if (m == nullptr)
    {{
        return nullptr;
    }}
    {block_name}Error = PyErr_NewException("{block_name}.error", NULL, NULL);
    Py_INCREF({block_name}Error);
    PyModule_AddObject(m, "error", {block_name}Error);
    return m;
}}'''

type_map = {
    'std::string': 's',
    'char*': 's',
    'int': 'i',
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
        wrapper_body += '    Py_RETURN_NONE;\n'
    else:
        if return_type in ['short', 'int', 'long']:
            wrapper_body += '        return PyLong_FromLong(return_value_raw);'
        elif return_type == 'long long':
            wrapper_body += '        return PyLong_FromLongLong(return_value_raw);'
        elif return_type in ['float', 'double']:
            wrapper_body += '        return PyFloat_FromDouble(return_value_raw);'

    return wrapper_body

def create(filename, block_name, block_signature, block):
    source = os.path.join(filename)
    with open(source, 'w') as sf:
        block_wrapper_body = make_wrapper(block_name, block_signature)
        sf.write(module_template.format(block_name=block_name, block=block, block_wrapper_body=block_wrapper_body, version=version.version))

