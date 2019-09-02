import sys
import copperhead as cpp


extra_compile_args = "'/std:c++14'" if sys.version.split('[')[1].startswith('MSC') else "'-std=c++14'"
config = {
    'extra_compile_args': extra_compile_args
}


# testing passing strings
print('Test 1')
src = '''
#include <iostream>
std::string greet(std::string name)
{
   std::string str = "Hello " + name;
   return str;
}'''
greet = cpp.generate('greet', 'std::string(std::string)', src, config=config)
print(greet('bob'))
print('')
