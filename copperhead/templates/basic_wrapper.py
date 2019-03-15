template = '''
// this code is automatically generated from cooperhead {version}
#include <Python.h>
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
    if (PyErr_Occurred())
    {{
        PyErr_Print();
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
}}
'''.strip()
