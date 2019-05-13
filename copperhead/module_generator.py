import importlib
import glob
import json
import pathlib
import os
import setuptools.sandbox
import sys

from copperhead.code_generator import create as create_code
from copperhead.setup_generator import create as create_setup
from copperhead.default_config import config as default_config

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
    this_cache_dir = pathlib.Path(cache_dir, block_name).resolve().absolute()
    os.makedirs(this_cache_dir, exist_ok=True)

    config_file = '.copperhead.json'
    if os.path.exists(config_file):
        with open(config_file) as json_config:
            config = {**json.load(json_config), **config}
    config = {**default_config, **config}

    egg = _get_egg(this_cache_dir)
    if not egg or rebuild:
        source = this_cache_dir / (block_name + '_block.cpp')
        create_code(source, block_name, block_signature, block)

        setup = this_cache_dir / (block_name + '_setup.py')
        create_setup(setup, block_name, source._str, config)

        if 'PYTHONPATH' not in os.environ:
            os.environ['PYTHONPATH'] = ''
        os.environ['PYTHONPATH'] += '{}{}'.format(os.pathsep, this_cache_dir)

        setuptools.sandbox.run_setup(str(setup), args=['install', '--install-lib={}'.format(this_cache_dir)])
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
