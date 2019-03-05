# copperhead

```copperhead``` is a dynamic code generator that allows C++ code blocks to be written and executed within Python. Ultimately the code is wrapped and built into a module using ```setuptools```. The path of the newly generated egg is added to the system path and the module is imported and returned.

The primary interface for using ```copperhead``` is through the ```generate``` function. Simply pass in the name fo the function and the block of code you need to build into a module.

Currently ```run.py``` includes a sample usage.

## TODO
Lots:
- dynamically generate wrapping function
- develop uniqueness in cache rather than basing on name
- add configurable options
    - compiler flags
    - link flags
    - additional includes
    - etc.
