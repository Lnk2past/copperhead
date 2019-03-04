import distutils
from distutils.core import run_setup
import importlib
import os
import sys

cache_dir = '.copperhead_cache'

setup_template = '''from distutils.core import setup, Extension
module1 = Extension('{name}',
                    sources = ['{source}'],
                    extra_compile_args = ['-std=c++14', '-O3'],
                    language='c++')

setup (name = '{name}',
       ext_modules = [module1])'''


module_template = '''PyObject* py_{name}(PyObject*, PyObject*)
{{
    {name}();
    Py_RETURN_NONE;
}}

static PyMethodDef {name}Methods[]
{{
    {{"{name}",  py_{name}, METH_VARARGS, nullptr}},
    {{nullptr, nullptr, 0, nullptr}}
}};

static PyModuleDef {name}module
{{
    PyModuleDef_HEAD_INIT,
    "{name}",
    nullptr,
    -1,
    {name}Methods
}};

PyMODINIT_FUNC PyInit_{name}(void)
{{
    return PyModule_Create(&{name}module);
}}'''


def generate(n, block, rebuild=False):
    this_cache_dir = os.path.join(cache_dir, n)
    os.makedirs(this_cache_dir, exist_ok=True)

    # .copperhead_cache/hello_world/hello_world-0.0.0.egg-info
    egg = os.path.join(this_cache_dir, '{}-0.0.0.egg-info'.format(n))
    if not os.path.exists(egg) or rebuild:
        source = os.path.join(this_cache_dir, n+'.cpp')
        with open(source, 'w') as sf:
            sf.write('#include <Python.h>\n')
            sf.write(block)
            sf.write(module_template.format(name=n))

        setup = os.path.join(this_cache_dir, n+'_setup.py')
        with open(setup, 'w') as sf:
            sf.write(setup_template.format(source=source, name=n))

        run_setup(setup, script_args=['install', '--install-purelib='+this_cache_dir, '--install-platlib='+this_cache_dir])

    sys.path.append(this_cache_dir)
    lib = importlib.import_module(n)

    return getattr(lib, n)
