import os

from .__version__ import __version__ as version
from .templates.basic_setup import template

def create(filename, block_name, source, compiler_flags=''):
    compiler_flags = ','.join("'{}'".format(compiler_flag) for compiler_flag in compiler_flags)
    with open(filename, 'w') as sf:
        sf.write(template.format(source=source, block_name=block_name, compiler_flags=compiler_flags, version=version))