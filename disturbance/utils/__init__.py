from disturbance.components.proposals.models import Proposal, ProposalType, HelpPage, ApplicationType
from collections import OrderedDict

def search_all(search_list, application_type='Disturbance'):
    """
    To run:
        from disturbance.utils import search_all
        search_all(['BRM', 'JM 1'])
    """
    result = {}
    for p in Proposal.objects.filter(application_type__name=application_type):
        try:
            if p.data:
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

def test_compare_data():
    p=Proposal.objects.get(id=100)

    dict1=p.data[0]
    dict2=p.previous_application.data[0]
    return compare_data(dict1, dict2, p.schema)


def compare_data(dict1, dict2, schema):
    """
    dict1 - most recent data
    dict2 - prev data
    schema - proposal.schema

    To run:
        from disturbance.utils import compare
        compare_data(dict1, dict2, schema)

    eg.
        p=Proposal.objects.get(id=110)
        dict1=p.data[0]
        dict2=p.previous_application.data[0]
        return compare_data(dict1, dict2, p.schema)
    """
    result = []
    flat_dict1 = flatten(dict1)
    flat_dict2 = flatten(dict2)
    for k1, v1 in flat_dict1.iteritems():
        for k2, v2 in flat_dict2.iteritems():
            if k1 ==k2 and v2:
                if v1 != v2:
                    result.append( {k1: [v1, v2]} )
                continue

    # Now find the Question(label) for this section(k1 or k2) and incorporate into the dict result
    new = {}
    name_map=search_keys2(flatten(schema), search_list=['name', 'label'])
    for item in result:
        k = item.keys()[0]
        v = item[k]
        section = k.split('.')[-1]
        label = [i['label'] for i in name_map if section in i['name'] ]
        if label:
            new.update( {k: {label[0]: v}} )

    return new


def create_helppage_object(application_type='Disturbance', help_type=HelpPage.HELP_TEXT_EXTERNAL):
	"""
	Create a new HelpPage object, with latest help_text/label anchors defined in the latest ProposalType.schema
	"""
	try:
		application_type_id = ApplicationType.objects.get(name=application_type).id
	except Exception, e:
		print 'application type: {} does not exist, maybe!'.format(application_type, e)

	try:
		help_page = HelpPage.objects.filter(application_type_id=application_type_id, help_type=help_type).latest('version')
		next_version = help_page.version + 1
	except Exception, e:
		next_version = 1

	try:
		proposal_type = ProposalType.objects.filter(name=application_type).latest('version')
	except Exception, e:
		print 'proposal type: {} does not exist, maybe!'.format(application_type, e)

   
 	help_text = 'help_text' if help_type==HelpPage.HELP_TEXT_EXTERNAL else 'help_text_assessor'
	help_list = search_keys(proposal_type.schema, search_list=[help_text,'label'])
	richtext = create_richtext_help(help_list)

	HelpPage.objects.create(application_type_id=application_type_id, help_type=help_type, version=next_version, content=richtext)

def create_richtext_help(help_list=None):

	# for testing
	if not help_list:
		pt = ProposalType.objects.all()[4]
		help_list = search_keys(pt.schema, search_list=['help_text','label'])[:3]

	richtext = u''
	for i in help_list:
		if 'anchor=' in i['help_text']:
			anchor = i['help_text'].split("anchor=")[1].split("\"")[0]
			#print anchor, i['label']

			richtext += u'<h1><a id="{0}" name="{0}"> {1} </a></h1><p>&nbsp;</p>'.format(anchor, i['label'])
		else:
			richtext += u'<h1> {} </h1><p>&nbsp;</p>'.format(i['label'])

	return richtext



def search_keys(dictionary, search_list=['help_text', 'label']):
    """
    Return search_list pairs from the schema -- given help_text, finds the equiv. label

    To run:
        from disturbance.utils import search_keys
        search_keys(dictionary, search_list=['help_text', 'label'])
    """
    result = []
    flat_dict = flatten(dictionary)
    for k, v in flat_dict.iteritems():
        if any(x in k for x in search_list):
            result.append( {k: v} )

    help_list = []
    for i in result:
        try:
            key = i.keys()[0]
            if key and key.endswith('help_text'):
                corresponding_label_key = '.'.join(key.split('.')[:-1]) + '.label'
                for j in result:
                    key_label = j.keys()[0]
                    if key_label and key_label.endswith('label') and key_label == corresponding_label_key: # and result.has_key(key):
                        #import ipdb; ipdb.set_trace()
                        help_list.append({'label': j[key_label], 'help_text': i[key]})
        except Exception, e:
            #import ipdb; ipdb.set_trace()
            print e

    return help_list

def search_keys2(dictionary, search_list=['help_text', 'label']):
    """
    Generic version of search_keys(). Return search_list pairs from the schema -- given help_text, finds the equiv. label

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
        #new_data = {}
        new_data = OrderedDict()

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
            #import ipdb; ipdb.set_trace()
            new_data[parent_key] = old_data
        else:
            raise AttributeError("key {} is already used".format(parent_key))

    return new_data


