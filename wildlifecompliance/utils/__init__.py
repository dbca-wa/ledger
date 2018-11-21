from django.conf import settings
from wildlifecompliance.components.applications.models import Application, ApplicationType
from collections import OrderedDict
from copy import deepcopy

   
def list_all(dictionary, search_list=[''], delimiter='.'):
    """
    List all flattenned questions, together with answers
    search_list = [''] --> will search for all questions with any answer, including non-answered questions

    To run:
        from wildlifecompliance.utils import list_all
        a = application.objects.all().last()
        dictionary = a.data[0]
        list_all(dictionary)

        OR

        // Search for specific test strings
        list_all(dictionary, ['search_string_1', 'search_string_2'])
    """
    result = [] 
    flat_dict = flatten(dictionary, delimiter=delimiter)
    for k, v in flat_dict.iteritems():
        if any(x in v for x in search_list):
            result.append( {k: v} )
    
    return result

def flatten(old_data, new_data=None, parent_key='', delimiter='.', width=4):
    '''
    Json-style nested dictionary / list flattener
    :old_data: the original data
    :new_data: the result dictionary
    :parent_key: all keys will have this prefix
    :delimiter: the separator between the keys
    :width: width of the field when converting list indexes
    '''
    if new_data is None:
        #new_data = {}
        new_data = OrderedDict()

    if isinstance(old_data, dict):
        for k, v in old_data.items():
            new_key = parent_key + delimiter + k if parent_key else k
            flatten(v, new_data, new_key, delimiter, width)
    elif isinstance(old_data, list):
        if len(old_data) == 1:
            flatten(old_data[0], new_data, parent_key, delimiter, width)
        else:
            for i, elem in enumerate(old_data):
                new_key = "{}{}{:0>{width}}".format(parent_key, delimiter if parent_key else '', i, width=width)
                flatten(elem, new_data, new_key, delimiter, width)
    else:
        if parent_key not in new_data:
            #import ipdb; ipdb.set_trace()
            new_data[parent_key] = old_data
        else:
            raise AttributeError("key {} is already used".format(parent_key))

    return new_data

