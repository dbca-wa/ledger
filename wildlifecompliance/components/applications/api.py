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
from django.core.exceptions import ValidationError
from django.conf import settings
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
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from wildlifecompliance.components.applications.utils import save_proponent_data,save_assessor_data,get_activity_type_schema
from wildlifecompliance.components.main.models import Document
from wildlifecompliance.components.main.utils import checkout, set_session_application, delete_session_application
from wildlifecompliance.components.applications.models import (
    ApplicationType,
    Application,
    ApplicationDocument,
    Referral,
    ApplicationCondition,
    ApplicationStandardCondition,
    Assessment,
    ApplicationGroupType,
    AmendmentRequest
)
from wildlifecompliance.components.applications.serializers import (
    SendReferralSerializer,
    ApplicationTypeSerializer,
    ApplicationSerializer,
    InternalApplicationSerializer,
    SaveApplicationSerializer,
    DTApplicationSerializer,
    ApplicationUserActionSerializer,
    ApplicationLogEntrySerializer,
    DTReferralSerializer,
    ReferralSerializer,
    ReferralApplicationSerializer,
    ApplicationConditionSerializer,
    ApplicationStandardConditionSerializer,
    ProposedLicenceSerializer,
    PropedDeclineSerializer,
    AssessmentSerializer,
    ApplicationGroupTypeSerializer,
    SaveAssessmentSerializer,
    AmendmentRequestSerializer,
    ExternalAmendmentRequestSerializer
    
)


class GetApplicationType(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        _type = ApplicationType.objects.first()
        if _type:
            serializer = ApplicationTypeSerializer(_type)
            return Response(serializer.data)
        else:
            return Response({'error': 'There is currently no application type.'}, status=status.HTTP_404_NOT_FOUND)

class GetEmptyList(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        return Response([])

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset() 
        serializer = DTApplicationSerializer(queryset, many=True)
        return Response(serializer.data)


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
    def user_list(self, request, *args, **kwargs):
        user_orgs = [org.id for org in request.user.wildlifecompliance_organisations.all()];
        qs = []
        qs.extend(list(self.get_queryset().filter(submitter = request.user).exclude(processing_status='discarded').exclude(processing_status=Application.PROCESSING_STATUS_CHOICES[13][0])))
        qs.extend(list(self.get_queryset().filter(org_applicant_id__in = user_orgs).exclude(processing_status='discarded').exclude(processing_status=Application.PROCESSING_STATUS_CHOICES[13][0])))
        queryset = list(set(qs))
        serializer = DTApplicationSerializer(queryset, many=True)
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
            instance = self.get_object()
            instance.submit(request,self)
            serializer = self.get_serializer(instance)
            print(instance.submitter.first_name)
            print(instance.submitter.last_name)
            print(instance.id)
            print(instance.application_fee)
            # raise Exception
            # send to checkout if application_fee > 0
            if instance.application_fee > 0:
                application_submission = u'Application submitted by {} confirmation WC{}'.format(
                    u'{} {}'.format(instance.submitter.first_name, instance.submitter.last_name), instance.id)
                print(' --- set session application --- ')
                print(request.session)
                set_session_application(request.session, instance)
                print(request.session)
                checkout_result = checkout(request, instance, invoice_text=application_submission)
                print(' ---- checkout_result ---- ')
                print(checkout_result)
            # return checkout_result
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
    def switch_status(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            status = request.data.get('status')
            if not status:
                raise serializers.ValidationError('Status is required')
            else:
                if not status in ['with_assessor','with_assessor_conditions','with_approver']:
                    raise serializers.ValidationError('The status provided is not allowed')
            instance.move_to_status(request,status)
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

    @detail_route(methods=['POST',])
    def final_licence(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedLicenceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.final_licence(request,serializer.validated_data)
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
            serializer = PropedDeclineSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # print(serializer.validated_data)
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


    @detail_route(methods=['POST',])
    def final_decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PropedDeclineSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.final_decline(request,serializer.validated_data)
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
    def assesor_send_referral(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SendReferralSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.send_referral(request,serializer.validated_data['email'])
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
            application_fee = request.data.get('application_fee')
            data = {
                'schema':schema_data,
                'submitter': request.user.id,
                'licence_type_data':licence_class_data,
                'licence_type_name': licence_type_name,
                'org_applicant': org_applicant,
                'application_fee': application_fee
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


class ReferralViewSet(viewsets.ModelViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request':request})
        return Response(serializer.data) 

    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(referral=request.user)
        serializer = DTReferralSerializer(qs, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def datatable_list(self, request, *args, **kwargs):
        application = request.GET.get('application',None)
        qs = self.get_queryset().all()
        if application:
            qs = qs.filter(application_id=int(application))
        serializer = DTReferralSerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET',])
    def complete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.complete(request)
            serializer = self.get_serializer(instance, context={'request':request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def remind(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.remind(request)
            serializer = InternalApplicationSerializer(instance.application,context={'request':request})
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
    def recall(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.recall(request)
            serializer = InternalApplicationSerializer(instance.application,context={'request':request})
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
    def resend(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.resend(request)
            serializer = InternalApplicationSerializer(instance.application,context={'request':request})
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

    @detail_route(methods=['post'])
    def send_referral(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SendReferralSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.send_referral(request,serializer.validated_data['email'])
            serializer = self.get_serializer(instance, context={'request':request})
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

class ApplicationConditionViewSet(viewsets.ModelViewSet):
    queryset = ApplicationCondition.objects.all()
    serializer_class = ApplicationConditionSerializer

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
    queryset = ApplicationGroupType.objects.all()
    serializer_class = ApplicationGroupTypeSerializer

    renderer_classes = [JSONRenderer,]
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(name='Assessor')
            # serializer = self.get_serializer(qs, many=True)
        print(qs)
        return qs

class AmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = AmendmentRequest.objects.all()
    serializer_class = AmendmentRequestSerializer

    def create(self, request, *args, **kwargs):
        try:
            # print(request.data)
            serializer = self.get_serializer(data= request.data)
            serializer.is_valid(raise_exception = True)
            instance = serializer.save()
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

    

    

