from .cpp_type import base_cpp_type


class Primitive(base_cpp_type):
    def __init__(self, cpp_type, format_unit, to_python_function, from_python_function):
        super().__init__(cpp_type, cpp_type, format_unit)
        self.to_python_function = to_python_function
        self.from_python_function = from_python_function


types = {
    'short': Primitive('short', 'h', 'PyLong_FromLong', 'PyLong_AsLong'),
    'int': Primitive('int', 'i', 'PyLong_FromLong', 'PyLong_AsLong'),
    'long': Primitive('long', 'l', 'PyLong_FromLong', 'PyLong_AsLong'),
    'long long': Primitive('long long', 'L', 'PyLong_FromLongLong', 'PyLong_AsLongLong'),
    'unsigned char': Primitive('unsigned char', 'b', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong'),
    'unsigned short': Primitive('unsigned short', 'H', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong'),
    'unsigned int': Primitive('unsigned int', 'I', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong'),
    'unsigned long': Primitive('unsigned long', 'k', 'PyLong_FromUnsignedLong', 'PyLong_AsUnsignedLong'),
    'unsigned long long': Primitive('unsigned long long', 'K', 'PyLong_FromLongUnsignedLong', 'PyLong_AsUnsignedLongLong'),
    'float': Primitive('float', 'f', 'PyFloat_FromDouble', 'PyFloat_AsDouble'),
    'double': Primitive('double', 'd', 'PyFloat_FromDouble', 'PyFloat_AsDouble'),
}

