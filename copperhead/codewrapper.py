import os
import re
import version

module_template = '''// this code is automatically generated from cooperhead {version}
#include <Python.h>

//**************************************
// this is the start injected code block
{block}
//**************************************

// this method is the primary wrapper for the code block
PyObject* py_{block_name}(PyObject*, PyObject*)
{{
    {block_name}();
    Py_RETURN_NONE;
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
    return PyModule_Create(&{block_name}module);
}}'''


def create(filename, block_name, block):
    source = os.path.join(filename)
    with open(source, 'w') as sf:
        sf.write(module_template.format(block_name=block_name, block=block, version=version.version))

