import copperhead as cpp

test = '''#include <iostream>
extern "C"
{
void hello_world()
{
   std::cout << "Hello World!" << std::endl;
}
}'''.strip()


hello_world = cpp.generate('hello_world', test)

hello_world()
