from django.conf import settings
from collections import OrderedDict
from wildlifecompliance.components.applications.models import Application
from wildlifecompliance.components.licences.models import DefaultActivity
#from copy import deepcopy


class ActivityPurposeMap():
    activity_purpose_map = {}

    def __init__(self):
        for i in DefaultActivity.objects.all():
            self.activity_purpose_map.update( {i.activity_type.name: i.activity.name} )

    def get(self, activity_name):
        """ Returns purpose, given activity 

        Result:
            from wildlifecompliance.utils import ActivityPurpose
            ap=ActivityPurposeMap()
            ap.get('Taking, Dealing and Processing')
            --> 'Bioprospecting - Flora or Fauna'

        """
        return self.activity_purpose_map.get(activity_name)


def unique_column_names(applications):
    """
    Returns Unique Column Names per Activity-Purpose - since 
	questions in schema may be added or deleted for newer applications

    To run:
        from wildlifecompliance.utils import unique_column_names
        applications =  Application.objects.filter(id__in=[121,122,123])
        unique_column_names(applications)

    Result:
		[u'Section1-0_0',
		 u'Section1-1_0',
		 u'Section1-2_0',
		 u'Section1-3_0',
		 u'Section2-0_0',
		 u'Section2-1_0',
		 u'Section2-2_0']
    """

    unique_names = set([])
    for app in applications:
        serialized_app = serialize_export(app)
        names = [item['name'] for item in serialized_app]

        unique_names = set(unique_names).union(names)

    return sorted(list(unique_names))

def unique_column_labels(applications):
    unique_names = set([])
    for app in applications:
        serialized_app = serialize_export(app)
        for item in serialized_app:
            item['name']
            
        names = [item['name'] for item in serialized_app]

        unique_names = set(unique_names).union(names)

def serialize_export(app_obj):
    """
    To run:
        from wildlifecompliance.utils import serialize_export
        app=Application.objects.get(id=140)
        serialize_export(app)
    _______________________________________
    key_value_pairs:
    [{u'Taking, Dealing and Processing.Section2_0.Section2-1_0': u''},
     {u'Taking, Dealing and Processing.Section2_0.Section2-0_0': u'abc'}]

    name_label_pairs:
    [{'label': u'The first question in section 1', 'name': u'Section1-0_0'},
     {'label': u'The second question in section 1', 'name': u'Section1-1_0'}

    result:
    [{'value': u'', 'name': u'Section2-1_0', 'key': u'Taking, Dealing and Processing.Section2_0.Section2-1_0', 'label': u'The second question in section 2'},
     {'value': u'abc', 'name': u'Section2-0_0', 'key': u'Taking, Dealing and Processing.Section2_0.Section2-0_0', 'label': u'The first question in section 2'}]
    """

    result = []
    name_label_pairs = search_keys(app_obj.schema, search_list=['name', 'label'])
    key_value_pairs = search(app_obj.data)

    ap = ActivityPurposeMap()
    # cross-reference name_label_pairs with key_value_pairs, and combine
    for key_value in key_value_pairs:
        for k,v in key_value.iteritems():
            name = k.split('.')[-1]
            activity = k.split('.')[0]
            try:
                label = [j['label']  for j in name_label_pairs if j['name']==name][0]
                result.append( dict(id=app_obj.id, key=k, activity=activity, purpose=ap.get(activity), name=name, label=label, value=v) )
            except:
                pass

    return result

class SearchUtils():
    def __init__(self, app_obj):
        self.app_obj = app_obj
        self.serialized_obj = serialize_export(app_obj)

    def search_value(self, section_name):
        """
        from wildlifecompliance.utils import SearchUtils
        a=Application.objects.get(id=129)
        s = SearchUtils(a)
        s.search_value(a, 'Species1-1_0')
        --> 'species a details'
        """
        for i in self.serialized_obj:
            if i['name'] == section_name:
                return i['value']
        return None


    
