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
from rest_framework.decorators import detail_route, list_route, renderer_classes
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
from disturbance.components.approvals.models import (
    Approval
)
from disturbance.components.approvals.serializers import (
    ApprovalSerializer,
    ApprovalCancellationSerializer,
    ApprovalSuspensionSerializer,
    ApprovalSurrenderSerializer,
    ApprovalUserActionSerializer,
    ApprovalLogEntrySerializer
)
from disturbance.helpers import is_customer, is_internal
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from disturbance.components.proposals.api import ProposalFilterBackend, ProposalRenderer

class ApprovalPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = Approval.objects.none()
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Approval.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            queryset =  Approval.objects.filter(applicant_id__in = user_orgs)
            return queryset
        return Approval.objects.none()

#    def list(self, request, *args, **kwargs):
#        response = super(ProposalPaginatedViewSet, self).list(request, args, kwargs)
#
#        # Add extra data to response.data
#        #response.data['regions'] = self.get_queryset().filter(region__isnull=False).values_list('region__name', flat=True).distinct()
#        return response

    @list_route(methods=['GET',])
    def approvals_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)

        To test:
            http://localhost:8000/api/approval_paginated/approvals_external/?format=datatables&draw=1&length=2
        """

        #import ipdb; ipdb.set_trace()
        #qs = self.queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
        #qs = ProposalFilterBackend().filter_queryset(self.request, qs, self)

        ids = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number').values_list('id', flat=True)
        qs = Approval.objects.filter(id__in=ids)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get('org_id')
        if applicant_id:
            qs = qs.filter(applicant_id=applicant_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ApprovalSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class ApprovalViewSet(viewsets.ModelViewSet):
    #queryset = Approval.objects.all()
    queryset = Approval.objects.none()
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Approval.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in self.request.user.disturbance_organisations.all()]
            queryset =  Approval.objects.filter(applicant_id__in = user_orgs)
            return queryset
        return Approval.objects.none()

    def list(self, request, *args, **kwargs):
        #queryset = self.get_queryset()
        queryset = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
        # Filter by org
        org_id = request.GET.get('org_id',None)
        if org_id:
            queryset = queryset.filter(applicant_id=org_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def filter_list(self, request, *args, **kwargs):
        """ Used by the external dashboard filters """
        #import ipdb; ipdb.set_trace()
        region_qs =  self.get_queryset().filter(current_proposal__region__isnull=False).values_list('current_proposal__region__name', flat=True).distinct()
        activity_qs =  self.get_queryset().filter(current_proposal__activity__isnull=False).values_list('current_proposal__activity', flat=True).distinct()
        data = dict(
            regions=region_qs,
            activities=activity_qs,
            approval_status_choices = [i[1] for i in Approval.STATUS_CHOICES],
        )
        return Response(data)


#    @list_route(methods=['GET',])
#    def approvals_paginated(self, request, *args, **kwargs):
#        """
#        Paginated serializer for datatables - used by the external dashboard
#
#		To test:
#        	http://localhost:8000/api/approvals/approvals_paginated/?format=datatables&draw=1&length=2
#        """
#
#        #import ipdb; ipdb.set_trace()
#        qs = self.get_queryset().order_by('lodgement_number', '-issue_date')
#        qs = ProposalFilterBackend().filter_queryset(self.request, qs, self)
#        #qs = qs.order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
#
#        self.renderer_classes = (ProposalRenderer,)
#        paginator = DatatablesPageNumberPagination()
#        paginator.page_size = qs.count()
#        result_page = paginator.paginate_queryset(qs, request)
#        serializer = ApprovalSerializer(result_page, context={'request':request}, many=True)
#        return paginator.get_paginated_response(serializer.data)


#    @list_route(methods=['GET',])
#    def user_list(self, request, *args, **kwargs):
#        user_orgs = [org.id for org in request.user.disturbance_organisations.all()];
#        qs = []
#        #qs.extend(list(self.get_queryset().filter(submitter = request.user).exclude(processing_status='discarded').exclude(processing_status=Proposal.PROCESSING_STATUS_CHOICES[13][0])))
#        #qs.extend(list(self.get_queryset().filter(applicant_id__in = user_orgs)))
#        qset = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
#        qs.extend(list(qset.filter(applicant_id__in = user_orgs)))
#        queryset = list(set(qs))
#        serializer = self.get_serializer(queryset, many=True)
#        return Response(serializer.data)

#    @list_route(methods=['GET',])
#    def user_list(self, request, *args, **kwargs):
#        queryset = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
#        serializer = self.get_serializer(queryset, many=True)
#        return Response(serializer.data)

#    @list_route(methods=['GET',])
#    def user_list_paginated(self, request, *args, **kwargs):
#        """
#        Placing Paginator class here (instead of settings.py) allows specific method for desired behaviour),
#        otherwise all serializers will use the default pagination class
#
#        https://stackoverflow.com/questions/29128225/django-rest-framework-3-1-breaks-pagination-paginationserializer
#        """
#        queryset = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
#        paginator = DatatablesPageNumberPagination()
#        paginator.page_size = queryset.count()
#        result_page = paginator.paginate_queryset(queryset, request)
#        #serializer = ListProposalSerializer(result_page, context={'request':request}, many=True)
#        serializer = self.get_serializer(result_page, context={'request':request}, many=True)
#        return paginator.get_paginated_response(serializer.data)



    @detail_route(methods=['POST',])
    def approval_cancellation(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalCancellationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_cancellation(request,serializer.validated_data)
            serializer = ApprovalSerializer(instance,context={'request':request})
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
    def approval_suspension(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalSuspensionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_suspension(request,serializer.validated_data)
            serializer = ApprovalSerializer(instance,context={'request':request})
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
    def approval_reinstate(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.reinstate_approval(request)
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

    @detail_route(methods=['POST',])
    def approval_surrender(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalSurrenderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_surrender(request,serializer.validated_data)
            serializer = ApprovalSerializer(instance,context={'request':request})
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
    def approval_pdf_view_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.pdf_view_log(request)
            serializer = ApprovalSerializer(instance,context={'request':request})
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
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ApprovalUserActionSerializer(qs,many=True)
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
            serializer = ApprovalLogEntrySerializer(qs,many=True)
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
                request.data['approval'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = ApprovalLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                import ipdb; ipdb.set_trace()
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

    @list_route(methods=['GET',])
    def sti_search(self, request, *args, **kwargs):
        """ Used by the internal users to filter for sti name in ptoposal titlei (for use by external systems) """
        #import ipdb; ipdb.set_trace()
        name = request.GET.get('name')
        data = Approval.objects.filter(current_proposal__title__icontains=name).values_list('licence_document___file', flat=True)
        return Response(list(data))

    @list_route(methods=['GET',])
    def sti_unmatched(self, request, *args, **kwargs):
        """ Used by the internal users to filter for sti name in ptoposal titlei (for use by external systems) """
        import ipdb; ipdb.set_trace()
        name = request.GET.get('name')
        data = Approval.objects.filter(current_proposal__title__icontains=name).values_list('licence_document___file', flat=True)


        #qs = User.objects.all()
        #for search_term in ['x', 'y', 'z']:
        #    qs = qs.filter(first_name__contains=search_term)

        return Response(list(data))
