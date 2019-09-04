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
PyObject* return_value_list{layer_index} = PyDict_New();
'''.rstrip('\n')

    to_python_list_intermediate_template_2 = r'''
PyObject *pykey = {to_python_function}(return_value_raw{layer_index}.first);
PyDict_SetItem(return_value_list{previous_layer_index}, pykey, return_value_list{layer_index});
'''.rstrip('\n')

    to_python_list_inner_template = r'''
PyObject *pykey = {to_python_function}(return_value_raw{layer_index}.first);
PyObject *pyvalue = {to_python_function}(return_value_raw{layer_index}.second);
PyDict_SetItem(return_value_list{previous_layer_index}, pos{layer_index}, pyvalue);
'''.rstrip('\n')

    from_python_list_template = r'''
Py_ssize_t ppos {{0}};
PyObject **pkey{layer_index};
PyObject **pvalue{layer_index};
while (PyDict_Next({name}{layer_index}, &ppos, &pkey, &pvalue))
{{
    auto &{name}_container{next_layer_index} = *({insertion_function}.first);
<next_layer>
}}
'''.rstrip('\n')

    from_python_list_intermediate_template = r'''
PyObject* {name}{next_layer_index} = PyDict_GetItem({name}{layer_index}, i{layer_index});
'''

    from_python_list_inner_template = r'''
PyObject *pyvalue = PyList_GetItem({name}{layer_index}, i{layer_index});
{name}_container{next_layer_index} = {from_python_function}(pyvalue);
'''.rstrip('\n')


types = {
    'std::map': AssociativeContainer('std::map', '{variable}.emplace({key}, {value})', '{variable}.size()'),
    # 'std::multimap': AssociativeContainer('std::multimap', '{variable}.emplace()', '{variable}.size()'),
    # 'std::set': AssociativeContainer('std::set', '{variable}.emplace()', '{variable}.size()'),
    # 'std::multiset': AssociativeContainer('std::multiset', '{variable}.emplace()', '{variable}.size()'),
}
