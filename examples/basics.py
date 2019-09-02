import sys
import copperhead as cpp


extra_compile_args = "'/std:c++14'" if sys.version.split('[')[1].startswith('MSC') else "'-std=c++14'"
config = {
    'extra_compile_args': extra_compile_args
}


# simple output
print('Test 1')
src = '''
#include <iostream>
void hello_world()
{
   std::cout << "Hello World!" << std::endl;
}'''
hello_world = cpp.generate('hello_world', 'void()', src, config=config)
hello_world()
print('')


# passing and returning primitives
print('Test 2')
src = '''
int fibonacci(int i)
{
   int f = 1;
   while (i > 1)
   {
      f *= (i--);
   }
   return f;
}'''
fibonacci = cpp.generate('fibonacci', 'int(int)', src, config=config)
print(fibonacci(6))
print('')


# testing exceptions
print('Test 3')
src = '''
#include <stdexcept>
void bad()
{
   throw std::runtime_error("You broke me!");
}'''
cpp.generate('bad', 'void()', src, config=config)
import bad  # noqa: E402
try:
    bad.bad()
except bad.error as e:
    print('Got some weird error...', e)
print('')
