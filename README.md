# copperhead

```copperhead``` is a dynamic code generator that allows C++ code blocks to be written and executed within Python. Ultimately the code is wrapped and built into a module using ```setuptools```. The path of the newly generated egg is added to the system path and the module is imported and returned.

The primary interface for using ```copperhead``` is through the ```generate``` function. Simply pass in the name fo the function and the block of code you need to build into a module.

### Important!
```copperhead``` is great for prototyping and "what-if" exploration. I would not recommend using ```copperhead``` directly for production code and environments, but it is something that can aid in developing production/release grade modules and libraries. I am always wary of dynamically generated code in production, but to each their own.

### More Important Things!
I am coding this to work with latest Python and with modern C++ techniques. I have no interest in backwards compatibility. While earlier versions and standards may work right now, I do not guarantee any of that moving forward. I will not hinder development for the sake of supporting something older.

- My development environment currently employs Python 3.6.7 and GCC 7.3.0
- My development environment will move soon to Python 3.7.2 and GCC 8.3.2

## Motivation

Why not just write C++ if you are going to write C++ anyway? Just write everything in Python; you did choose the language! Why bother mixing languges? Why not use any of the existing language binding generators? These are all valid questions.

Well, the first and foremost answer is that I wanted to learn more about integrating the languages. Secondly, there isn't anything quite like maintaining your cross-language code in a contained and encapsulated manner. I am not saying that maintaining C++ source code embedded directly in your Python code is the way to go, but I like the idea of being able to ask myself "Hey, I wonder if I can squeeze out some performance by writing this block in C++?" and then being able to just *do it* without thinking much about it.

```copperhead``` generates real C++ code without depending on 3rd party C++ libraries. This is done *within Python*, not from a native library or set of headers. This is important, because it means that you can focus on writing the C++ and not on all of the boilerplate that comes with a set of native bindings, build systems, etc. From a workflow perspective you do not need to change editors (if your workflow requires it), you do not need to run a set of commands to build and install, you do not need to do anything other than writing your code and then calling it. Workflow efficiency is important.

When you are done using ```copperhead``` you are left with the raw *C++ and setup.py* files used to generate the extension in the first place. This means that you have something concrete, reusable, tweakable, etc. that is purely standard C++ and standard Python. Say what you will, but this is probably the best part about ```copperhead```.

So... why not just write C++? The answer is simple. Maybe your project really is better suited for Python, save some particular performance critical areas. By all means, write your program in Python if that is the language that suits it best. I am not here to tell you what languages to use or not use for your projects.

## Examples
### Hello World!
Here is a simple example showing how to create your typical *Hello World!* program:

```python
import copperhead as cpp

hello_world_cpp = '''
#include <iostream>
void hello_world()
{
   std::cout << "Hello World!" << std::endl;
}'''

hello_world = cpp.generate('hello_world', 'void()', hello_world_cpp)

hello_world()
```

Breakdown:
- import ```copperhead```; we import ```as cpp``` for simple use
- The string ```hello_world_cpp``` contains raw C++ source. While not valid as a standalone C++ executable (no *main* function), this is perfectly fine for library code.
- We can then call ```cpp.generate```, passing in the name of the function, its signature, and then the code block itself. This will perform the following:
   - Autogenerate the Python bindings for the code
   - Autogenerate the ```setup.py``` for the extension
   - Build the extensions and install it in a local cache
   - Update your paths to include the newly generated extension
   - Return a handle to the function
- Lastly, we call the function. 

### Mandelbrot
Want to generate the Mandelbrot Set? Awesome! You get to it and write a simple implementation to generate a file with the escape times:
```python
def mandlebrot(c):
    max_iter = 100
    i = 0
    z = 0.0j
    while abs(z) < 2.0 and i < max_iter:
        z = z * z + c
        i += 1
    return max_iter - i

x = -2.0
y = 1.25
h = 0.0005
n = int(2.5 / h)

with open('fractal.dat', 'w') as f:
    for yidx in range(n):
        for xidx in range(n):
            f.write('{} '.format(mandlebrot(complex(x, y))))
            x += h
        f.write('\n')
        y -= h
        x -= 2.5
```

If this is the implementation you want, then fine. On my system it takes ~1 minutes 40 seconds to run. However, I do not want to wait upwards 2 minutes for this to run, and at scale this setup gets *worse*. There are potentially problems with buffering the output and maybe there are some other micro-optimizations we could make, but the improvements are not substantial and they really do not solve our performance problem. *Queue enter ```copperhead```*

Lots of iterating and lots of output. Sounds like something C++ would be pretty good at, right? Let's make an implementation that does something comparable:

```python
import copperhead as cpp

mandelbrot_cpp = r'''
#include <cmath>
#include <complex>
#include <fstream>

inline int mandelbrot(const std::complex<double> &c)
{
    const int max_iter {100};
    int i {0};
    std::complex<double> z {0.0, 0.0};
    while (std::abs(z) < 2.0 && i < max_iter)
    {
        z  = z * z + c;
        ++i;
    }
    return max_iter - i;
}

void compute(std::string filename, double x, double y, double h)
{
    const auto n {std::lround(2.5 / h)};
    std::ofstream f(filename);
    for (long yidx {0}; yidx < n; ++yidx)
    {
        for (long xidx = 0; xidx < n; ++xidx)
        {
            f << mandelbrot(std::complex<double>(x, y)) << " ";
            x  += h;
        }
        f << "\n";
        y -= h;
        x -= 2.5;
    }
}'''

compute = cpp.generate('compute', 'void(std::string, double, double, double)', mandelbrot_cpp)
compute('fractal.dat', -2.0, 1.25, 0.0005)
```

Before diving into evaluating this against our Python, do note that I decided to make this input driven. We can specify the return and parameter types to the function so that we may pass data in. here we specify the output filename and some parameters that dictate the region of the set we are concerned with and the granularity of our iteration.

Running this you will see a good bit of jargon dumped to stdout: this is the creation of the C++ extension (running again, the cache is accessed and you will not see it). On my system this runs in ~9 seconds. 1:40 to 0:09. The improvements here become even greater as the problem space scales. While timing is hardly a valuble benchmark, the savings here are too great and too obvious to ignore.

## TODO
Lots:
- more readme updates
- dynamically generate wrapping function
   - support more simple types
   - support STL container converions (vector, array, list, map, etc.)
   - improve error handling
- develop uniqueness in cache rather than basing on name
- add configurable options
    - compiler flags
    - link flags
    - additional includes
    - etc.
- provide official benchmarking results between Python and C++

