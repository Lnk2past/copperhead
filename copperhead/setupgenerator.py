import os
import version

setup_template = '''# this code is automatically generated from cooperhead {version}
#

from setuptools import setup, Extension
module1 = Extension('{block_name}',
                    sources = ['{source}'],
                    extra_compile_args = ['-std=c++14', '-O3'],
                    language='c++')

setup (name = '{block_name}',
       ext_modules = [module1])'''


def create(filename, block_name, source):
    with open(filename, 'w') as sf:
        sf.write(setup_template.format(source=source, block_name=block_name, version=version.version))