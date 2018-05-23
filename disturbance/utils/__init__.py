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

def create_helppage_object(application_type='Disturbance'):
	"""
	Create a new HelpPage object, with latest help_text/label anchors defined in the latest ProposalType.schema
	"""
	try:
		application_type_id = ApplicationType.objects.get(name=application_type).id
	except Exception, e:
		print 'application type: {} does not exist, maybe!'.format(application_type, e)

	try:
		help_page = HelpPage.objects.filter(application_type_id=application_type_id).latest('version')
		next_version = help_page.version + 1
	except Exception, e:
		next_version = 1

	try:
		proposal_type = ProposalType.objects.filter(name=application_type).latest('version')
	except Exception, e:
		print 'proposal type: {} does not exist, maybe!'.format(application_type, e)


	help_list = search_keys(proposal_type.schema, search_list=['help_text','label'])
	richtext = create_richtext_help(help_list)

	HelpPage.objects.create(application_type_id=application_type_id, version=next_version, content=richtext)

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
    To run:
        from disturbance.utils import search
        search(dictionary, ['BRM', 'JM 1'])
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