def search_value(app_obj, section_name):
    """
        from wildlifecompliance.utils import search_value
        a=Application.objects.get(id=129)
        search_value(a, 'Species1-1_0')
        --> 'species a details'
    """
    s = serialize_export(app_obj)
    for i in s:
        if i['name'] == section_name:
            return i['value']
    return None


def search(dictionary, search_list=[''], delimiter='.'):
    """
    List all flattened questions, together with answers
    search_list = [''] --> will search for all questions with any answer, including non-answered questions

    To run:
        from wildlifecompliance.utils import list_all
        a = application.objects.all().last()
        dictionary = a.data[0]
        search(dictionary)

        OR

        // Search for specific test strings
        search(dictionary, ['search_string_1', 'search_string_2']), or
        search(dictionary, ['BRM', 'JM 1'])
    """
    result = []
    flat_dict = flatten(dictionary, delimiter=delimiter)
    for k, v in flat_dict.iteritems():
        if any(x in v for x in search_list):
            result.append( {k: v} )

    return result

def search_keys(dictionary, search_list=['help_text', 'label']):
    """
    Return search_list pairs from the schema -- given help_text, finds the equiv. label

    To run:
        from disturbance.utils import search_keys
        search_keys2(dictionary, search_list=['help_text', 'label'])
        search_keys2(dictionary, search_list=['name', 'label'])
    """
    search_item1 = search_list[0]
    search_item2 = search_list[1]
    result = []
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.iteritems():
        if any(x in k for x in search_list):
            result.append( {k: v} )

    help_list = []
    for i in result:
        try:
            key = i.keys()[0]
            if key and key.endswith(search_item1):
                corresponding_label_key = '.'.join(key.split('.')[:-1]) + '.' + search_item2
                for j in result:
                    key_label = j.keys()[0]
                    if key_label and key_label.endswith(search_item2) and key_label == corresponding_label_key: # and result.has_key(key):
                        #import ipdb; ipdb.set_trace()
                        help_list.append({search_item2: j[key_label], search_item1: i[key]})
        except Exception, e:
            #import ipdb; ipdb.set_trace()
            print e

    return help_list

def test_search_multiple_keys():
    p=Proposal.objects.get(id=139)
    return search_multiple_keys(p.schema, primary_search='isRequired', search_list=['label', 'name'])

def search_multiple_keys(dictionary, primary_search='isRequired', search_list=['label', 'name']):
    """
    Given a primary search key, return a list of key/value pairs corresponding to the same section/level

    To test:
        p=Proposal.objects.get(id=139)
        return search_multiple_keys(p.schema, primary_search='isRequired', search_list=['label', 'name'])

    Example result:
    [
        {'isRequired': {'label': u'Enter the title of this proposal','name': u'Section0-0'}},
        {'isRequired': {'label': u'Enter the purpose of this proposal', 'name': u'Section0-1'}},
        {'isRequired': {'label': u'In which Local Government Authority (LAG) is this proposal located?','name': u'Section0-2'}},
        {'isRequired': {'label': u'Describe where this proposal is located', 'name': u'Section0-3'}}
    ]
    """

    # get a flat list of the schema and keep only items in all_search_list
    all_search_list = [primary_search] + search_list
    result = []
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.iteritems():
        if any(x in k for x in all_search_list):
            result.append( {k: v} )

    # iterate through the schema and get the search items corresponding to each primary_search item (at the same level/section)
    help_list = []
    for i in result:
        try:
            tmp_dict = {}
            key = i.keys()[0]
            if key and key.endswith(primary_search):
                for item in all_search_list:
                    corresponding_label_key = '.'.join(key.split('.')[:-1]) + '.' + item
                    for j in result:
                        key_label = j.keys()[0]
                        if key_label and key_label.endswith(item) and key_label == corresponding_label_key: # and result.has_key(key):
                            tmp_dict.update({item: j[key_label]})
                if tmp_dict:
                    help_list.append(  tmp_dict )
                #if tmp_dict:
                #  help_list.append( {primary_search: tmp_dict} )

        except Exception, e:
            #import ipdb; ipdb.set_trace()
            print e

    return help_list

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

