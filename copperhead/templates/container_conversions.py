# this is the primary loop template for converting to a Python list
to_python_list_template = r'''
Py_ssize_t pos{layer_index} {{0}};
for (auto & return_value_raw{layer_index} : return_value_raw{previous_layer_index})
{{
    <next_layer>
    <finalize_set>
    ++pos{layer_index};
}}
'''


# this intermediate template is used for inserting a new PyListObject above a loop as needed
to_python_list_intermediate_template = r'''
PyObject* return_value_list{next_layer_index} = PyList_New({get_size_function});
'''


# this intermediate tempalte is used for setting a new PyListObject into the parent list
to_python_list_intermediate_template_2 = r'''
PyList_SET_ITEM(return_value_list{layer_index}, pos{layer_index}, return_value_list{next_layer_index});
'''


# this is the inner template for setting the converted value (as opposed to nesting another list)
to_python_list_inner_template = r'''
PyObject *pyvalue = {to_python_function}(return_value_raw{layer_index});
PyList_SET_ITEM(return_value_list{layer_index}, pos{layer_index}, pyvalue);
'''


# this is the primary loop template for converting from a Python list
from_python_list_template = r'''
// iterate across the list, current layer={layer_index} (empty means 1st)
for (Py_ssize_t i{layer_index} {{0}}; i{layer_index} < PyList_Size({name}{layer_index}); i{layer_index}++)
{{
{insertion_function};
auto &{name}_container{next_layer_index} = {name}_container{layer_index}.back();
<next_layer>
}}
'''


# this intermediate template is used for getting the next nested PyListObject
from_python_list_intermediate_template = r'''
PyObject* {name}{next_layer_index} = PyList_GetItem({name}{layer_index}, i{layer_index});
'''


# this is the inner template for getting the converted value (as opposed to another list)
from_python_list_inner_template = r'''
PyObject *pyvalue = PyList_GetItem({name}{layer_index}, i{layer_index});
{name}_container{next_layer_index} = {from_python_function}(pyvalue);
'''
