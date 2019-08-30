import sys
import copperhead as cpp

extra_compile_args = "'/std:c++14'" if sys.version.split('[')[1].startswith('MSC') else "'-std=c++14'"
config = {
    'extra_compile_args': extra_compile_args
}


# passing std::vector
print('Test 1')
test1 = r'''
#include <iostream>
#include <vector>
void vprint(const std::vector<int> &v)
{
    for (auto i : v)
    {
        std::cout << i << " ";
    }
    std::cout << std::endl;
}'''
vprint = cpp.generate('vprint', 'void(std::vector<int>)', test1, config=config)
vprint([1, 2, 3, 4])
print('')


# passing multiple containers
print('Test 2')
test2 = r'''
#include <list>
#include <vector>
int vsum(std::vector<int> v1, std::list<int> v2)
{
    int sum = 0;
    for (auto i : v1)
    {
        sum += i;
    }
    for (auto i : v2)
    {
        sum += i;
    }
    return sum;
}'''
vsum = cpp.generate('vsum', 'int(std::vector<int>, std::list<int>)', test2, config=config)
print(vsum([1, 2, 3, 4], [5, 6, 7, 8, 9]))
print('')


# returning a std::vector
print('Test 3')
test3 = r'''
#include <vector>
std::vector<int> vcsum(std::vector<int> v)
{
    for (std::size_t i = 1; i < v.size(); ++i)
    {
        v[i] += v[i-1];
    }
    return v;
}'''
vcsum = cpp.generate('vcsum', 'std::vector<int>(std::vector<int>)', test3, config=config)
print(vcsum([1, 2, 3, 4]))
print('')


# passing std::deque and std::queue
print('Test 4')
test4 = r'''
#include <deque>
#include <iostream>
#include <queue>
void qs(std::deque<double> deq, std::queue<double> c1)
{
    std::cout << c1.size() << '\n';

    std::queue<double> c2(c1);
    std::cout << c2.size() << '\n';

    std::queue<double> c3(deq);
    std::cout << c3.size() << '\n';
}'''
qs = cpp.generate('qs', 'void(std::deque<double>, std::queue<double>)', test4, config=config)
qs([3.14, 1.41, 4.15, 1.59, 5.92], [5.0001])
print('')


# passing nested std::vector
print('Test 5')
test5 = r'''
#include <iostream>
#include <vector>
void vprint2d(std::vector<std::vector<int>> v)
{
    for (auto r : v)
    {
        for (auto i : r)
        {
            std::cout << i << " ";
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;
}'''
vprint2d = cpp.generate('vprint2d', 'void(std::vector<std::vector<int>>)', test5, config=config)
vprint2d([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
print('')

# passing std::vector dested 3 deep
print('Test 6')
test6 = r'''
#include <iostream>
#include <vector>
void vprint3d(std::vector<std::vector<std::vector<int>>> v)
{
    for (auto r : v)
    {
        for (auto c : r)
        {
            for (auto i : c)
            {
                std::cout << i << " ";
            }
            std::cout << std::endl;
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;
}'''
vprint3d = cpp.generate('vprint3d', 'void(std::vector<std::vector<std::vector<int>>>)', test6, config=config)
vprint3d([[[1, 2, 3], [1, 2, 3], [1, 2, 3]], [[1, 2, 3], [1, 2, 3], [1, 2, 3]], [[1, 2, 3], [1, 2, 3], [1, 2, 3]]])
print('')


# returning nested std::vector
print('Test 7')
test7 = r'''
#include <vector>
std::vector<std::vector<int>> init2d()
{
    std::vector<std::vector<int>> v2d;
    for (auto i = 0; i < 3; ++i)
    {
        v2d.push_back({1, 2, 3});
    }
    return v2d;
}'''
init2d = cpp.generate('init2d', 'std::vector<std::vector<int>>()', test7, config=config)
print(init2d())
print('')


# returning std::list nested inside std::vector
print('Test 8')
test8 = r'''
#include <list>
#include <vector>
std::vector<std::list<double>> init2dvlist()
{
    std::vector<std::list<double>> v2dvl;
    for (auto i = 0; i < 3; ++i)
    {
        v2dvl.push_back({1.3, 2.41, 3.141592});
    }
    return v2dvl;
}'''
init2dvlist = cpp.generate('init2dvlist', 'std::vector<std::list<double>>()', test8, config=config)
print(init2dvlist())
print('')
