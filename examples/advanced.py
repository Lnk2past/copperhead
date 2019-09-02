import sys
import copperhead as cpp


extra_compile_args = "'/std:c++14'" if sys.version.split('[')[1].startswith('MSC') else "'-std=c++14'"
config = {
    'extra_compile_args': extra_compile_args
}


# passing nested std::vector
print('Test 1')
src = r'''
#include <iostream>
#include <numeric>
#include <vector>
std::vector<std::vector<int>> two_dim_vector_test(std::vector<std::vector<int>> v)
{
    for (auto &r : v)
    {
        std::partial_sum(std::begin(r), std::end(r), std::begin(r));
    }
    return v;
}'''
two_dim_vector_test = cpp.generate('two_dim_vector_test', 'std::vector<std::vector<int>>(std::vector<std::vector<int>>)', src, config=config)
print(two_dim_vector_test([[0, 1, 2], [3, 4, 5], [6, 7, 8]]))
print('')


# passing std::vector dested 3 deep
print('Test 2')
src = r'''
#include <iostream>
#include <numeric>
#include <vector>
std::vector<std::vector<std::vector<int>>> three_dim_vector_test(std::vector<std::vector<std::vector<int>>> v)
{
    for (auto &r : v)
    {
        for (auto &c : r)
        {
            std::partial_sum(std::begin(c), std::end(c), std::begin(c));
        }
    }
    return v;
}'''
three_dim_vector_test = cpp.generate('three_dim_vector_test', 'std::vector<std::vector<std::vector<int>>>(std::vector<std::vector<std::vector<int>>>)', src, config=config)
print(three_dim_vector_test([[[1, 2, 3], [1, 2, 3], [1, 2, 3]], [[1, 2, 3], [1, 2, 3], [1, 2, 3]], [[1, 2, 3], [1, 2, 3], [1, 2, 3]]]))
print('')
