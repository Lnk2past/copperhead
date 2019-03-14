import importlib
import glob
import os
import setuptools.sandbox
import sys

import copperhead.codewrapper
import copperhead.setupgenerator


cache_dir = '.copperhead_cache'


def generate(block_name, block_signature, block, rebuild=False):
    this_cache_dir = os.path.abspath(os.path.join(cache_dir, block_name))
    os.makedirs(this_cache_dir, exist_ok=True)

    egg = _get_egg(this_cache_dir)
    if not egg or rebuild:
        source = os.path.abspath(os.path.join(this_cache_dir, block_name + '_block.cpp'))
        copperhead.codewrapper.create(source, block_name, block_signature, block)

        setup = os.path.abspath(os.path.join(this_cache_dir, block_name + '_setup.py'))
        copperhead.setupgenerator.create(setup, block_name, source)

        if 'PYTHONPATH' not in os.environ:
            os.environ['PYTHONPATH'] = ''
        os.environ['PYTHONPATH'] += ':{}'.format(this_cache_dir)

        setuptools.sandbox.run_setup(setup, args=['install',
            '--install-lib='+this_cache_dir
            ])
        egg = _get_egg(this_cache_dir)

    sys.path.append(egg)
    lib = importlib.import_module(block_name)

    return getattr(lib, block_name)


def _get_egg(directory):
    eggs = glob.glob(os.path.join(directory, '*.egg'))
    if eggs:
        return eggs[0]
    return ''

