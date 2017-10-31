from preserialize.serialize import serialize

from ledger.accounts.models import EmailUser, Document
from wildlifelicensing.apps.applications.models import Application, ApplicationCondition, AmendmentRequest, Assessment, AssessmentCondition
from wildlifelicensing.apps.main.helpers import is_customer, is_officer


PROCESSING_STATUSES = dict(Application.PROCESSING_STATUS_CHOICES)
ID_CHECK_STATUSES = dict(Application.ID_CHECK_STATUS_CHOICES)
RETURNS_CHECK_STATUSES = dict(Application.RETURNS_CHECK_STATUS_CHOICES)
CHARACTER_CHECK_STATUSES = dict(Application.CHARACTER_CHECK_STATUS_CHOICES)
REVIEW_STATUSES = dict(Application.REVIEW_STATUS_CHOICES)
AMENDMENT_REQUEST_REASONS = dict(AmendmentRequest.REASON_CHOICES)
ASSESSMENT_STATUSES = dict(Assessment.STATUS_CHOICES)
ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES = dict(AssessmentCondition.ACCEPTANCE_STATUS_CHOICES)


def _extend_item_name(name, suffix, repetition):
    return '{}{}-{}'.format(name, suffix, repetition)


def create_data_from_form(schema, post_data, file_data, post_data_index=None):
    data = []

    for item in schema:
        data.append(_create_data_from_item(item, post_data, file_data, 0, ''))

    return data


