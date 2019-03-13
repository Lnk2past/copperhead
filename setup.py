from setuptools import setup, find_packages
from copperhead import version

setup(
    name='copperhead',
    version=version.version,
    packages=find_packages(),
    author='Lnk2past',
    description='An Inline C++ Extension Generator for Python',
    license='MIT',
    keywords='cpp cpluscplus c++ extension',
    url='https://github.com/Lnk2past/copperhead'
)