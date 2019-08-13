import traceback
import os
import base64
import geojson
import json
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db.models import Q, Min
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
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
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from datetime import datetime, timedelta, date
from commercialoperator.components.proposals.utils import save_proponent_data,save_assessor_data, proposal_submit
from commercialoperator.components.proposals.models import searchKeyWords, search_reference, ProposalUserAction
from commercialoperator.utils import missing_required_fields, search_tenure

from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from commercialoperator.components.main.models import Document, Region, District, Tenure, ApplicationType, RequiredDocument
from commercialoperator.components.proposals.models import (
    ProposalType,
    Proposal,
    ProposalDocument,
    Referral,
    ReferralRecipientGroup,
    QAOfficerGroup,
    QAOfficerReferral,
    ProposalRequirement,
    ProposalStandardRequirement,
    AmendmentRequest,
    AmendmentReason,
    Vehicle,
    Vessel,
    ProposalOtherDetails,
    ProposalAccreditation,
    ChecklistQuestion,
    ProposalAssessment,
    ProposalAssessmentAnswer,
    RequirementDocument,
)
from commercialoperator.components.proposals.serializers import (
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
    QAOfficerReferralSerializer,
    ReferralProposalSerializer,
    ProposalRequirementSerializer,
    ProposalStandardRequirementSerializer,
    ProposedApprovalSerializer,
    PropedDeclineSerializer,
    AmendmentRequestSerializer,
    SearchReferenceSerializer,
    SearchKeywordSerializer,
    ListProposalSerializer,
    ProposalReferralSerializer,
    AmendmentRequestDisplaySerializer,
    SaveVehicleSerializer,
    VehicleSerializer,
    VesselSerializer,
    OnHoldSerializer,
    ProposalOtherDetailsSerializer,
    SaveProposalOtherDetailsSerializer,
    ProposalParkSerializer,
    ChecklistQuestionSerializer,
    ProposalAssessmentSerializer,
    ProposalAssessmentAnswerSerializer
)
from commercialoperator.components.bookings.models import Booking, ParkBooking, BookingInvoice
from commercialoperator.components.approvals.models import Approval
from commercialoperator.components.approvals.serializers import ApprovalSerializer
from commercialoperator.components.compliances.models import Compliance
from commercialoperator.components.compliances.serializers import ComplianceSerializer
from ledger.payments.invoice.models import Invoice

from commercialoperator.helpers import is_customer, is_internal
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer
from rest_framework.filters import BaseFilterBackend
import reversion
from reversion.models import Version

import logging
logger = logging.getLogger(__name__)


