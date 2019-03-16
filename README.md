# copperhead
[![Build Status](https://travis-ci.org/Lnk2past/copperhead.svg?branch=master)](https://travis-ci.org/Lnk2past/copperhead)

__c__ o __pp__ erhead --> __cpp__ --> __C++__

## Introduction
```copperhead``` is a dynamic code generator that allows C++ code blocks to be written and executed within Python. Ultimately the code is wrapped and built into a module using ```setuptools```. ```copperhead``` is great for prototyping and "what-if" exploration. I would not necessarily recommend using it directly for production code and environments, but it is something that can aid in developing production/release grade modules and libraries.

## Installation
Currently working to get this onto PyPI, but for now you can clone and install via ```setup.py```
```
python setup.py install
```

```copperhead``` will use the compiler that was used to build your Python installation, and so on older systems you may run into isues until I implement a way to pass compiler flags in (to perhaps revert the C++ standard to something older; right now defaults to C++14).

## Motivation
First and foremost I wanted to learn more about the Python C API (something I have only really hit the surface of over the years). I also was watching CppCon videos [(this one in particular)](https://www.youtube.com/watch?v=nXaxk27zwlk) and I was fascinated when he (Chandler Carruth) started writing assmebly inline with his C++. I have never worked with C++ on that low a level, and it blew my mind a little. I thought to myself and wondered "what if I could write my C++ inline with my Python?". So here we are today.

```copperhead``` generates vanilla C++ code without depending on 3rd party C++ libraries. This is done *within Python*, not from a native library or set of headers. This is important, because it means that you can focus on writing the C++ and not on all of the boilerplate that comes with a set of native bindings, build systems, etc. You simply write your C++ and keep going. *That is it*.

When you are done using ```copperhead``` you are left with the raw *C++ and setup.py* files used to generate the extension in the first place. This means that you have something concrete, reusable, tweakable, etc. that is purely standard C++ and standard Python. Say what you will, but this is probably the best part about ```copperhead```.

## How It Works
### Code Generation
```copperhead``` works by automatically wrapping your C++ code in a new Python API enabled function and pairing it with the necessary code to pack it into a module that is compatible with Python. There are three primary steps to this process:
1. Generate the function wrapper
2. Generate the module
3. Generate the setup script

The function wrapper is the most complicated component. ```copperhead``` will examine the return type and parameter types of the function type supplied and will generate all of the variables needed to convert from Python inputs to C++ types, call your function, and convert the return to a Python type.

The module is fairly cookie cutter at the moment and simply includes your C++ function, the wrapper, and all the boilerplate for making a module.

The setup script is just a *setup.py* script that we populate with a few bits of data, nothing special here.

### Installing & Importing C++ Modules
The newly created *setup.py* script is used for generating the module. It will dump the new modules locally in a directory named *.copperhead\_cache*. Your path will be adjusted to include the newly generated egg. If the egg already exists, this process is skipped and you will simply import what is already available. Note that the *function* is returned, not the module.

## Development Environment
I am coding this to work with latest Python and with modern C++ techniques. I have ~~absolutely no~~ little interest in backwards compatibility. While earlier versions and standards may work right now, I do not guarantee any of that moving forward. I will not hinder development for the sake of supporting something older.

I have two primary development environments at the moment and so you can for expect support for at least the following:
- **Python 3.5.3** and GCC 6.3.0 (Raspbian)
- **Python 3.6.7** and GCC 7.3.0 (Ubuntu 18.04.2)

## Basic Usage
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

### STL Support
Basic STL support is provided now, with more planned. You can supply *std::vector*, *std::list*, *std::queue*, *std::deque* as return and parameter types, and can nest them within eachother.

```python
import copperhead as cpp

std_vector_cpp = '''
#include <iostream>
#include <vector>
void vprint(std::vector<int> v)
{
    for (auto i : v)
    {
        std::cout << i << " ";
    }
    std::cout << std::endl;
}'''

vprint = cpp.generate('vprint', 'void(std::vector<int>)', std_vector_cpp)

vprint()
```

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
        for (long xidx {0}; xidx < n; ++xidx)
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

Note that the [example code](examples/fractal.py) in this repository uses ```h = 0.005``` to reduce the runtime during testing.

## License
See [LICENSE.md](LICENSE.md) for the specifics, but it is an MIT license.

## TODO
Lots:
- more readme updates
- dynamically generate wrapping function
   - support more simple types (various char types?)
   - support STL container converions (std::map, std::unordered_map, std::array)
   - support cv-qualifiers, pointers & references
   - improve error handling
- add support to expose more than 1 function per call to generate
- develop uniqueness in cache rather than basing on name
- add configurable options
    - compiler flags
    - link flags
    - additional includes
    - etc.
- provide official benchmarking results between Python and C++
