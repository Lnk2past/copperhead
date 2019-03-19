import copperhead as cpp

print(cpp.__file__)
print(dir(cpp))

# simple output
print('Test 1')
test1 = '''
#include <iostream>
void hello_world()
{
   std::cout << "Hello World!" << std::endl;
}'''
hello_world = cpp.generate('hello_world', 'void()', test1)
hello_world()
print('')


# passing and returning primitives
print('Test 2')
test2 = '''
int fibonacci(int i)
{
   int f = 1;
   while (i > 1)
   {
      f *= (i--);
   }
   return f;
}'''
fibonacci = cpp.generate('fibonacci', 'int(int)', test2)
print(fibonacci(6))
print('')


# passing multiple arguments
print('Test 3')
test3 = '''
int sum(int i, int j)
{
   return i+j;
}'''
sum = cpp.generate('sum', 'int(int, int)', test3)
print(sum(6, 10))
print('')


# testing passing strings
print('Test 4')
test4 = '''
#include <iostream>
void greet(std::string name)
{
   std::cout << "Hello, " << name << std::endl;
}'''
greet = cpp.generate('greet', 'void(std::string)', test4)
greet('bob')
print('')


# testing exceptions
print('Test 5')
test5 = '''
#include <stdexcept>
void bad()
{
   throw std::runtime_error("You broke me!");
}'''
cpp.generate('bad', 'void()', test5)
import bad
try:
   bad.bad()
except bad.error as e:
   print('Got some weird error...', e)
print('')
