class Collection:
    def __init__(self, cpp_type, format_unit, to_python_function=None, from_python_function=None, c_type=None, insertion_function=None, get_size_function=None):
        self.cpp_type = cpp_type
        self.c_type = c_type if c_type else cpp_type
        self.format_unit = format_unit
        self.to_python_function = to_python_function
        self.from_python_function = from_python_function
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function

