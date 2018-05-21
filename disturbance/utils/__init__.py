from disturbance.components.proposals.models import Proposal

def search_all(search_list, application_type='Disturbance'):
    """
    To run:
        from disturbance.utils import search_all
        search_all(['BRM', 'JM 1'])
    """
    result = {}
    for p in Proposal.objects.filter(application_type__name=application_type):
        try:
            ret = search(p.data[0], search_list)
            if ret:
                result.update( {p.lodgement_number: ret} )
        except:
            pass

    return result

def search(dictionary, search_list):
    """
    To run:
        from disturbance.utils import search
        search(dictionary, ['BRM', 'JM 1'])
    """
    result = []
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.iteritems():
        if any(x in v for x in search_list):
            result.append( {k: v} )

    return result

def flatten(old_data, new_data=None, parent_key='', sep='.', width=4):
    '''
    Json-style nested dictionary / list flattener
    :old_data: the original data
    :new_data: the result dictionary
    :parent_key: all keys will have this prefix
    :sep: the separator between the keys
    :width: width of the field when converting list indexes
    '''
    if new_data is None:
        new_data = {}

    if isinstance(old_data, dict):
        for k, v in old_data.items():
            new_key = parent_key + sep + k if parent_key else k
            flatten(v, new_data, new_key, sep, width)
    elif isinstance(old_data, list):
        if len(old_data) == 1:
            flatten(old_data[0], new_data, parent_key, sep, width)
        else:
            for i, elem in enumerate(old_data):
                new_key = "{}{}{:0>{width}}".format(parent_key, sep if parent_key else '', i, width=width)
                flatten(elem, new_data, new_key, sep, width)
    else:
        if parent_key not in new_data:
            new_data[parent_key] = old_data
        else:
            raise AttributeError("key {} is already used".format(parent_key))

    return new_data


