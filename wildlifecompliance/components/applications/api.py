import traceback
import os
import datetime
import base64
import json
import geojson
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db.models import Q, Min
from django.db import transaction
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.conf import settings
from wildlifecompliance import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes, parser_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from ledger.checkout.utils import calculate_excl_gst
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from wildlifecompliance.components.applications.utils import save_proponent_data,save_assessor_data,get_activity_type_schema
from wildlifecompliance.components.main.models import Document
from wildlifecompliance.components.main.utils import checkout, set_session_application, delete_session_application
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.applications.models import (
    Application,
    ApplicationDocument,
    ApplicationCondition,
    ApplicationStandardCondition,
    Assessment,
    ApplicationGroupType,
    AmendmentRequest,
    ApplicationUserAction
)
from wildlifecompliance.components.applications.serializers import (
    ApplicationSerializer,
    InternalApplicationSerializer,
    SaveApplicationSerializer,
    BaseApplicationSerializer,
    DTInternalApplicationSerializer,
    DTExternalApplicationSerializer,
    ApplicationUserActionSerializer,
    ApplicationLogEntrySerializer,
    ApplicationConditionSerializer,
    ApplicationStandardConditionSerializer,
    ProposedLicenceSerializer,
    ProposedDeclineSerializer,
    AssessmentSerializer,
    ApplicationGroupTypeSerializer,
    SaveAssessmentSerializer,
    AmendmentRequestSerializer,
    ExternalAmendmentRequestSerializer,
    ApplicationProposedIssueSerializer,
    DTAssessmentSerializer
)