class GetProposalType(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        _type = ProposalType.objects.first()
        if _type:
            serializer = ProposalTypeSerializer(_type)
            return Response(serializer.data)
        else:
            return Response({'error': 'There is currently no application type.'}, status=status.HTTP_404_NOT_FOUND)

class GetEmptyList(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        return Response([])

#class DatatablesFilterBackend(BaseFilterBackend):
#
#	def filter_queryset(self, request, queryset, view):
#		queryset = super(DatatablesFilterBackend, self).filter_queryset(request, queryset, view)
#		import ipdb; ipdb.set_trace()
#		return queryset

'''
1. internal_proposal.json
2. regions.json
3. trails.json
4. vehicles.json
5. access_types.json
6. required_documents.json
7. land_activities.json
8. vessels.json
9. marine_activities.json
10. marine_parks.json
11. accreditation_choices.json
12. licence_period_choices.json
13. global_settings.json
14. questions.json
15. amendment_request_reason_choices.json
16. contacts.json

'''
class ProposalFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        def get_choice(status, choices=Proposal.PROCESSING_STATUS_CHOICES):
            for i in choices:
                if i[1]==status:
                    return i[0]
            return None

        # on the internal dashboard, the Region filter is multi-select - have to use the custom filter below
        regions = request.GET.get('regions')
        if regions:
            if queryset.model is Proposal:
                queryset = queryset.filter(region__name__iregex=regions.replace(',', '|'))
            elif queryset.model is Referral or queryset.model is Compliance:
                queryset = queryset.filter(proposal__region__name__iregex=regions.replace(',', '|'))

        # on the internal dashboard, the Payment Status filter is a property field (not a DB field) - have to use the custom filter below
        payment_status = request.GET.get('payment_status')
        if payment_status:
            if queryset.model is ParkBooking:
                #invoice_refs = BookingInvoice.objects.all().values_list('invoice_reference', flat=True).distinct()
                #filtered_refs = [x.reference for x in Invoice.objects.filter(reference__in=invoice_refs) if x.payment_status==payment_status]
                #queryset = queryset.filter(booking__invoices__invoice_reference__in=filtered_refs)

                #[ParkBooking.objects.filter(booking__invoices__invoice_reference=x).latest('id') for x in refs if Invoice.objects.get(reference=x).payment_status==payment_status]
                #queryset = queryset.filter(booking__invoices__invoice_reference__in=filtered_refs)

                #import ipdb; ipdb.set_trace()
                refs = [i.booking.invoices.last().invoice_reference  for i in ParkBooking.objects.all() if i.booking and i.booking.invoices.last()]
                filtered_refs = [i.reference for i in Invoice.objects.filter(reference__in=refs) if i.payment_status==payment_status]
                queryset = queryset.filter(booking__invoices__invoice_reference__in=filtered_refs).distinct('id')

        park = request.GET.get('park')
        if park:
            if queryset.model is Booking:
                #import ipdb; ipdb.set_trace()
                queryset = queryset.filter(park_bookings__park__id__in=[park])




        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if queryset.model is Proposal:
            if date_from:
                queryset = queryset.filter(lodgement_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(lodgement_date__lte=date_to)
        elif queryset.model is Approval:
            if date_from:
                queryset = queryset.filter(start_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(expiry_date__lte=date_to)
        elif queryset.model is Compliance:
            if date_from:
                queryset = queryset.filter(due_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(due_date__lte=date_to)
        elif queryset.model is Referral:
            if date_from:
                queryset = queryset.filter(proposal__lodgement_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(proposal__lodgement_date__lte=date_to)
        elif queryset.model is ParkBooking:
            if date_from:
                queryset = queryset.filter(arrival__gte=date_from)

            if date_to:
                queryset = queryset.filter(arrival__lte=date_to)



        queryset = super(ProposalFilterBackend, self).filter_queryset(request, queryset, view)
        setattr(view, '_datatables_total_count', total_count)
        return queryset

class ProposalRenderer(DatatablesRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        #import ipdb; ipdb.set_trace()
        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
            data['recordsTotal'] = renderer_context['view']._datatables_total_count
            #data.pop('recordsTotal')
            #data.pop('recordsFiltered')
        return super(ProposalRenderer, self).render(data, accepted_media_type, renderer_context)



#from django.utils.decorators import method_decorator
#from django.views.decorators.cache import cache_page
class ProposalPaginatedViewSet(viewsets.ModelViewSet):
    #import ipdb; ipdb.set_trace()
    #queryset = Proposal.objects.all()
    #filter_backends = (DatatablesFilterBackend,)
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    queryset = Proposal.objects.none()
    serializer_class = ListProposalSerializer
    page_size = 10

#    @method_decorator(cache_page(60))
#    def dispatch(self, *args, **kwargs):
#        return super(ListProposalViewSet, self).dispatch(*args, **kwargs)

    @property
    def excluded_type(self):
        try:
            return ApplicationType.objects.get(name='E Class')
        except:
            return ApplicationType.objects.none()

    def get_queryset(self):
        user = self.request.user
        #import ipdb; ipdb.set_trace()
        if is_internal(self.request): #user.is_authenticated():
            qs= Proposal.objects.all().exclude(application_type=self.excluded_type)
            return qs.exclude(migrated=True)
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            qs= Proposal.objects.filter( Q(org_applicant_id__in = user_orgs) | Q(submitter = user) ).exclude(application_type=self.excluded_type)
            return qs.exclude(migrated=True)
        return Proposal.objects.none()

#    def filter_queryset(self, request, queryset, view):
#        return self.filter_backends[0]().filter_queryset(self.request, queryset, view)
        #return super(ProposalPaginatedViewSet, self).filter_queryset(request, queryset, view)

#    def list(self, request, *args, **kwargs):
#        response = super(ProposalPaginatedViewSet, self).list(request, args, kwargs)
#
#        # Add extra data to response.data
#        #response.data['regions'] = self.get_queryset().filter(region__isnull=False).values_list('region__name', flat=True).distinct()
#        return response

    @list_route(methods=['GET',])
    def proposals_internal(self, request, *args, **kwargs):
        """
        Used by the internal dashboard

        http://localhost:8499/api/proposal_paginated/proposal_paginated_internal/?format=datatables&draw=1&length=2
        """
        #import ipdb; ipdb.set_trace()
        qs = self.get_queryset()
        #qs = self.filter_queryset(self.request, qs, self)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(org_applicant_id=applicant_id)
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    @list_route(methods=['GET',])
    def referrals_internal(self, request, *args, **kwargs):
        """
        Used by the internal dashboard

        http://localhost:8499/api/proposal_paginated/referrals_internal/?format=datatables&draw=1&length=2
        """
        #import ipdb; ipdb.set_trace()
        self.serializer_class = ReferralSerializer
        #qs = Referral.objects.filter(referral=request.user) if is_internal(self.request) else Referral.objects.none()
        qs = Referral.objects.filter(referral_group__in=request.user.referralrecipientgroup_set.all()) if is_internal(self.request) else Referral.objects.none()
        #qs = self.filter_queryset(self.request, qs, self)
        qs = self.filter_queryset(qs)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = DTReferralSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)

    @list_route(methods=['GET',])
    def qaofficer_info(self, request, *args, **kwargs):
        """
        Used by the internal dashboard

        http://localhost:8499/api/proposal_paginated/qaofficer_internal/?format=datatables&draw=1&length=2
        """
        #import ipdb; ipdb.set_trace()
        qa_officers = QAOfficerGroup.objects.get(default=True).members.all().values_list('email', flat=True)
        if request.user.email in qa_officers:
            return Response({'QA_Officer': True})
        else:
            return Response({'QA_Officer': False})


    @list_route(methods=['GET',])
    def qaofficer_internal(self, request, *args, **kwargs):
        """
        Used by the internal dashboard

        http://localhost:8499/api/proposal_paginated/qaofficer_internal/?format=datatables&draw=1&length=2
        """
        #import ipdb; ipdb.set_trace()
        qa_officers = QAOfficerGroup.objects.get(default=True).members.all().values_list('email', flat=True)
        if request.user.email not in qa_officers:
            return self.paginator.get_paginated_response([])

        qs = self.get_queryset()
        qs = qs.filter(qaofficer_referrals__gt=0)
        #qs = self.filter_queryset(self.request, qs, self)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(org_applicant_id=applicant_id)
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


    @list_route(methods=['GET',])
    def proposals_external(self, request, *args, **kwargs):
        """
        Used by the external dashboard

        http://localhost:8499/api/proposal_paginated/proposal_paginated_external/?format=datatables&draw=1&length=2
        """
        qs = self.get_queryset().exclude(processing_status='discarded')
        #qs = self.filter_queryset(self.request, qs, self)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(org_applicant_id=applicant_id)
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        #import ipdb; ipdb.set_trace()
        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class VersionableModelViewSetMixin(viewsets.ModelViewSet):
    @detail_route(methods=['GET',])
    def history(self, request, *args, **kwargs):
        #import ipdb; ipdb.set_trace()
        _object = self.get_object()
        #_versions = reversion.get_for_object(_object)
        _versions = Version.objects.get_for_object(_object)

        _context = {
            'request': request
        }

        #_version_serializer = VersionSerializer(_versions, many=True, context=_context)
        _version_serializer = ProposalSerializer([v.object for v in _versions], many=True, context=_context)
        # TODO
        # check pagination
        return Response(_version_serializer.data)

class ProposalSubmitViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.none()
    serializer_class = ProposalSerializer
    lookup_field = 'id'

    @property
    def excluded_type(self):
        try:
            return ApplicationType.objects.get(name='E Class')
        except:
            return ApplicationType.objects.none()

    def get_queryset(self):
        user = self.request.user
        #import ipdb; ipdb.set_trace()
        if is_internal(self.request): #user.is_authenticated():
            return Proposal.objects.all().exclude(application_type=self.excluded_type)
            #return Proposal.objects.filter(region__isnull=False)
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            queryset =  Proposal.objects.filter( Q(org_applicant_id__in = user_orgs) | Q(submitter = user) )
            #queryset =  Proposal.objects.filter(region__isnull=False).filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
            return queryset.exclude(application_type=self.excluded_type)
        logger.warn("User is neither customer nor internal user: {} <{}>".format(user.get_full_name(), user.email))
        return Proposal.objects.none()

#    def perform_create(self, serializer):
#        serializer.partial = True
#        serializer.save(created_by=self.request.user)

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            #import ipdb; ipdb.set_trace()
            instance = self.get_object()
            #instance.submit(request,self)
            #instance.tenure = search_tenure(instance)
            #instance.save()
            serializer = self.get_serializer(instance)
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


class ProposalViewSet(viewsets.ModelViewSet):
#class ProposalViewSet(VersionableModelViewSetMixin):
    #import ipdb; ipdb.set_trace()
    #queryset = Proposal.objects.all()
    queryset = Proposal.objects.none()
    serializer_class = ProposalSerializer
    lookup_field = 'id'

    @property
    def excluded_type(self):
        try:
            return ApplicationType.objects.get(name='E Class')
        except:
            return ApplicationType.objects.none()

    def get_queryset(self):
        user = self.request.user
        #import ipdb; ipdb.set_trace()
        if is_internal(self.request): #user.is_authenticated():
            qs= Proposal.objects.all().exclude(application_type=self.excluded_type)
            return qs.exclude(migrated=True)
            #return Proposal.objects.filter(region__isnull=False)
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.commercialoperator_organisations.all()]
            queryset =  Proposal.objects.filter( Q(org_applicant_id__in = user_orgs) | Q(submitter = user) ).exclude(migrated=True)
            #queryset =  Proposal.objects.filter(region__isnull=False).filter( Q(applicant_id__in = user_orgs) | Q(submitter = user) )
            return queryset.exclude(application_type=self.excluded_type)
        logger.warn("User is neither customer nor internal user: {} <{}>".format(user.get_full_name(), user.email))
        return Proposal.objects.none()

    @list_route(methods=['GET',])
    def filter_list(self, request, *args, **kwargs):
        """ Used by the internal/external dashboard filters """
        region_qs =  self.get_queryset().filter(region__isnull=False).values_list('region__name', flat=True).distinct()
        #district_qs =  self.get_queryset().filter(district__isnull=False).values_list('district__name', flat=True).distinct()
        activity_qs =  self.get_queryset().filter(activity__isnull=False).values_list('activity', flat=True).distinct()
        submitter_qs = self.get_queryset().filter(submitter__isnull=False).distinct('submitter__email').values_list('submitter__first_name','submitter__last_name','submitter__email')
        submitters = [dict(email=i[2], search_term='{} {} ({})'.format(i[0], i[1], i[2])) for i in submitter_qs]
        data = dict(
            regions=region_qs,
            #districts=district_qs,
            activities=activity_qs,
            submitters=submitters,
            #processing_status_choices = [i[1] for i in Proposal.PROCESSING_STATUS_CHOICES],
            #processing_status_id_choices = [i[0] for i in Proposal.PROCESSING_STATUS_CHOICES],
            #customer_status_choices = [i[1] for i in Proposal.CUSTOMER_STATUS_CHOICES],
            approval_status_choices = [i[1] for i in Approval.STATUS_CHOICES],
        )
        return Response(data)

    @detail_route(methods=['GET',])
    def compare_list(self, request, *args, **kwargs):
        """ Returns the reversion-compare urls --> list"""
        current_revision_id = Version.objects.get_for_object(self.get_object()).first().revision_id
        versions = Version.objects.get_for_object(self.get_object()).select_related("revision__user").filter(Q(revision__comment__icontains='status') | Q(revision_id=current_revision_id))
        version_ids = [i.id for i in versions]
        urls = ['?version_id2={}&version_id1={}'.format(version_ids[0], version_ids[i+1]) for i in range(len(version_ids)-1)]
        return Response(urls)


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
                #instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' in request.POST and 'filename' in request.POST:
                proposal_id = request.POST.get('proposal_id')
                filename = request.POST.get('filename')
                _file = request.POST.get('_file')
                if not _file:
                    _file = request.FILES.get('_file')

                document = instance.documents.get_or_create(input_name=section, name=filename)[0]
                path = default_storage.save('{}/proposals/{}/documents/{}'.format(settings.MEDIA_APP_DIR, proposal_id, filename), ContentFile(_file.read()))

                document._file = path
                document.save()
                instance.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

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

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def process_onhold_document(self, request, *args, **kwargs):
        try:
            #import ipdb; ipdb.set_trace()
            instance = self.get_object()
            action = request.POST.get('action')
            section = request.POST.get('input_name')
            if action == 'list' and 'input_name' in request.POST:
                pass

#            elif action == 'delete' and 'document_id' in request.POST:
#                document_id = request.POST.get('document_id')
#                document = instance.onhold_documents.get(id=document_id)
#
#                if document._file and os.path.isfile(document._file.path) and document.can_delete:
#                    os.remove(document._file.path)
#
#                document.delete()
#                instance.save(version_comment='OnHold File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history
#                #instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'delete' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.onhold_documents.get(id=document_id)

                document.visible = False
                document.save()
                instance.save(version_comment='OnHold File Hidden: {}'.format(document.name)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' in request.POST and 'filename' in request.POST:
                proposal_id = request.POST.get('proposal_id')
                filename = request.POST.get('filename')
                _file = request.POST.get('_file')
                if not _file:
                    _file = request.FILES.get('_file')

                document = instance.onhold_documents.get_or_create(input_name=section, name=filename)[0]
                path = default_storage.save('{}/proposals/{}/onhold/{}'.format(settings.MEDIA_APP_DIR, proposal_id, filename), ContentFile(_file.read()))

                document._file = path
                document.save()
                instance.save(version_comment='On Hold File Added: {}'.format(filename)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return  Response( [dict(input_name=d.input_name, name=d.name,file=d._file.url, id=d.id, can_delete=d.can_delete) for d in instance.onhold_documents.filter(input_name=section, visible=True) if d._file] )

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

    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def process_qaofficer_document(self, request, *args, **kwargs):
        try:
            #import ipdb; ipdb.set_trace()
            instance = self.get_object()
            action = request.POST.get('action')
            section = request.POST.get('input_name')
            if action == 'list' and 'input_name' in request.POST:
                pass

            elif action == 'delete' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.qaofficer_documents.get(id=document_id)

                document.visible = False
                document.save()
                instance.save(version_comment='QA Officer File Hidden: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' in request.POST and 'filename' in request.POST:
                proposal_id = request.POST.get('proposal_id')
                filename = request.POST.get('filename')
                _file = request.POST.get('_file')
                if not _file:
                    _file = request.FILES.get('_file')

                document = instance.qaofficer_documents.get_or_create(input_name=section, name=filename)[0]
                path = default_storage.save('{}/proposals/{}/qaofficer/{}'.format(settings.MEDIA_APP_DIR, proposal_id, filename), ContentFile(_file.read()))

                document._file = path
                document.save()
                instance.save(version_comment='QA Officer File Added: {}'.format(filename)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return  Response( [dict(input_name=d.input_name, name=d.name,file=d._file.url, id=d.id, can_delete=d.can_delete) for d in instance.qaofficer_documents.filter(input_name=section, visible=True) if d._file] )

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


#    def list(self, request, *args, **kwargs):
#        #import ipdb; ipdb.set_trace()
#        #queryset = self.get_queryset()
#        #serializer = DTProposalSerializer(queryset, many=True)
#        #import ipdb; ipdb.set_trace()
#        #serializer = DTProposalSerializer(self.get_queryset(), many=True)
#        serializer = ListProposalSerializer(self.get_queryset(), context={'request':request}, many=True)
#        return Response(serializer.data)

    @list_route(methods=['GET',])
    def list_paginated(self, request, *args, **kwargs):
        """
        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset()
        paginator = PageNumberPagination()
        #paginator = LimitOffsetPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return paginator.get_paginated_response(serializer.data)


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
                    #import ipdb; ipdb.set_trace()
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
            #qs = instance.requirements.all()
            qs = instance.requirements.all().exclude(is_deleted=True)
            serializer = ProposalRequirementSerializer(qs,many=True, context={'request':request})
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
            serializer = AmendmentRequestDisplaySerializer(qs,many=True)
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
    def vehicles(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.vehicles
            #qs = qs.filter(status = 'requested')
            serializer = VehicleSerializer(qs,many=True)
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
    def vessels(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.vessels
            #qs = qs.filter(status = 'requested')
            serializer = VesselSerializer(qs,many=True)
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
        qs = self.get_queryset().exclude(processing_status='discarded')
        #serializer = DTProposalSerializer(qs, many=True)
        serializer = ListProposalSerializer(qs,context={'request':request}, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def user_list_paginated(self, request, *args, **kwargs):
        """
        Placing Paginator class here (instead of settings.py) allows specific method for desired behaviour),
        otherwise all serializers will use the default pagination class

        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset().exclude(processing_status='discarded')
        paginator = DatatablesPageNumberPagination()
        paginator.page_size = proposals.count()
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return paginator.get_paginated_response(serializer.data)

    @list_route(methods=['GET',])
    def list_paginated(self, request, *args, **kwargs):
        """
        Placing Paginator class here (instead of settings.py) allows specific method for desired behaviour),
        otherwise all serializers will use the default pagination class

        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
        """
        proposals = self.get_queryset()
        paginator = DatatablesPageNumberPagination()
        paginator.page_size = proposals.count()
        result_page = paginator.paginate_queryset(proposals, request)
        serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
        return paginator.get_paginated_response(serializer.data)

    #Documents on Activities(land)and Activities(Marine) tab for T-Class related to required document questions
    @detail_route(methods=['POST'])
    @renderer_classes((JSONRenderer,))
    def process_required_document(self, request, *args, **kwargs):
        try:
            #import ipdb; ipdb.set_trace()
            instance = self.get_object()
            action = request.POST.get('action')
            section = request.POST.get('input_name')
            required_doc_id=request.POST.get('required_doc_id')
            if action == 'list' and 'required_doc_id' in request.POST:
                pass

            elif action == 'delete' and 'document_id' in request.POST:
                document_id = request.POST.get('document_id')
                document = instance.required_documents.get(id=document_id)

                if document._file and os.path.isfile(document._file.path) and document.can_delete:
                    os.remove(document._file.path)

                document.delete()
                instance.save(version_comment='Required document File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Deleted: {}'.format(document.name)) # to allow revision to be added to reversion history

            elif action == 'save' and 'input_name' and 'required_doc_id' in request.POST and 'filename' in request.POST:
                proposal_id = request.POST.get('proposal_id')
                filename = request.POST.get('filename')
                _file = request.POST.get('_file')
                if not _file:
                    _file = request.FILES.get('_file')

                required_doc_instance=RequiredDocument.objects.get(id=required_doc_id)
                document = instance.required_documents.get_or_create(input_name=section, name=filename, required_doc=required_doc_instance)[0]
                path = default_storage.save('{}/proposals/{}/required_documents/{}'.format(settings.MEDIA_APP_DIR, proposal_id, filename), ContentFile(_file.read()))

                document._file = path
                document.save()
                instance.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history
                #instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

            return  Response( [dict(input_name=d.input_name, name=d.name,file=d._file.url, id=d.id, can_delete=d.can_delete) for d in instance.required_documents.filter(required_doc=required_doc_id) if d._file] )

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
    def internal_proposal(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InternalProposalSerializer(instance,context={'request':request})
        return Response(serializer.data)

    @detail_route(methods=['GET',])
    def proposal_parks(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProposalParkSerializer(instance,context={'request':request})
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
            #import ipdb; ipdb.set_trace()
            instance = self.get_object()
            #instance.submit(request,self)
            proposal_submit(instance, request)
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

#    @detail_route(methods=['post'])
#    @renderer_classes((JSONRenderer,))
#    def update_files(self, request, *args, **kwargs):
#        try:
#            #import ipdb; ipdb.set_trace()
#            instance = self.get_object()
#            instance.update(request,self)
#            instance.save()
#            serializer = self.get_serializer(instance)
#            return Response(serializer.data)
#            #return redirect(reverse('external'))
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
            approver_comment = request.data.get('approver_comment')
            if not status:
                raise serializers.ValidationError('Status is required')
            else:
                if not status in ['with_assessor','with_assessor_requirements','with_approver']:
                    raise serializers.ValidationError('The status provided is not allowed')
            instance.move_to_status(request,status, approver_comment)
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

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def on_hold(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                is_onhold =  eval(request.data.get('onhold'))
                data = {}
                if is_onhold:
                    data['type'] = u'onhold'
                    instance.on_hold(request)
                else:
                    data['type'] = u'onhold_remove'
                    instance.on_hold_remove(request)

                data['proposal'] = u'{}'.format(instance.id)
                data['staff'] = u'{}'.format(request.user.id)
                data['text'] = request.user.get_full_name() + u': {}'.format(request.data['text'])
                data['subject'] = request.user.get_full_name() + u': {}'.format(request.data['text'])
                serializer = ProposalLogEntrySerializer(data=data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()

                # save the files
                #import ipdb; ipdb.set_trace()
                documents_qs = instance.onhold_documents.filter(input_name='on_hold_file', visible=True)
                for f in documents_qs:
                    document = comms.documents.create(_file=f._file, name=f.name)
                    #document = comms.documents.create()
                    #document.name = f.name
                    #document._file = f._file #.strip('/media')
                    document.input_name = f.input_name
                    document.can_delete = True
                    document.save()
                # end save documents

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
    def with_qaofficer(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                #import ipdb; ipdb.set_trace()
                instance = self.get_object()
                is_with_qaofficer =  eval(request.data.get('with_qaofficer'))
                data = {}
                if is_with_qaofficer:
                    data['type'] = u'with_qaofficer'
                    instance.with_qaofficer(request)
                else:
                    data['type'] = u'with_qaofficer_completed'
                    instance.with_qaofficer_completed(request)

                data['proposal'] = u'{}'.format(instance.id)
                data['staff'] = u'{}'.format(request.user.id)
                data['text'] = request.user.get_full_name() + u': {}'.format(request.data['text'])
                data['subject'] = request.user.get_full_name() + u': {}'.format(request.data['text'])
                serializer = ProposalLogEntrySerializer(data=data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()

                # Save the files
                #import ipdb; ipdb.set_trace()
                document_qs=[]
                if is_with_qaofficer:
                    #Get the list of documents attached by assessor when sending application to QA officer
                    documents_qs = instance.qaofficer_documents.filter(input_name='assessor_qa_file', visible=True)
                else:
                    #Get the list of documents attached by QA officer when sending application back to assessor
                    documents_qs = instance.qaofficer_documents.filter(input_name='qaofficer_file', visible=True)
                for f in documents_qs:
                    document = comms.documents.create(_file=f._file, name=f.name)
                    #document = comms.documents.create()
                    #document.name = f.name
                    #document._file = f._file #.strip('/media')
                    document.input_name = f.input_name
                    document.can_delete = True
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

    @detail_route(methods=['post'])
    def assesor_send_referral(self, request, *args, **kwargs):
        try:
            #import ipdb; ipdb.set_trace()
            instance = self.get_object()
            serializer = SendReferralSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            #text=serializer.validated_data['text']
            #instance.send_referral(request,serializer.validated_data['email'])
            instance.send_referral(request,serializer.validated_data['email_group'], serializer.validated_data['text'])
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
            # schema=request.data.get('schema')
            # import json
            # sc=json.loads(schema)
            #import ipdb; ipdb.set_trace()
            # other_details_data=sc['other_details']
            # print other_details_data
            # serializer = ProposalOtherDetailsSerializer(instance.other_details,data=other_details_data)
            # serializer.is_valid(raise_exception=True)
            # serializer.save()
            # select_parks_activities=sc['selected_parks_activities']
            # select_trails_activities=sc['selected_trails_activities']
            # marine_parks_activities=json.loads(request.data.get('marine_parks_activities'))
            #print marine_parks_activities
            #trails=list(sc['trails'])
            save_proponent_data(instance,request,self)
            # if parks:
            #     instance.save_parks(request,parks)
            return redirect(reverse('external'))
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
                'org_applicant': request.data.get('org_applicant'),
                'application_type': application_type,
                'region': region,
                'district': district,
                'activity': activity,
                'approval_level': approval_level,
                #'other_details': {},
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
            #import ipdb; ipdb.set_trace()
            serializer.is_valid(raise_exception=True)
            #serializer.save()
            instance=serializer.save()
            #Create ProposalOtherDetails instance for T Class licence
            if application_name=='T Class':
                other_details_data={
                'proposal': instance.id
                }
                serializer=SaveProposalOtherDetailsSerializer(data=other_details_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            serializer = SaveProposalSerializer(instance)
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

    @list_route(methods=['GET',])
    def filter_list(self, request, *args, **kwargs):
        """ Used by the external dashboard filters """
        qs =  self.get_queryset().filter(referral=request.user)
        region_qs =  qs.filter(proposal__region__isnull=False).values_list('proposal__region__name', flat=True).distinct()
        #district_qs =  qs.filter(proposal__district__isnull=False).values_list('proposal__district__name', flat=True).distinct()
        activity_qs =  qs.filter(proposal__activity__isnull=False).order_by('proposal__activity').distinct('proposal__activity').values_list('proposal__activity', flat=True).distinct()
        submitter_qs = qs.filter(proposal__submitter__isnull=False).order_by('proposal__submitter').distinct('proposal__submitter').values_list('proposal__submitter__first_name','proposal__submitter__last_name','proposal__submitter__email')
        submitters = [dict(email=i[2], search_term='{} {} ({})'.format(i[0], i[1], i[2])) for i in submitter_qs]
        processing_status_qs =  qs.filter(proposal__processing_status__isnull=False).order_by('proposal__processing_status').distinct('proposal__processing_status').values_list('proposal__processing_status', flat=True)
        processing_status = [dict(value=i, name='{}'.format(' '.join(i.split('_')).capitalize())) for i in processing_status_qs]
        data = dict(
            regions=region_qs,
            #districts=district_qs,
            activities=activity_qs,
            submitters=submitters,
            processing_status_choices=processing_status,
        )
        return Response(data)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request':request})
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(referral=request.user)
        serializer = DTReferralSerializer(qs, many=True)
        #serializer = DTReferralSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def user_group_list(self, request, *args, **kwargs):
        qs = ReferralRecipientGroup.objects.filter().values_list('name', flat=True)
        return Response(qs)

    @list_route(methods=['GET',])
    def datatable_list(self, request, *args, **kwargs):
        proposal = request.GET.get('proposal',None)
        qs = self.get_queryset().all()
        if proposal:
            qs = qs.filter(proposal_id=int(proposal))
        serializer = DTReferralSerializer(qs, many=True)
        return Response(serializer.data)


    @detail_route(methods=['GET',])
    def referral_list(self, request, *args, **kwargs):
        instance = self.get_object()
        #qs = self.get_queryset().all()
        #qs=qs.filter(sent_by=instance.referral, proposal=instance.proposal)

        qs = Referral.objects.filter(referral_group__in=request.user.referralrecipientgroup_set.all(), proposal=instance.proposal)
        serializer = DTReferralSerializer(qs, many=True)
        #serializer = ProposalReferralSerializer(qs, many=True)

        return Response(serializer.data)

    @detail_route(methods=['GET', 'POST'])
    def complete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            #import ipdb; ipdb.set_trace()
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
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

class ProposalRequirementViewSet(viewsets.ModelViewSet):
    #queryset = ProposalRequirement.objects.all()
    queryset = ProposalRequirement.objects.none()
    serializer_class = ProposalRequirementSerializer

    def get_queryset(self):
        qs = ProposalRequirement.objects.all().exclude(is_deleted=True)
        return qs

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

    @detail_route(methods=['GET',])
    def discard(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
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

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def delete_document(self, request, *args, **kwargs):
        try:
            #import ipdb; ipdb.set_trace()
            instance = self.get_object()
            RequirementDocument.objects.get(id=request.data.get('id')).delete()
            return Response([dict(id=i.id, name=i.name,_file=i._file.url) for i in instance.requirement_documents.all()])
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    def update(self, request, *args, **kwargs):
        #import ipdb; ipdb.set_trace()
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=json.loads(request.data.get('data')))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instance.add_documents(request)
            return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    def create(self, request, *args, **kwargs):
        #import ipdb; ipdb.set_trace()
        try:
#            data = {
#                'due_date': request.data.get('due_date'),
#                'standard': request.data.get('standard'),
#                'recurrence': reqeust.data.get('recurrence'),
#                'recurrence_pattern': request.data.get('recurrence_pattern'),
#                'proposal': request.data.get('proposal'),
#                'referral_group': request.data.get('referral_group'),
#            }

            #serializer = self.get_serializer(data= request.data)
            serializer = self.get_serializer(data= json.loads(request.data.get('data')))
            #serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception = True)
            instance = serializer.save()
            instance.add_documents(request)
            #serializer = self.get_serializer(instance)
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
            reason_id=request.data.get('reason')
            data = {
                #'schema': qs_proposal_type.order_by('-version').first().schema,
                'text': request.data.get('text'),
                'proposal': request.data.get('proposal'),
                'reason': AmendmentReason.objects.get(id=reason_id) if reason_id else None,
            }
            serializer = self.get_serializer(data= request.data)
            #serializer = self.get_serializer(data=data)
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
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class AccreditationTypeView(views.APIView):

    renderer_classes = [JSONRenderer,]
    def get(self,request, format=None):
        choices_list = []
        #choices = ProposalOtherDetails.ACCREDITATION_TYPE_CHOICES
        choices=ProposalAccreditation.ACCREDITATION_TYPE_CHOICES
        if choices:
            for c in choices:
                choices_list.append({'key': c[0],'value': c[1]})
        return Response(choices_list)

class LicencePeriodChoicesView(views.APIView):

    renderer_classes = [JSONRenderer,]
    def get(self,request, format=None):
        choices_list = []
        choices = ProposalOtherDetails.LICENCE_PERIOD_CHOICES
        if choices:
            for c in choices:
                choices_list.append({'key': c[0],'value': c[1]})
        return Response(choices_list)


class AmendmentRequestReasonChoicesView(views.APIView):

    renderer_classes = [JSONRenderer,]
    def get(self,request, format=None):
        choices_list = []
        #choices = AmendmentRequest.REASON_CHOICES
        choices=AmendmentReason.objects.all()
        if choices:
            for c in choices:
                #choices_list.append({'key': c[0],'value': c[1]})
                choices_list.append({'key': c.id,'value': c.reason})
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

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by('id')
    serializer_class = VehicleSerializer

    @detail_route(methods=['post'])
    def edit_vehicle(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = SaveVehicleSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instance.proposal.log_user_action(ProposalUserAction.ACTION_EDIT_VEHICLE.format(instance.id),request)
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

    def create(self, request, *args, **kwargs):
        try:
            #instance = self.get_object()
            serializer = SaveVehicleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            instance.proposal.log_user_action(ProposalUserAction.ACTION_CREATE_VEHICLE.format(instance.id),request)
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

class VesselViewSet(viewsets.ModelViewSet):
    queryset = Vessel.objects.all().order_by('id')
    serializer_class = VesselSerializer

    @detail_route(methods=['post'])
    def edit_vessel(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = VesselSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instance.proposal.log_user_action(ProposalUserAction.ACTION_EDIT_VESSEL.format(instance.id),request)
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

    def create(self, request, *args, **kwargs):
        try:
            #instance = self.get_object()
            serializer = VesselSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            instance.proposal.log_user_action(ProposalUserAction.ACTION_CREATE_VESSEL.format(instance.id),request)
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

class AssessorChecklistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChecklistQuestion.objects.none()
    serializer_class = ChecklistQuestionSerializer

    def get_queryset(self):
        qs=ChecklistQuestion.objects.filter(Q(list_type = 'assessor_list')& Q(obsolete=False))
        return qs

class ProposalAssessmentViewSet(viewsets.ModelViewSet):
    #queryset = ProposalRequirement.objects.all()
    queryset = ProposalAssessment.objects.all()
    serializer_class = ProposalAssessmentSerializer

    @detail_route(methods=['post'])
    def update_assessment(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            #import ipdb; ipdb.set_trace()
            request.data['submitter']= request.user.id
            serializer = ProposalAssessmentSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            #import ipdb; ipdb.set_trace()
            checklist=request.data['checklist']
            if checklist:
                for chk in checklist:
                    try:
                        #import ipdb; ipdb.set_trace()
                        chk_instance=ProposalAssessmentAnswer.objects.get(id=chk['id'])
                        serializer_chk = ProposalAssessmentAnswerSerializer(chk_instance, data=chk)
                        serializer_chk.is_valid(raise_exception=True)
                        serializer_chk.save()
                    except:
                        raise
            #instance.proposal.log_user_action(ProposalUserAction.ACTION_EDIT_VESSEL.format(instance.id),request)
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
