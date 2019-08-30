from .cpp_type import base_cpp_type


class UnorderedAssociativeContainer(base_cpp_type):
    def __init__(self, cpp_type, insertion_function, get_size_function):
        super().__init__(cpp_type, 'PyObject*', 'O')
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function


types = {
    # 'std::unordered_map': UnorderedAssociativeContainer('std::unordered_map', ),
    # 'std::unordered_multimap': UnorderedAssociativeContainer('std::unordered_multimap', ),
    # 'std::unordered_set': UnorderedAssociativeContainer('std::unordered_set', ),
    # 'std::unordered_multiset': UnorderedAssociativeContainer('std::unordered_multiset', ),
}
