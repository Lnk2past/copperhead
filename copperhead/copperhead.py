import importlib
import glob
import json
import os
import setuptools.sandbox
import sys

import copperhead.codewrapper
import copperhead.setupgenerator
from copperhead.default_config import default_config

cache_dir = '.copperhead_cache'


def generate(block_name, block_signature, block, config={}, rebuild=False):
    """
    Generate a new module for the input block of code and return the function handle.

    Parameters
    ----------
    block_name : str
        name of block. used for the name of the generated function and module
    block_signature : str
        function type
    block : str
        code to be wrapped
    config : dict
        dictionary of configurables
    rebuild : bool
        flag to rebuild the block, default to False

    Returns
    -------
    function
        Newly generated function
    """
    this_cache_dir = os.path.abspath(os.path.join(cache_dir, block_name))
    os.makedirs(this_cache_dir, exist_ok=True)

    config_file = '.copperhead.json'
    if os.path.exists(config_file):
        with open(config_file) as json_config:
            config = {**json.load(json_config), **config}
    config = {**default_config, **config}

    egg = _get_egg(this_cache_dir)
    if not egg or rebuild:
        source = os.path.abspath(os.path.join(this_cache_dir, block_name + '_block.cpp'))
        copperhead.codewrapper.create(source, block_name, block_signature, block)

        setup = os.path.abspath(os.path.join(this_cache_dir, block_name + '_setup.py'))
        copperhead.setupgenerator.create(setup, block_name, source, config)

        if 'PYTHONPATH' not in os.environ:
            os.environ['PYTHONPATH'] = ''
        os.environ['PYTHONPATH'] += ':{}'.format(this_cache_dir)

        setuptools.sandbox.run_setup(setup, args=['install',
            '--install-lib={}'.format(this_cache_dir)
            ])
        egg = _get_egg(this_cache_dir)

    sys.path.append(egg)
    lib = importlib.import_module(block_name)
    return getattr(lib, block_name)


def _get_egg(directory):
    """Blindly find and return the first egg we find"""
    eggs = glob.glob(os.path.join(directory, '*.egg'))
    if eggs:
        return eggs[0]
    return ''

