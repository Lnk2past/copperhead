import copperhead as cpp

test1 = '''
#include <iostream>
void hello_world()
{
   std::cout << "Hello World!" << std::endl;
}'''

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

test3 = '''
int sum(int i, int j)
{
   return i+j;
}'''

test4 = '''
double average3(double i, double j, double k)
{
   return (i + j + k) / 3.0;
}'''

test5 = '''
#include <iostream>
void greet(std::string name)
{
   std::cout << "Hello, " << name << std::endl;
}'''

test6 = '''
#include <stdexcept>
void bad()
{
   throw std::runtime_error("You broke me!");
}'''

# testing simple output
hello_world = cpp.generate('hello_world', 'void()', test1)
hello_world()

# testing passing and returning ints
fibonacci = cpp.generate('fibonacci', 'int(int)', test2)
print(fibonacci(6))

# testing passing and returning ints
sum = cpp.generate('sum', 'int(int, int)', test3)
print(sum(6, 10))

# testing passing and returning doubles
average3 = cpp.generate('average3', 'double(double, double, double)', test4)
print(average3(1.0, 2.0, 4.5))

# tsting passing strings
greet = cpp.generate('greet', 'void(std::string)', test5)
greet('bob')

# testing exceptions
badfunc = cpp.generate('bad', 'void()', test6)
import bad
try:
   badfunc()
except bad.error as e:
   print('Got some weird error...', e)


