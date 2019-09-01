from .cpp_type import base_cpp_type


class Collection:
    def __init__(self, cpp_type, insertion_function=None, get_size_function=None):
        super().__init__(cpp_type, 'PyObject*', 'O')
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function


types = {
    # 'std::tuple': Collection('std::tuple', ),
}
