import sys
import copperhead as cpp

extra_compile_args = '/std:c++14' if sys.version.split('[')[1].startswith('MSC') else '-std=c++14'
config = {
    'extra_compile_args': extra_compile_args
}


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

compute = cpp.generate('compute', 'void(std::string, double, double, double)', mandelbrot_cpp, config=config)
compute('fractal.dat', -2.0, 1.25, 0.005)
