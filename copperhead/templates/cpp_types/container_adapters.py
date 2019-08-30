from .cpp_type import base_cpp_type


class ContainerAdapter(base_cpp_type):
    def __init__(self, cpp_type, insertion_function, get_size_function):
        super().__init__(cpp_type, 'PyObject*', 'O')
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function


types = {
    'std::stack': ContainerAdapter('std::stack', '{variable}.emplace()', '{variable}.size()'),
    'std::queue': ContainerAdapter('std::queue', '{variable}.emplace()', '{variable}.size()'),
    'std::priority_queue': ContainerAdapter('std::priority_queue', '{variable}.emplace()', '{variable}.size()'),
}
