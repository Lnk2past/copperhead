import sys
import copperhead as cpp


extra_compile_args = "'/std:c++14'" if sys.version.split('[')[1].startswith('MSC') else "'-std=c++14'"
config = {
    'extra_compile_args': extra_compile_args
}


# passing and returning a std::stack
print('Test 1')
src = r'''
#include <iostream>
#include <numeric>
#include <stack>
std::stack<int> stack_test(std::stack<int> v)
{
    v.pop();
    v.pop();
    v.push(42);
    return v;
}'''
stack_test = cpp.generate('stack_test', 'std::stack<int>(std::stack<int>)', src, config=config)
print(stack_test([1, 2, 3, 4]))
print('')


# passing and returning a std::queue
print('Test 2')
src = r'''
#include <iostream>
#include <numeric>
#include <queue>
std::queue<int> queue_test(std::queue<int> v)
{
    v.pop();
    v.pop();
    v.push(42);
    return v;
}'''
queue_test = cpp.generate('queue_test', 'std::queue<int>(std::queue<int>)', src, config=config)
print(queue_test([1, 2, 3, 4]))
print('')


# # passing and returning a std::priority_queue
# print('Test 3')
# src = r'''
# #include <iostream>
# #include <numeric>
# #include <queue>
# std::priority_queue<int> priority_queue_test(std::priority_queue<int> v)
# {
#     v.pop();
#     v.pop();
#     v.push(42);
#     return v;
# }'''
# priority_queue_test = cpp.generate('priority_queue_test', 'std::priority_queue<int>(std::priority_queue<int>)', src, config=config)
# print(priority_queue_test([1, 2, 3, 4]))
# print('')
