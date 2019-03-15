import copperhead as cpp

test1 = r'''
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

vprint = cpp.generate('vprint', 'void(std::vector<int>)', test1)
vprint([1, 2, 3, 4])

vsum = cpp.generate('vsum', 'int(std::vector<int>, std::list<int>)', test2)
print(vsum([1, 2, 3, 4], [5, 6, 7, 8, 9]))

vcsum = cpp.generate('vcsum', 'std::vector<int>(std::vector<int>)', test3)
print(vcsum([1, 2, 3, 4]))

qs = cpp.generate('qs', 'void(std::deque<double>, std::queue<double>)', test4)
qs([3.14, 1.41, 4.15, 1.59, 5.92], [5.0001])

vprint2d = cpp.generate('vprint2d', 'void(std::vector<std::vector<int>>)', test5)
vprint2d([[0,1,2], [3,4,5], [6,7,8]])

vprint3d = cpp.generate('vprint3d', 'void(std::vector<std::vector<std::vector<int>>>)', test6)
vprint3d([[[1,2,3], [1,2,3], [1,2,3]], [[1,2,3], [1,2,3], [1,2,3]], [[1,2,3], [1,2,3], [1,2,3]]])

