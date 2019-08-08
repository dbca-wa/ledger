from wildlifecompliance.components.call_email.models import Location #, CallEmail
from wildlifecompliance.components.call_email.serializers import LocationSerializer
#from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome
from django.core.files.storage import default_storage 
import os
from django.core.files.base import ContentFile
import traceback

def create_new_person(request, *args, **kwargs):
    pass


def save_location(location_request_data, *args, **kwargs):
    if location_request_data.get('id'):
        location_instance = Location.objects.get(id=location_request_data.get('id'))
        location_serializer = LocationSerializer(
            instance=location_instance,
            data=location_request_data,
            partial=True
        )
        location_serializer.is_valid(raise_exception=True)
        if location_serializer.is_valid():
            location_serializer.save()
    else:
        location_serializer = LocationSerializer(
            data=location_request_data,
            partial=True
        )
        location_serializer.is_valid(raise_exception=True)
        if location_serializer.is_valid():
            location_instance = location_serializer.save()
    return location_serializer.data

def process_generic_document(request, instance, document_type=None, *args, **kwargs):
    print("process_generic_document")
    print(request.data)
    try:
        action = request.data.get('action')
        comms_log_id = request.data.get('comms_log_id')
        comms_instance = None
        # returned_file_data = None

        if document_type == 'comms_log' and comms_log_id and comms_log_id is not 'null':
            comms_instance = instance.comms_logs.get(
                    id=comms_log_id)
        elif document_type == 'comms_log':
            comms_instance = instance.comms_logs.create()

        print('comms_instance')
        print(comms_instance)

        if action == 'list':
            pass

        elif action == 'delete':
            delete_document(request, instance, comms_instance)

        elif action == 'cancel':
            deleted = cancel_document(request, instance, comms_instance)

        elif action == 'save':
            save_document(request, instance, comms_instance)

        # HTTP Response varies by action and instance type
        if comms_instance and action == 'cancel' and deleted:
            return deleted
        elif comms_instance:
            returned_file_data = [dict(
                        file=d._file.url,
                        id=d.id,
                        name=d.name,
                        ) for d in comms_instance.documents.all() if d._file]
            return {'filedata': returned_file_data,
                    'comms_instance_id': comms_instance.id}
        else:
            returned_file_data = [dict(
                        file=d._file.url,
                        id=d.id,
                        name=d.name,
                        ) for d in instance.documents.all() if d._file]
            return {'filedata': returned_file_data}

    except Exception as e:
        print(traceback.print_exc())
        raise e

def delete_document(request, instance, comms_instance=None):
    # inspection report delete
    if request.data.get('inspection_report') and 'document_id' in request.data:
        document_id = request.data.get('document_id')
        document = instance.report.get(id=document_id)

    # comms_log doc store delete
    elif comms_instance and 'document_id' in request.data:
        document_id = request.data.get('document_id')
        document = comms_instance.documents.get(id=document_id)

    # default doc store delete
    elif 'document_id' in request.data:
        document_id = request.data.get('document_id')
        document = instance.documents.get(id=document_id)

    if document._file and os.path.isfile(
            document._file.path):
        os.remove(document._file.path)

    document.delete()

def cancel_document(request, instance, comms_instance=None):
        # inspection report cancel
        if request.data.get('inspection_report'):
            document_list = instance.report.all()

            for document in document_list:
                if document._file and os.path.isfile(
                        document._file.path):
                    os.remove(document._file.path)
                document.delete()

        # comms_log doc cancel
        elif comms_instance:
            document_list = comms_instance.documents.all()

            for document in document_list:
                if document._file and os.path.isfile(
                        document._file.path):
                    os.remove(document._file.path)
                document.delete()
            return comms_instance.delete()

        # default doc cancel
        else:
            document_list = instance.documents.all()

            for document in document_list:
                if document._file and os.path.isfile(
                        document._file.path):
                    os.remove(document._file.path)
                document.delete()

def save_document(request, instance, comms_instance=None):
        # inspection report save
        if request.data.get('inspection_report') and 'filename' in request.data:
            filename = request.data.get('filename')
            _file = request.data.get('_file')

            document = instance.report.get_or_create(
                name=filename)[0]
            path = default_storage.save(
                'wildlifecompliance/compliance/{}/{}/report/{}'.format(
                    instance._meta.model_name, instance.id, filename), ContentFile(
                    _file.read()))

            document._file = path
            document.save()
        # comms_log doc store save
        elif comms_instance and 'filename' in request.data:
            filename = request.data.get('filename')
            _file = request.data.get('_file')

            document = comms_instance.documents.get_or_create(
                name=filename)[0]
            path = default_storage.save(
                'wildlifecompliance/compliance/{}/{}/communications/{}/documents/{}'.format(
                    instance._meta.model_name, instance.id, comms_instance.id, filename), ContentFile(
                    _file.read()))

            document._file = path
            document.save()

        # default doc store save
        elif 'filename' in request.data:
            filename = request.data.get('filename')
            _file = request.data.get('_file')

            document = instance.documents.get_or_create(
                name=filename)[0]
            path = default_storage.save(
                'wildlifecompliance/compliance/{}/{}/documents/{}'.format(
                    instance._meta.model_name, instance.id, filename), ContentFile(
                    _file.read()))

            document._file = path
            document.save()

