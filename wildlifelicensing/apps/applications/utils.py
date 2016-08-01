import os
import shutil
import string
import random

from preserialize.serialize import serialize

from oscar.apps.partner.strategy import Selector

from ledger.catalogue.models import Product
from ledger.accounts.models import EmailUser, Document

from wildlifelicensing.apps.applications.models import Application, ApplicationCondition, AmendmentRequest, Assessment, AssessmentCondition
from collections import OrderedDict


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


def create_data_from_form(form_structure, post_data, file_data, post_data_index=None):
    data = []

    for item in form_structure:
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


def _append_random_to_filename(file_name, random_string_size=5):
    name, extention = os.path.splitext(file_name)

    chars = string.ascii_uppercase + string.digits

    random_string = ''.join(random.choice(chars) for _ in range(random_string_size))

    return '{}-{}{}'.format(name, random_string, extention)


def rename_filename_doubleups(post_data, file_data):
    counter = 0

    ordered_file_data = OrderedDict(file_data)
    post_data_values = post_data.values()
    file_data_values = [str(file_value) for file_value in ordered_file_data.values()]

    for file_key, file_value in ordered_file_data.iteritems():
        if str(file_value) in file_data_values[:counter] or str(file_value) in post_data_values:
            file_data[file_key].name = _append_random_to_filename(file_value.name)

        counter += 1


def get_all_filenames_from_application_data(item, data):
    filenames = []

    if isinstance(item, list):
        for i, child in enumerate(item):
            filenames += get_all_filenames_from_application_data(child, data[i])
    elif 'children' in item:
        for child in item['children']:
            for child_data in data[item['name']]:
                filenames += get_all_filenames_from_application_data(child, child_data)
    else:
        if item.get('type', '') == 'file':
            if item['name'] in data and len(data[item['name']]) > 0:
                filenames.append(data[item['name']])

    return filenames


def prepend_url_to_files(item, data, root_url):
    # ensure root url ends with a /
    if root_url[-1] != '/':
        root_url += '/'

    if isinstance(item, list):
        for i, child in enumerate(item):
            prepend_url_to_files(child, data[i], root_url)
    elif 'children' in item:
        for child in item['children']:
            for child_data in data[item['name']]:
                prepend_url_to_files(child, child_data, root_url)
    else:
        if item.get('type', '') == 'file':
            if item['name'] in data and len(data[item['name']]) > 0:
                data[item['name']] = root_url + data[item['name']]


def convert_documents_to_url(item, data, document_queryset):
    if isinstance(item, list):
        for i, child in enumerate(item):
            convert_documents_to_url(child, data[i], document_queryset)
    elif 'children' in item:
        for child in item['children']:
            for child_data in data[item['name']]:
                convert_documents_to_url(child, child_data, document_queryset)
    else:
        if item.get('type', '') == 'file':
            if item['name'] in data and len(data[item['name']]) > 0:
                try:
                    data[item['name']] = document_queryset.get(name=data[item['name']]).file.url
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


def set_app_session_data(session, key, value):
    if 'application' not in session:
        session['application'] = {}

    session['application'][key] = value

    session.modified = True


def is_app_session_data_set(session, key):
    return 'application' in session and key in session['application']


def get_app_session_data(session, key):
    if is_app_session_data_set(session, key):
        return session['application'][key]
    else:
        return None


def delete_app_session_data(session):
    temp_files_dir = get_app_session_data(session, 'temp_files_dir')

    if temp_files_dir is not None:
        try:
            shutil.rmtree(temp_files_dir)
        except (shutil.Error, OSError) as e:
            raise e

    if 'application' in session:
        del session['application']


def clone_application_for_renewal(application, save=False):
    application.customer_status = 'draft'
    application.processing_status = 'renewal'

    application.id_check_status = 'not_checked'
    application.character_check_status = 'not_checked'
    application.review_status = 'not_reviewed'

    application.lodgement_number = ''
    application.lodgement_sequence = 0
    application.lodgement_date = None

    application.assigned_officer = None

    application.licence = None

    original_application_pk = application.pk

    application.previous_application = Application.objects.get(pk=original_application_pk)

    application.pk = None

    application.save(no_revision=True)

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


def licence_requires_payment(licence_type):
    try:
        product = Product.objects.get(title=licence_type.code_slug)

        selector = Selector()
        strategy = selector.strategy()
        purchase_info = strategy.fetch_for_product(product=product)

        return purchase_info.price.excl_tax > 0

    except Product.DoesNotExist:
        return False


def format_application(instance, attrs):
    attrs['processing_status'] = PROCESSING_STATUSES[attrs['processing_status']]
    attrs['id_check_status'] = ID_CHECK_STATUSES[attrs['id_check_status']]
    attrs['returns_check_status'] = RETURNS_CHECK_STATUSES[attrs['returns_check_status']]
    attrs['character_check_status'] = CHARACTER_CHECK_STATUSES[attrs['character_check_status']]
    attrs['review_status'] = REVIEW_STATUSES[attrs['review_status']]

    attrs['conditions'] = serialize([ap.condition for ap in instance.applicationcondition_set.all().order_by('order')])

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