class GetEmptyList(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        return Response([])

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Application.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.wildlifecompliance_organisations.all()]
            return Application.objects.filter(Q(org_applicant_id__in = user_orgs) | Q(proxy_applicant = user) | Q(submitter = user) )
        return Application.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = BaseApplicationSerializer(queryset, many=True, context={'request':request})
        return Response(serializer.data)

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def process_document(self, request, *args, **kwargs):
        try:
            #import ipdb; ipdb.set_trace()
            instance = self.get_object()
            action = request.POST.get('action')
            section = request.POST.get('input_name')
            if action == 'list' and 'input_name' in request.POST:
                pass

            elif action == 'delete' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.documents.get(id=document_id)

                if document._file and os.path.isfile(document._file.path) and document.can_delete:
                    os.remove(document._file.path)

                document.delete()
                instance.save(version_comment='Approval File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' in request.POST and 'filename' in request.POST:
                application_id = request.POST.get('application_id')
                filename = request.POST.get('filename')
                _file = request.POST.get('_file')
                if not _file:
                    _file = request.FILES.get('_file')

                document = instance.documents.get_or_create(input_name=section, name=filename)[0]
                path = default_storage.save('applications/{}/documents/{}'.format(application_id, filename), ContentFile(_file.read()))

                document._file = path
                document.save()
                instance.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return  Response( [dict(input_name=d.input_name, name=d.name,file=d._file.url, id=d.id, can_delete=d.can_delete) for d in instance.documents.filter(input_name=section) if d._file] )

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ApplicationUserActionSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = ApplicationLogEntrySerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                request.data['application'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = ApplicationLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def conditions(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.conditions.all()
            licence_activity_type = self.request.query_params.get('licence_activity_type', None)
            print('activity type from conditions api')
            print(licence_activity_type)
            if licence_activity_type is not None:
                print('inside if')
                qs = qs.filter(licence_activity_type=licence_activity_type)
            print(qs)

            serializer = ApplicationConditionSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def assessments(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.assessments
            serializer = AssessmentSerializer(qs,many=True)
            print(qs)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['GET',])
    def amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.amendment_requests
            qs = qs.filter(status = 'requested')
            serializer = ExternalAmendmentRequestSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @list_route(methods=['GET',])
    def internal_datatable_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = DTInternalApplicationSerializer(queryset, many=True,context={'request':request})
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        user_orgs = [org.id for org in request.user.wildlifecompliance_organisations.all()];
        qs = []
        qs.extend(list(self.get_queryset().filter(submitter = request.user).exclude(processing_status='discarded').exclude(processing_status=Application.PROCESSING_STATUS_CHOICES[13][0])))
        qs.extend(list(self.get_queryset().filter(proxy_applicant = request.user).exclude(processing_status='discarded').exclude(processing_status=Application.PROCESSING_STATUS_CHOICES[13][0])))
        qs.extend(list(self.get_queryset().filter(org_applicant_id__in = user_orgs).exclude(processing_status='discarded').exclude(processing_status=Application.PROCESSING_STATUS_CHOICES[13][0])))
        queryset = list(set(qs))
        serializer = DTExternalApplicationSerializer(queryset, many=True,context={'request':request})
        return Response(serializer.data)

    @detail_route(methods=['GET',])
    def internal_application(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InternalApplicationSerializer(instance,context={'request':request})
        return Response(serializer.data)

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            print("=====FRom Submit application")
            print(request.POST.keys())
            instance = self.get_object()
            instance.submit(request,self)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            delete_session_application(request.session)
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            delete_session_application(request.session)
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def application_fee_checkout(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            product_lines = []
            application_submission = u'Application submitted by {} confirmation WC{}'.format(
                u'{} {}'.format(instance.submitter.first_name, instance.submitter.last_name), instance.id)
            set_session_application(request.session, instance)
            product_lines.append({
                'ledger_description': '{}'.format(instance.licence_type_name),
                'quantity': 1,
                'price_incl_tax': str(instance.application_fee),
                'price_excl_tax': str(calculate_excl_gst(instance.application_fee)),
                'oracle_code': ''
            })
            checkout_result = checkout(request, instance, lines=product_lines,
                                       invoice_text=application_submission)
            return checkout_result
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def accept_id_check(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept_id_check(request)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def reset_id_check(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.reset_id_check(request)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def request_id_check(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.request_id_check(request)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def accept_character_check(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept_character_check(request)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def send_to_assessor(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print(request.data)
            # instance.send_to_assessor(request)
            # serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_officer(request,request.user)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get('assessor_id',None)
            user = None
            if not user_id:
                raise serializers.ValidationError('An assessor id is required')
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError('A user with the id passed in does not exist')
            instance.assign_officer(request,user)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def unassign(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign(request)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def update_activity_status(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            activity_id = request.data.get('activity_id')
            status = request.data.get('status')
            if not status or not activity_id:
                raise serializers.ValidationError('Status and activity id is required')
            else:
                if status not in Application.ACTIVITY_PROCESSING_STATUS_CHOICES:
                    raise serializers.ValidationError('The status provided is not allowed')
            instance.update_activity_status(request,activity_id,status)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def complete_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            selected_assessment_id = request.data.get('selected_assessment_tab')
            print('from api')
            print(selected_assessment_id)
            instance.complete_assessment(request)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def proposed_licence(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedLicenceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.proposed_licence(request,serializer.validated_data)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def get_proposed_decisions(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs=instance.get_proposed_decisions(request)
            # qs = instance.decisions.filter(action='propose_issue')
            # print(qs)
            serializer = ApplicationProposedIssueSerializer(qs,many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def final_decision(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # serializer = ProposedLicenceSerializer(data=request.data)
            # serializer.is_valid(raise_exception=True)
            print(request.data)
            instance.final_decision(request)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def proposed_decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedDeclineSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.proposed_decline(request,serializer.validated_data)
            serializer = InternalApplicationSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def draft(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            save_proponent_data(instance,request,self)
            return redirect(reverse('external'))
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
        raise serializers.ValidationError(str(e))

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def assessor_save(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            save_assessor_data(instance,request,self)
            return redirect(reverse('external'))
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @renderer_classes((JSONRenderer,))
    def create(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            app_data = self.request.data
            licence_class_data=app_data.pop('licence_class_data')
            licence_type_name = app_data.pop('licence_type_name')
            schema_data=get_activity_type_schema(licence_class_data)
            org_applicant=request.data.get('org_applicant')
            proxy_applicant=request.data.get('proxy_applicant')
            application_fee = request.data.get('application_fee')
            licence_fee = request.data.get('licence_fee')
            #import ipdb; ipdb.set_trace()
            data = {
                'schema':schema_data,
                'submitter': request.user.id,
                'licence_type_data':licence_class_data,
                'licence_type_name': licence_type_name,
                'org_applicant': org_applicant,
                'proxy_applicant': proxy_applicant,
                'application_fee': application_fee,
                'licence_fee': licence_fee
            }
            serializer = SaveApplicationSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def update(self, request, *args, **kwargs):
        try:
            http_status = status.HTTP_200_OK
            instance = self.get_object()
            serializer = SaveApplicationSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def destroy(self, request,*args,**kwargs):
        try:
            http_status = status.HTTP_200_OK
            instance = self.get_object()
            serializer = SaveApplicationSerializer(instance,{'processing_status':'discarded'},partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data,status=http_status)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def assessment_details(self, request, *args, **kwargs):
        # queryset = self.get_queryset()
        instance = self.get_object()
        queryset =  Assessment.objects.filter(application=instance.id)
        licence_activity_type = self.request.query_params.get('licence_activity_type', None)
        if licence_activity_type is not None:
            queryset = queryset.filter(licence_activity_type=licence_activity_type)
        serializer = AssessmentSerializer(queryset,many=True)
        return Response(serializer.data)

    @detail_route(permission_classes=[],methods=['GET'])
    def application_checkout_status(self, request, *args, **kwargs):
        from django.utils import timezone
        http_status = status.HTTP_200_OK
        try:
            instance = self.get_object()
            response = {
                'status': 'rejected',
                'error': ''
            }
            # # Check the type of booking
            # if instance.booking_type != 3:
            #    response['error'] = 'This booking has already been paid for'
            #    return Response(response,status=status.HTTP_200_OK)
            # # Check if the time for the booking has elapsed
            # if instance.expiry_time <= timezone.now():
            #     response['error'] = 'This booking has expired'
            #     return Response(response,status=status.HTTP_200_OK)
            #if all is well
            response['status'] = 'approved'
            return Response(response,status=status.HTTP_200_OK)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

class ApplicationConditionViewSet(viewsets.ModelViewSet):
    queryset = ApplicationCondition.objects.all()
    serializer_class = ApplicationConditionSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return ApplicationCondition.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.wildlifecompliance_organisations.all()]
            user_applications = [application.id for application in Application.objects.filter(Q(org_applicant_id__in = user_orgs) | Q(proxy_applicant = user) | Q(submitter = user) )]
            return ApplicationCondition.objects.filter(Q(application_id__in = user_applications))
        return ApplicationCondition.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                instance = serializer.save()
                instance.submit()
                instance.application.log_user_action(ApplicationUserAction.ACTION_ENTER_CONDITIONS.format(instance.licence_activity_type.name),request)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def move_up(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.up()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def move_down(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.down()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

class ApplicationStandardConditionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApplicationStandardCondition.objects.all()
    serializer_class = ApplicationStandardConditionSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return ApplicationStandardCondition.objects.all()
        elif is_customer(self.request):
            return ApplicationStandardCondition.objects.none()
        return ApplicationStandardCondition.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Assessment.objects.all()
        elif is_customer(self.request):
            return Assessment.objects.none()
        return Assessment.objects.none()

    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        # Get the assessor groups the current user is member of
        assessor_groups = ApplicationGroupType.objects.filter(type='assessor', members__email=request.user.email)

        # For each assessor groups get the assessments
        queryset = self.get_queryset().none()
        for group in assessor_groups:
            queryset = queryset | Assessment.objects.filter(assessor_group=group)

        serializer = DTAssessmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @renderer_classes((JSONRenderer,))
    def create(self, request, *args, **kwargs):
        try:
            print(request.data)
            serializer = SaveAssessmentSerializer(data=request.data)
            serializer.is_valid(raise_exception = True)
            instance = serializer.save()
            instance.generate_assessment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                print e
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def remind_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.remind_assessment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def recall_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.recall_assessment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def resend_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.resend_assessment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class AssessorGroupViewSet(viewsets.ModelViewSet):
    queryset = ApplicationGroupType.objects.filter(type='assessor')
    serializer_class = ApplicationGroupTypeSerializer
    renderer_classes = [JSONRenderer,]

    def get_queryset(self):
        if is_internal(self.request):
            return ApplicationGroupType.objects.filter(type='assessor')
        elif is_customer(self.request):
            return ApplicationGroupType.objects.none()
        return ApplicationGroupType.objects.none()

    @list_route(methods=['POST',])
    def user_list(self, request, *args, **kwargs):
        app_id = request.data.get('application_id')
        application = Application.objects.get(id=app_id)
        id_list = set()
        for assessment in application.assessments:
            id_list.add(assessment.assessor_group.id)
        queryset = self.get_queryset().exclude(id__in=id_list)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class AmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = AmendmentRequest.objects.all()
    serializer_class = AmendmentRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return AmendmentRequest.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.wildlifecompliance_organisations.all()]
            user_applications = [application.id for application in Application.objects.filter(Q(org_applicant_id__in = user_orgs) | Q(proxy_applicant = user) | Q(submitter = user) )]
            return AmendmentRequest.objects.filter(Q(application_id__in = user_applications))
        return AmendmentRequest.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            # print(request.data)
            amend_data=self.request.data
            reason=amend_data.pop('reason')
            application =amend_data.pop('application')
            text=amend_data.pop('text')
            activity_type_id=amend_data.pop('activity_type_id')
            print(type(application))
            print(application)
            for item in activity_type_id:
                data={
                    'application':application,
                    'reason': reason,
                    'text':text,
                    'licence_activity_type':item
                }
                serializer = self.get_serializer(data= data)
                serializer.is_valid(raise_exception = True)
                instance = serializer.save()
                instance.reason = reason
                instance.generate_amendment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e,'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                print e
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

class AmendmentRequestReasonChoicesView(views.APIView):

    renderer_classes = [JSONRenderer,]
    def get(self,request, format=None):
        choices_list = []
        choices = AmendmentRequest.REASON_CHOICES
        if choices:
            for c in choices:
                choices_list.append({'key': c[0],'value': c[1]})

        return Response(choices_list)