def _create_data_from_item(item, post_data, file_data, repetition, suffix):
    item_data = {}

    if 'name' in item:
        extended_item_name = _extend_item_name(item['name'], suffix, repetition)
    else:
        raise Exception('Missing name in item %s' % item['label'])

    if 'children' not in item:
        if item['type'] in ['checkbox' 'declaration']:
            item_data[item['name']] = extended_item_name in post_data
        elif item['type'] == 'file':
            if extended_item_name in file_data:
                item_data[item['name']] = str(file_data.get(extended_item_name))
            elif extended_item_name + '-existing' in post_data and len(post_data[extended_item_name + '-existing']) > 0:
                item_data[item['name']] = post_data.get(extended_item_name + '-existing')
            else:
                item_data[item['name']] = ''
        else:
            if extended_item_name in post_data:
                item_data[item['name']] = post_data.get(extended_item_name)
    else:
        item_data_list = []
        for rep in xrange(0, int(post_data.get(extended_item_name, 1))):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(_create_data_from_item(child_item, post_data, file_data, 0,
                                                         '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

        item_data[item['name']] = item_data_list

    if 'conditions' in item:
        for condition in item['conditions'].keys():
            for child in item['conditions'][condition]:
                item_data.update(_create_data_from_item(child, post_data, file_data, repetition, suffix))

    return item_data


def extract_licence_fields(schema, data):
    licence_fields = []

    if schema is not None:
        for item in schema:
            _extract_licence_fields_from_item(item, data, licence_fields)

    return licence_fields


def _extract_licence_fields_from_item(item, data, licence_fields):
    children_extracted = False

    if item.get('isLicenceField', False):
        if 'children' not in item:
            # label / checkbox types are extracted differently so skip here
            if item['type'] not in ('label', 'checkbox'):
                licence_field = _create_licence_field(item)

                if 'options' in item:
                    licence_field['options'] = item['options']
                    licence_field['defaultBlank'] = item.get('defaultBlank', False)

                licence_field['data'] = _extract_item_data(item['name'], data)

                licence_fields.append(licence_field)
        else:
            licence_field = _create_licence_field(item)
            licence_field['children'] = []

            child_data = _extract_item_data(item['name'], data)

            for index in range(len(child_data)):
                group_licence_fields = []
                for child_item in item.get('children'):
                    if child_item['type'] == 'label' and child_item.get('isLicenceField', False):
                        _extract_label_and_checkboxes(child_item, item.get('children'), child_data[index], group_licence_fields)

                    _extract_licence_fields_from_item(child_item, child_data[index], group_licence_fields)
                licence_field['children'].append(group_licence_fields)

            licence_fields.append(licence_field)

            children_extracted = True

    # extract licence fields from field's children
    if 'children' in item and not children_extracted:
        for child_item in item.get('children'):
            if child_item['type'] == 'label' and child_item.get('isLicenceField', False):
                _extract_label_and_checkboxes(child_item, item.get('children'), data, licence_fields)
            _extract_licence_fields_from_item(child_item, data, licence_fields)

    # extract licence fields from field's conditional children
    if 'conditions' in item:
        for condition in item['conditions'].keys():
            for child_item in item['conditions'][condition]:
                if child_item['type'] == 'label' and child_item.get('isLicenceField', False):
                    _extract_label_and_checkboxes(child_item, item['conditions'][condition], data, licence_fields)
                _extract_licence_fields_from_item(child_item, data, licence_fields)


def _extract_label_and_checkboxes(current_item, items, data, licence_fields):
    licence_field = _create_licence_field(current_item)
    licence_field['options'] = []

    # find index of first checkbox after checkbox label within current item list
    checkbox_index = 0
    while checkbox_index < len(items) and items[checkbox_index]['name'] != current_item['name']:
        checkbox_index += 1
    checkbox_index += 1

    # add all checkboxes to licence field options
    while checkbox_index < len(items) and items[checkbox_index]['type'] == 'checkbox':
        name = items[checkbox_index]['name']
        option = {
            'name': name,
            'label': items[checkbox_index]['label']
        }
        if name in data:
            option['data'] = data[name]

        licence_field['options'].append(option)

        checkbox_index += 1

    licence_fields.append(licence_field)


def _create_licence_field(item):
    return {
        'name': item['name'],
        'type': item['type'],
        'label': item['licenceFieldLabel'] if 'licenceFieldLabel' in item else item['label'],
        'help_text': item.get('licenceFieldHelpText', ''),
        'readonly': item.get('isLicenceFieldReadonly', False)
    }


def _extract_item_data(name, data):
    def ___extract_item_data(name, data):
        if isinstance(data, dict):
            if name in data:
                return data[name]
            else:
                for value in data.values():
                    result = ___extract_item_data(name, value)
                    if result is not None:
                        return result
        if isinstance(data, list):
            for item in data:
                result = ___extract_item_data(name, item)
                if result is not None:
                    return result

    result = ___extract_item_data(name, data)

    return result if result is not None else ''


def update_licence_fields(licence_fields, post_data):
    if not licence_fields:
        return None
    for field in licence_fields:
        if 'children' not in field:
            if field['type'] == 'label':
                for option in field['options']:
                    if option['name'] in post_data:
                        option['data'] = post_data[option['name']]
            else:
                field['data'] = post_data.get(field['name'])
        else:
            for index, group in enumerate(field['children']):
                for child_field in group:
                    if child_field['type'] == 'label':
                        for option in child_field['options']:
                            if option['name'] in post_data:
                                data_list = post_data.getlist(option['name'])
                                if index < len(data_list):
                                    option['data'] = data_list[index]
                    else:
                        data_list = post_data.getlist(child_field['name'])
                        if index < len(data_list):
                            child_field['data'] = data_list[index]

    return licence_fields


def convert_documents_to_url(data, document_queryset, suffix):
    if isinstance(data, list):
        for item in data:
            convert_documents_to_url(item, document_queryset, '')
    else:
        for item, value in data.items():
            if isinstance(value, list):
                for rep in xrange(0, len(value)):
                    convert_documents_to_url(value[rep], document_queryset, '{}-{}'.format(suffix, rep))
            else:
                try:
                    # for legacy applications, need to check if there's a document where file is
                    # named by the file name rather than the form field name
                    data[item] = document_queryset.get(name=value).file.url
                except Document.DoesNotExist:
                    try:
                        data[item] = document_queryset.get(name='{}{}-0'.format(item, suffix)).file.url
                    except Document.DoesNotExist:
                        pass


class SessionDataMissingException(Exception):
    pass


def determine_applicant(request):
    if 'application' in request.session:
        if 'customer_pk' in request.session.get('application'):
            try:
                applicant = EmailUser.objects.get(pk=request.session['application']['customer_pk'])
            except EmailUser.DoesNotExist:
                raise SessionDataMissingException('customer_pk does not refer to existing customer')
            except EmailUser.MultipleObjectsReturned:
                raise SessionDataMissingException('customer_pk does not refer to several customers')
        else:
            raise SessionDataMissingException('customer_pk not set in session')
    else:
        raise SessionDataMissingException('application not set in session')

    return applicant


def set_session_application(session, application):
    session['application_id'] = application.id

    session.modified = True


def get_session_application(session):
    if 'application_id' in session:
        application_id = session['application_id']
    else:
        raise Exception('Application not in Session')

    try:
        return Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        raise Exception('Application not found for application_id {}'.format(application_id))


def delete_session_application(session):
    if 'application_id' in session:
        del session['application_id']
        session.modified = True


def remove_temp_applications_for_user(user):
    if is_customer(user):
        Application.objects.filter(applicant=user, customer_status='temp').delete()
    elif is_officer(user):
        Application.objects.filter(proxy_applicant=user, customer_status='temp').delete()


def clone_application_with_status_reset(application, is_licence_amendment=False):
    application.customer_status = 'temp'
    application.processing_status = 'temp'

    application.id_check_status = 'not_checked'
    application.character_check_status = 'not_checked'
    application.returns_check_status = 'not_checked'
    application.review_status = 'not_reviewed'

    application.correctness_disclaimer = False
    application.further_information_disclaimer = False

    application.lodgement_number = ''
    application.lodgement_sequence = 0
    application.lodgement_date = None

    application.assigned_officer = None

    application.licence = None

    if not is_licence_amendment:
        application.invoice_reference = ''

    original_application_pk = application.pk

    application.previous_application = Application.objects.get(pk=original_application_pk)

    application.pk = None

    application.save(no_revision=True)

    # clone variants
    for application_variant in Application.variants.through.objects.filter(application=original_application_pk):
        application_variant.application = application
        application_variant.pk = None
        application_variant.save()

    # clone documents
    for application_document in Application.documents.through.objects.filter(application=original_application_pk):
        application_document.application = application
        application_document.pk = None
        application_document.save()

    # clone conditions
    for application_condition in ApplicationCondition.objects.filter(application=original_application_pk):
        application_condition.application = application
        application_condition.pk = None
        application_condition.save()

    return application


def append_app_document_to_schema_data(schema, data, app_doc):
    section = {'type': 'section', 'label': 'Original Application Document', 'name': 'original_application_document'}
    section['children'] = [{'type': 'file', 'label': 'Application Document File', 'name': 'application_document'}]

    schema.append(section)

    data.append({'original_application_document': [{'application_document': app_doc}]})

    return schema, data


def get_log_entry_to(application):
    if application.proxy_applicant is None:
        return application.applicant.get_full_name()
    else:
        return application.proxy_applicant.get_full_name()


def format_application(instance, attrs):
    attrs['processing_status'] = PROCESSING_STATUSES[attrs['processing_status']]
    attrs['id_check_status'] = ID_CHECK_STATUSES[attrs['id_check_status']]
    attrs['returns_check_status'] = RETURNS_CHECK_STATUSES[attrs['returns_check_status']]
    attrs['character_check_status'] = CHARACTER_CHECK_STATUSES[attrs['character_check_status']]
    attrs['review_status'] = REVIEW_STATUSES[attrs['review_status']]
    attrs['licence_type']['default_conditions'] = serialize([ap.condition for ap in instance.licence_type.defaultcondition_set.order_by('order')])
    attrs['conditions'] = serialize([ap.condition for ap in instance.applicationcondition_set.order_by('order')])

    attrs['applicant_profile']['user'] = serialize(instance.applicant_profile.user,exclude=['postal_address','residential_address','billing_address'])
    attrs['applicant_profile']['postal_address'] = serialize(instance.applicant_profile.postal_address,exclude=['user','oscar_address'])
    if instance.applicant.identification is not None and instance.applicant.identification.file is not None: 
        attrs['applicant']['identification']['url'] = instance.applicant.identification.file.url
    if instance.applicant.senior_card is not None and instance.applicant.senior_card.file is not None: 
        attrs['applicant']['senior_card']['url'] = instance.applicant.senior_card.file.url

    return attrs


def format_amendment_request(instance, attrs):
    attrs['reason'] = AMENDMENT_REQUEST_REASONS[attrs['reason']]

    return attrs


def format_assessment(instance, attrs):
    attrs['conditions'] = serialize(instance.assessmentcondition_set.all().order_by('order'),
                                    fields=['acceptance_status', 'id', 'condition'], posthook=format_assessment_condition)
    attrs['status'] = ASSESSMENT_STATUSES[attrs['status']]

    return attrs


def format_assessment_condition(instance, attrs):
    attrs['acceptance_status'] = ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES[attrs['acceptance_status']]

    return attrs
