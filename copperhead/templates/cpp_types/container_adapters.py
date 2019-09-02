from .cpp_type import base_cpp_type


class ContainerAdapter(base_cpp_type):
    def __init__(self, cpp_type, insertion_function, get_size_function):
        super().__init__(cpp_type, 'PyObject*', 'O')
        self.insertion_function = insertion_function
        self.get_size_function = get_size_function

    to_python_list_template = r'''
Py_ssize_t pos{layer_index} {{0}};
while (!return_value_raw{previous_layer_index}.empty())
{{
    auto & return_value_raw{layer_index} = return_value_raw{previous_layer_index}.top();
    <next_layer>
    <finalize_set>
    return_value_raw{previous_layer_index}.pop();
    ++pos{layer_index};
}}
'''.rstrip('\n')

    to_python_list_intermediate_template = r'''
PyObject* return_value_list{layer_index} = PyList_New({get_size_function});
'''.rstrip('\n')


    to_python_list_intermediate_template_2 = r'''
PyList_SET_ITEM(return_value_list{previous_layer_index}, pos{layer_index}, return_value_list{next_layer_index});
'''.rstrip('\n')

    to_python_list_inner_template = r'''
PyObject *pyvalue = {to_python_function}(return_value_raw{layer_index});
PyList_SET_ITEM(return_value_list{previous_layer_index}, pos{layer_index}, pyvalue);
'''.rstrip('\n')

    from_python_list_template = r'''
// iterate across the list, current layer={layer_index} (empty means 1st)
for (Py_ssize_t i{layer_index} {{PyList_Size({name}{layer_index}) - 1}}; i{layer_index} >= 0; i{layer_index}--)
{{
    {insertion_function};
    auto &{name}_container{next_layer_index} = {name}_container{layer_index}.top();
    <next_layer>
}}
'''.rstrip('\n')

    from_python_list_intermediate_template = r'''
PyObject* {name}{next_layer_index} = PyList_GetItem({name}{layer_index}, i{layer_index});
'''.rstrip('\n')

    from_python_list_inner_template = r'''
PyObject *pyvalue = PyList_GetItem({name}{layer_index}, i{layer_index});
{name}_container{next_layer_index} = {from_python_function}(pyvalue);
'''


types = {
    'std::stack': ContainerAdapter('std::stack', '{variable}.emplace()', '{variable}.size()'),
    'std::queue': ContainerAdapter('std::queue', '{variable}.emplace()', '{variable}.size()'),
    # 'std::priority_queue': ContainerAdapter('std::priority_queue', '{variable}.emplace()', '{variable}.size()'),
}


queue_from_python_list_template = r'''
// iterate across the list, current layer={layer_index} (empty means 1st)
for (Py_ssize_t i{layer_index} {{0}}; i{layer_index} < PyList_Size({name}{layer_index}); i{layer_index}++)
{{
    {insertion_function};
    auto &{name}_container{next_layer_index} = {name}_container{layer_index}.back();
    <next_layer>
}}
'''


queue_to_python_list_template = r'''
Py_ssize_t pos{layer_index} {{0}};
while (!return_value_raw{previous_layer_index}.empty())
{{
    auto & return_value_raw{layer_index} = return_value_raw{previous_layer_index}.front();
    <next_layer>
    <finalize_set>
    return_value_raw{previous_layer_index}.pop();
    ++pos{layer_index};
}}
'''
types['std::queue'].from_python_list_template = queue_from_python_list_template
types['std::queue'].to_python_list_template = queue_to_python_list_template


# priority_queue_from_python_list_template = r'''
# // iterate across the list, current layer={layer_index} (empty means 1st)
# for (Py_ssize_t i{layer_index} {{PyList_Size({name}{layer_index}) - 1}}; i{layer_index} >= 0; i{layer_index}--)
# {{
#     {insertion_function};
#     auto {name}_container{next_layer_index} = {name}_container{layer_index}.top();
#     <next_layer>
# }}
# '''

# priority_queue_from_python_list_inner_template = r'''
# PyObject *pyvalue = PyList_GetItem({name}{layer_index}, i{layer_index});
# {name}_container{next_layer_index} = {from_python_function}(pyvalue);
# '''
# types['std::priority_queue'].from_python_list_template = priority_queue_from_python_list_template
# types['std::priority_queue'].from_python_list_inner_template = priority_queue_from_python_list_inner_template
