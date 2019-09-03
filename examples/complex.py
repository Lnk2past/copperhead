import sys
import copperhead as cpp


extra_compile_args = "'/std:c++14'" if sys.version.split('[')[1].startswith('MSC') else "'-std=c++14'"
config = {
    'extra_compile_args': extra_compile_args
}


# testing passing complex numbers
print('Test 1')
src = '''
#include <complex>
void test(std::complex<double> z)
{
   std::cout << z << std::endl;
}'''
test = cpp.generate('test', 'void(std::complex<double>)', src, config=config)
test(complex(1, 1))
print('')
