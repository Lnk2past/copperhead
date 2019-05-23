template = '''
# this code is automatically generated from cooperhead {version}
#
from setuptools import setup, Extension
module1 = Extension('{block_name}',
                    sources = [{source!r}],
                    include_dirs = [{include_dirs}],
                    define_macros = [{define_macros}],
                    undef_macros = [{undef_macros}],
                    library_dirs = [{library_dirs}],
                    libraries = [{libraries}],
                    runtime_library_dirs = [{runtime_library_dirs}],
                    extra_objects = [{extra_objects}],
                    extra_compile_args = [{extra_compile_args}],
                    extra_link_args = [{extra_link_args}],
                    export_symbols = [{export_symbols}],
                    depends = [{depends}],
                    language = 'c++',
                    optional = {optional}
)
setup (name = '{block_name}',
       ext_modules = [module1])
'''.strip()
