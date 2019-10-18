import sys
import copperhead as cpp


extra_compile_args = "'/std:c++14'" if sys.version.split('[')[1].startswith('MSC') else "'-std=c++14'"
config = {
    'extra_compile_args': extra_compile_args
}


# passing and returning a std::vector
print('Test 1')
src = r'''
#include <iostream>
#include <numeric>
#include <vector>
std::vector<int> vector_test(std::vector<int> v)
{
    std::partial_sum(std::begin(v), std::end(v), std::begin(v));
    for (auto i : v)
    {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    return v;
}'''
vector_test = cpp.generate('vector_test', 'std::vector<int>(std::vector<int>)', src, config=config)
vector_test([1, 2, 3, 4])
print('')


# passing and returning a std::deque
print('Test 2')
src = r'''
#include <deque>
#include <iostream>
#include <numeric>
std::deque<int> deque_test(std::deque<int> v)
{
    std::partial_sum(std::begin(v), std::end(v), std::begin(v));
    for (auto i : v)
    {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    return v;
}'''
deque_test = cpp.generate('deque_test', 'std::deque<int>(std::deque<int>)', src, config=config)
deque_test([1, 2, 3, 4])
print('')


# passing and returning a std::forward_list
print('Test 3')
src = r'''
#include <forward_list>
#include <iostream>
#include <numeric>
std::forward_list<int> forward_list_test(std::forward_list<int> v)
{
    std::partial_sum(std::begin(v), std::end(v), std::begin(v));
    for (auto i : v)
    {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    return v;
}'''
forward_list_test = cpp.generate('forward_list_test', 'std::forward_list<int>(std::forward_list<int>)', src, config=config)
forward_list_test([1, 2, 3, 4])
print('')


# passing and returning a std::list
print('Test 4')
src = r'''
#include <iostream>
#include <list>
#include <numeric>
std::list<int> list_test(std::list<int> v)
{
    std::partial_sum(std::begin(v), std::end(v), std::begin(v));
    for (auto i : v)
    {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    return v;
}'''
list_test = cpp.generate('list_test', 'std::list<int>(std::list<int>)', src, config=config)
list_test([1, 2, 3, 4])
print('')
