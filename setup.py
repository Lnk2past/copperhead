from setuptools import setup
from copperhead import version

setup(
    name='copperhead',
    version=version.version,
    packages=['copperhead'],
    author='Lnk2past',
    description='An Inline C++ Extension Generator for Python',
    license='MIT',
    keywords='cpp cpluscplus c++ extension',
    url='https://github.com/Lnk2past/copperhead'
)