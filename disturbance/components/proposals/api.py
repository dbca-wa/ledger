import traceback
import os
import datetime
import base64
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
from disturbance.components.proposals.utils import save_proponent_data,save_assessor_data
from disturbance.components.proposals.models import searchKeyWords, search_reference, ProposalUserAction
from disturbance.utils import missing_required_fields, search_tenure

from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from disturbance.components.main.models import Document, Region, District, Tenure, ApplicationType
from disturbance.components.proposals.models import (
    ProposalType,
    Proposal,
    ProposalDocument,
    Referral,
    ProposalRequirement,
    ProposalStandardRequirement,
    AmendmentRequest,

)
from disturbance.components.proposals.serializers import (
    SendReferralSerializer,
    ProposalTypeSerializer,
    ProposalSerializer,
    InternalProposalSerializer,
    SaveProposalSerializer,
    DTProposalSerializer,
    ProposalUserActionSerializer,
    ProposalLogEntrySerializer,
    DTReferralSerializer,
    ReferralSerializer,
    ReferralProposalSerializer,
    ProposalRequirementSerializer,
    ProposalStandardRequirementSerializer,
    ProposedApprovalSerializer,
    PropedDeclineSerializer,
    AmendmentRequestSerializer,
    SearchReferenceSerializer,
    SearchKeywordSerializer,
    ListProposalSerializer
)
from disturbance.helpers import is_customer, is_internal


