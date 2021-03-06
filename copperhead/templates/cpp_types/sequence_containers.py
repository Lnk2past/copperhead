from .cpp_type import base_cpp_type


class SequenceContainer(base_cpp_type):
    def __init__(self, cpp_type, insertion_function, get_size_function):
        super().__init__(cpp_type, 'PyObject*', 'O')
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function

    to_python_list_template = r'''
Py_ssize_t pos{layer_index} {{0}};
for (auto & return_value_raw{layer_index} : return_value_raw{previous_layer_index})
{{
    <next_layer>
    <finalize_set>
    ++pos{layer_index};
}}
'''.strip('\n')

    to_python_list_intermediate_template = r'''
PyObject* return_value_list{layer_index} = PyList_New({get_size_function});
'''.strip('\n')

    to_python_list_intermediate_template_2 = r'''
PyList_SET_ITEM(return_value_list{previous_layer_index}, pos{layer_index}, return_value_list{layer_index});
'''.strip('\n')

    to_python_list_inner_template = r'''
auto pyvalue = {to_python_function}(return_value_raw{layer_index});
PyList_SET_ITEM(return_value_list{previous_layer_index}, pos{layer_index}, pyvalue);
'''.strip('\n')

    from_python_list_template = r'''
for (Py_ssize_t i{layer_index} {{0}}; i{layer_index} < PyList_Size({name}{layer_index}); i{layer_index}++)
{{
    auto &{name}_container{next_layer_index} = *{insertion_function};
    <next_layer>
}}
'''.strip('\n')

    from_python_list_intermediate_template = r'''
auto {name}{next_layer_index} = PyList_GetItem({name}{layer_index}, i{layer_index});
'''

    from_python_list_inner_template = r'''
auto pyvalue = PyList_GetItem({name}{layer_index}, i{layer_index});
{name}_container{next_layer_index} = {from_python_function}(pyvalue);
'''.strip('\n')


types = {
    'std::vector': SequenceContainer('std::vector', '{variable}.emplace(std::end({variable}))', '{variable}.size()'),
    'std::deque': SequenceContainer('std::deque', '{variable}.emplace(std::end({variable}))', '{variable}.size()'),
    'std::forward_list': SequenceContainer('std::forward_list', '{variable}.emplace_after({variable}.before_begin())', 'std::distance(std::begin({variable}), std::end({variable}))'),
    'std::list': SequenceContainer('std::list', '{variable}.emplace(std::end({variable}))', '{variable}.size()'),
}


from_python_list_forward_list_template = r'''
// iterate across the list, current layer={layer_index} (empty means 1st)
for (Py_ssize_t i{layer_index} {{PyList_Size({name}{layer_index}) - 1}}; i{layer_index} >= 0 ; i{layer_index}--)
{{
    auto &{name}_container{next_layer_index} = *{insertion_function};
    <next_layer>
}}
'''.strip('\n')
types['std::forward_list'].from_python_list_template = from_python_list_forward_list_template
