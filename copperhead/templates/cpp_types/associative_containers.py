from .cpp_type import base_cpp_type


class AssociativeContainer(base_cpp_type):
    def __init__(self, cpp_type, insertion_function, get_size_function):
        super().__init__(cpp_type, 'PyObject*', 'O')
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function


types = {
    # 'std::map': AssociativeContainer('std::map', '{variable}.emplace()', '{variable}.size()'),
    # 'std::multimap': AssociativeContainer('std::multimap', '{variable}.emplace()', '{variable}.size()'),
    # 'std::set': AssociativeContainer('std::set', '{variable}.emplace()', '{variable}.size()'),
    # 'std::multiset': AssociativeContainer('std::multiset', '{variable}.emplace()', '{variable}.size()'),
}
