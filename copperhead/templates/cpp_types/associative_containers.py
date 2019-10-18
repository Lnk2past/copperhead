from .cpp_type import base_cpp_type


class AssociativeContainer(base_cpp_type):
    def __init__(self, cpp_type, insertion_function, get_size_function):
        super().__init__(cpp_type, 'PyObject*', 'O')
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function

    to_python_list_template = r'''
for (auto &return_value_raw{layer_index} : return_value_raw{previous_layer_index})
{{
    <next_layer>
    <finalize_set>
}}
'''.rstrip('\n')

    to_python_list_intermediate_template = r'''
auto return_value_list{layer_index} = PyDict_New();
'''.rstrip('\n')

    to_python_list_intermediate_template_2 = r'''
auto pykey = {to_python_function}(return_value_raw{layer_index}.first);
PyDict_SetItem(return_value_list{previous_layer_index}, pykey, return_value_list{layer_index});
'''.rstrip('\n')

    to_python_list_inner_template = r'''
auto pykey{layer_index} = {to_python_function_key}(return_value_raw{layer_index}.first.c_str());
auto pyvalue{layer_index} = {to_python_function_value}(return_value_raw{layer_index}.second);
PyDict_SetItem(return_value_list{previous_layer_index}, pykey{layer_index}, pyvalue{layer_index});
'''.rstrip('\n')

    from_python_list_template = r'''
Py_ssize_t ppos{layer_index} {{0}};
PyObject *pkey{layer_index};
PyObject *pvalue{layer_index};
while (PyDict_Next({name}{layer_index}, &ppos{layer_index}, &pkey{layer_index}, &pvalue{layer_index}))
{{
    <next_layer>
}}
'''.rstrip('\n')

    from_python_list_intermediate_template = r'''
auto {name}{next_layer_index} = PyDict_GetItem({name}{layer_index}, i{layer_index});
'''.rstrip('\n')

    from_python_list_inner_template = r'''
{variable}[{from_python_function_key}(pkey{layer_index})] = {from_python_function_value}(pvalue{layer_index});
'''.rstrip('\n')


types = {
    'std::map': AssociativeContainer('std::map', '', '{variable}.size()'),
    # 'std::multimap': AssociativeContainer('std::multimap', '{variable}.emplace()', '{variable}.size()'),
    # 'std::set': AssociativeContainer('std::set', '{variable}.emplace()', '{variable}.size()'),
    # 'std::multiset': AssociativeContainer('std::multiset', '{variable}.emplace()', '{variable}.size()'),
}
