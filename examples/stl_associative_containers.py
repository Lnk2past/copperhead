import sys
import copperhead as cpp


extra_compile_args = "'/std:c++14'" if sys.version.split('[')[1].startswith('MSC') else "'-std=c++14'"
config = {
    'extra_compile_args': extra_compile_args
}


# passing and returning a std::map
print('Test 1')
src = r'''
#include <iostream>
#include <map>
#include <string>
std::map<std::string, int> map_test(std::map<std::string, int> m)
{
    m["foobar"] = 10;
    return m;
}'''
map_test = cpp.generate('map_test', 'std::map<std::string, int>(std::map<std::string, int>)', src, config=config)
print(map_test({'foo': 1, 'bar': 2}))
print('')
