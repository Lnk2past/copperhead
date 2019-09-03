from .cpp_type import base_cpp_type


class Complex(base_cpp_type):
    def __init__(self, cpp_type, c_type, format_unit, to_python_function, from_python_function):
        super().__init__(cpp_type, c_type, format_unit)
        self.to_python_function = to_python_function
        self.from_python_function = from_python_function


types = {
    # 'std::complex': Complex('std::complex', 'Py_complex', 'D', 'PyComplex_FromCComplex', 'PyComplex_AsCComplex')
}
