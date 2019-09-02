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
void greet(std::string name)
{
   std::cout << "Hello, " << name << std::endl;
}'''
greet = cpp.generate('greet', 'void(std::string)', src, config=config)
greet('bob')
print('')
