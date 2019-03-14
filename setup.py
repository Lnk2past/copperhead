import os
from setuptools import setup, find_packages

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'copperhead', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    packages=find_packages(),
    author=about['__author__'],
    description=about['__description__'],
    license=about['__license__'],
    url=about['__url__']
)