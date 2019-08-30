from .cpp_type import base_cpp_type


class SequenceContainer(base_cpp_type):
    def __init__(self, cpp_type, insertion_function, get_size_function):
        super().__init__(cpp_type, 'PyObject*', 'O')
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function


types = {
    'std::deque': SequenceContainer('std::deque', '{variable}.emplace_back()', '{variable}.size()'),
    'std::forward_list': SequenceContainer('std::forward_list', '{variable}.push_front()', '{variable}.size()'),
    'std::list': SequenceContainer('std::list', '{variable}.emplace_back()', '{variable}.size()'),
    'std::vector': SequenceContainer('std::vector', '{variable}.emplace_back()', '{variable}.size()'),
}
