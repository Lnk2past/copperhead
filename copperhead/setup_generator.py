from copperhead.__version__ import __version__ as version
from copperhead.templates.basic_setup import template


def create(filename, block_name, source, config):
    with open(filename, 'w') as sf:
        sf.write(template.format(source=source, block_name=block_name, version=version, **config))