class GetProposalType(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        _type = ProposalType.objects.first()
        if _type:
            serializer = ProposalTypeSerializer(_type)
            return Response(serializer.data)
        else:
            return Response({'error': 'There is currently no proposal type.'}, status=status.HTTP_404_NOT_FOUND)

class GetEmptyList(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        return Response([])

class ProposalViewSet(viewsets.ModelViewSet):
    #import ipdb; ipdb.set_trace()
    #queryset = Proposal.objects.all()
    queryset = Proposal.objects.none()
    serializer_class = ProposalSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request): #user.is_authenticated():
            return Proposal.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            queryset =  Proposal.objects.filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
            return queryset
        return Proposal.objects.none()



    def list(self, request, *args, **kwargs):
        #import ipdb; ipdb.set_trace()
        #queryset = self.get_queryset()
        #serializer = DTProposalSerializer(queryset, many=True)
        #import ipdb; ipdb.set_trace()
        #serializer = DTProposalSerializer(self.get_queryset(), many=True)
        serializer = ListProposalSerializer(self.get_queryset(), context={'request':request}, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET',])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ProposalUserActionSerializer(qs,many=True)
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
            serializer = ProposalLogEntrySerializer(qs,many=True)
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
                request.data['proposal'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = ProposalLogEntrySerializer(data=request.data)
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
    def requirements(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.requirements.all()
            serializer = ProposalRequirementSerializer(qs,many=True)
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
            serializer = AmendmentRequestSerializer(qs,many=True)
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



#    @list_route(methods=['GET',])
#    def user_list(self, request, *args, **kwargs):
#        user_orgs = [org.id for org in request.user.disturbance_organisations.all()];
#        qs = []
#        qs.extend(list(self.get_queryset().filter(submitter = request.user).exclude(processing_status='discarded')))
#        #Remove filter to include 'Apporved Proposals in external dashboard .exclude(processing_status=Proposal.PROCESSING_STATUS_CHOICES[13][0])
#        qs.extend(list(self.get_queryset().filter(applicant_id__in = user_orgs).exclude(processing_status='discarded')))
#        #Remove filter to include 'Apporved Proposals in external dashboard .exclude(processing_status=Proposal.PROCESSING_STATUS_CHOICES[13][0])
#        queryset = list(set(qs))
#        serializer = DTProposalSerializer(queryset, many=True)
#        return Response(serializer.data)


    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        qs = self.get_queryset().exclude(processing_status='discarded')
        #serializer = DTProposalSerializer(qs, many=True)
        serializer = ListProposalSerializer(qs,context={'request':request}, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET',])
    def internal_proposal(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InternalProposalSerializer(instance,context={'request':request})
        return Response(serializer.data)

#    @detail_route(methods=['post'])
#    @renderer_classes((JSONRenderer,))
#    def _submit(self, request, *args, **kwargs):
#        try:
#            #import ipdb; ipdb.set_trace()
#            instance = self.get_object()
#            save_proponent_data(instance,request,self)
#            missing_fields = missing_required_fields(instance)
#
#            if False: #missing_fields:
#            #if missing_fields:
#                return Response({'missing_fields': missing_fields})
#            else:
#                #raise serializers.ValidationError(repr({'abcde': 123, 'missing_fields':True}))
#                instance.submit(request,self)
#                serializer = self.get_serializer(instance)
#                #import ipdb; ipdb.set_trace()
#                return Response(serializer.data)
#        except serializers.ValidationError:
#            print(traceback.print_exc())
#            raise
#        except ValidationError as e:
#            if hasattr(e,'error_dict'):
#                raise serializers.ValidationError(repr(e.error_dict))
#            else:
#                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
#        except Exception as e:
#            print(traceback.print_exc())
#            raise serializers.ValidationError(str(e))


    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.submit(request,self)
            instance.tenure = search_tenure(instance)
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
            #return redirect(reverse('external'))
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
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_officer(request,request.user)
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
                if not status in ['with_assessor','with_assessor_requirements','with_approver']:
                    raise serializers.ValidationError('The status provided is not allowed')
            instance.move_to_status(request,status)
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
    def reissue_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            status = request.data.get('status')
            if not status:
                raise serializers.ValidationError('Status is required')
            else:
                if not status in ['with_approver']:
                    raise serializers.ValidationError('The status provided is not allowed')
            instance.reissue_approval(request,status)
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
    def renew_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.renew_approval(request)
            serializer = SaveProposalSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e[0].encode('utf-8')))

    @detail_route(methods=['GET',])
    def amend_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.amend_approval(request)
            serializer = SaveProposalSerializer(instance,context={'request':request})
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e[0].encode('utf-8')))


    @detail_route(methods=['POST',])
    def proposed_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedApprovalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.proposed_approval(request,serializer.validated_data)
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
    def approval_level_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance = instance.assing_approval_level_document(request)
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
    def final_approval(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ProposedApprovalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.final_approval(request,serializer.validated_data)
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
            instance.proposed_decline(request,serializer.validated_data)
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
            serializer = InternalProposalSerializer(instance,context={'request':request})
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
            #text=serializer.validated_data['text']
            #instance.send_referral(request,serializer.validated_data['email'])
            instance.send_referral(request,serializer.validated_data['email'], serializer.validated_data['text'])
            serializer = InternalProposalSerializer(instance,context={'request':request})
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

#    @detail_route(methods=['post'])
#    @renderer_classes((JSONRenderer,))
#    def save_section(self, request, *args, **kwargs):
#        try:
#            instance = self.get_object()
#            save_proponent_data(instance,request,self)
#            return redirect(reverse('external'))
#        except serializers.ValidationError:
#            print(traceback.print_exc())
#            raise
#        except ValidationError as e:
#            raise serializers.ValidationError(repr(e.error_dict))
#        except Exception as e:
#            print(traceback.print_exc())
#        raise serializers.ValidationError(str(e))
#
#
#    @detail_route(methods=['post'])
#    def _save_section(self, request, *args, **kwargs):
#        import ipdb; ipdb.set_trace()
#        try:
#            instance = self.get_object()
#
#            if request.data.has_key('upload_file'):
#                parent_section = request.data.get('upload_file')['parent_section']
#                section = request.data.get('upload_file')['section']
#                filename = request.data.get('upload_file')['filename']
#                if isinstance(instance.data, list) and instance.data[0].has_key(parent_section): #  parent_section in instance.data[0]['proposalSummarySection'][0]:
#                    if isinstance(instance.data[0].get(parent_section), list):
#                        instance.data[0][parent_section][0][section] = filename
#                    else:
#                        instance.data[0][parent_section] = [{section: filename}]
#                else:
#                    if isinstance(instance.data, list):
#                        instance.data.append( {parent_section: [{section: filename}]} )
#                    else:
#                        # instance.data == None
#                        instance.data = [ {parent_section: [{section: filename}]} ]
#                instance.save()
#                return redirect(reverse('external'))
#
#
#            elif request.data.has_key('delete_file'):
#                # TODO currently assumes only one file in instance.data section
#                parent_section = request.data.get('upload_file')['parent_section']
#                section = request.data.get('delete_file')['section']
#                filename = request.data.get('delete_file')['filename']
#                #if section in instance.data[0]['proposalSummarySection'][0]:
#                #    instance.data[0]['proposalSummarySection'][0][section] = ''
#                if section in instance.data[0][parent_section][0]:
#                    instance.data[0][parent_section][0][section] = ''
#                    instance.save()
#                    return redirect(reverse('external'))
#
#
#            return redirect(reverse('external'))
#        except serializers.ValidationError:

#            print(traceback.print_exc())
#            raise
#        except ValidationError as e:
#            raise serializers.ValidationError(repr(e.error_dict))
#        except Exception as e:
#            print(traceback.print_exc())
#        raise serializers.ValidationError(str(e))


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

    def create(self, request, *args, **kwargs):
        #import ipdb; ipdb.set_trace()
        try:
            http_status = status.HTTP_200_OK
            application_type = request.data.get('application')
            region = request.data.get('region')
            district = request.data.get('district')
            #tenure = request.data.get('tenure') 
            activity = request.data.get('activity')
            sub_activity1 = request.data.get('sub_activity1')
            sub_activity2 = request.data.get('sub_activity2')
            category = request.data.get('category')
            approval_level = request.data.get('approval_level')

            application_name = ApplicationType.objects.get(id=application_type).name
            # Get most recent versions of the Proposal Types
            qs_proposal_type = ProposalType.objects.all().order_by('name', '-version').distinct('name')
            proposal_type = qs_proposal_type.get(name=application_name)


            data = {
                #'schema': qs_proposal_type.order_by('-version').first().schema,
                'schema': proposal_type.schema,
                'submitter': request.user.id,
                'applicant': request.data.get('behalf_of'),
                'application_type': application_type,
                'region': region,
                'district': district,
                'activity': activity,
                'approval_level': approval_level,
                #'tenure': tenure,
                'data': [
                    {
                        u'regionActivitySection': [{
                            'Region': Region.objects.get(id=region).name if region else None,
                            'District': District.objects.get(id=district).name if district else None,
                            #'Tenure': Tenure.objects.get(id=tenure).name if tenure else None,
                            #'ApplicationType': ApplicationType.objects.get(id=application_type).name
                            'ActivityType': activity,
                            'Sub-activity level 1': sub_activity1,
                            'Sub-activity level 2': sub_activity2,
                            'Management area': category,
                        }]
                    }

                ],
            }
            serializer = SaveProposalSerializer(data=data)
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
            serializer = SaveProposalSerializer(instance,data=request.data)
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
            serializer = SaveProposalSerializer(instance,{'processing_status':'discarded', 'previous_application': None},partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data,status=http_status)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

class ReferralViewSet(viewsets.ModelViewSet):
    #queryset = Referral.objects.all()
    queryset = Referral.objects.none()
    serializer_class = ReferralSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated() and is_internal(self.request):
            #queryset =  Referral.objects.filter(referral=user)
            queryset =  Referral.objects.all()
            return queryset
        return Referral.objects.none()


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request':request})
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        #qs = self.get_queryset().filter(referral=request.user)
        #serializer = DTReferralSerializer(qs, many=True)
        serializer = DTReferralSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def datatable_list(self, request, *args, **kwargs):
        proposal = request.GET.get('proposal',None)
        qs = self.get_queryset().all()
        if proposal:
            qs = qs.filter(proposal_id=int(proposal))
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
            serializer = InternalProposalSerializer(instance.proposal,context={'request':request})
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
            serializer = InternalProposalSerializer(instance.proposal,context={'request':request})
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
            serializer = InternalProposalSerializer(instance.proposal,context={'request':request})
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
            instance.send_referral(request,serializer.validated_data['email'],serializer.validated_data['text'])
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

class ProposalRequirementViewSet(viewsets.ModelViewSet):
    queryset = ProposalRequirement.objects.all()
    serializer_class = ProposalRequirementSerializer

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

class ProposalStandardRequirementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProposalStandardRequirement.objects.all()
    serializer_class = ProposalStandardRequirementSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = AmendmentRequest.objects.all()
    serializer_class = AmendmentRequestSerializer

    def create(self, request, *args, **kwargs):
        try:
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

class SearchKeywordsView(views.APIView):
    renderer_classes = [JSONRenderer,]
    def post(self,request, format=None):
        qs = []
        searchWords = request.data.get('searchKeywords')
        searchProposal = request.data.get('searchProposal')
        searchApproval = request.data.get('searchApproval')
        searchCompliance = request.data.get('searchCompliance')
        if searchWords:
            qs= searchKeyWords(searchWords, searchProposal, searchApproval, searchCompliance)
        #queryset = list(set(qs))
        serializer = SearchKeywordSerializer(qs, many=True)
        return Response(serializer.data)

class SearchReferenceView(views.APIView):
    renderer_classes = [JSONRenderer,]
    def post(self,request, format=None):
        try:
            qs = []
            reference_number = request.data.get('reference_number')
            if reference_number:
                qs= search_reference(reference_number)
            #queryset = list(set(qs))
            serializer = SearchReferenceSerializer(qs)
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


