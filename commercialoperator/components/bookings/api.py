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
from commercialoperator.components.proposals.models import Proposal, ApplicationType
from commercialoperator.components.bookings.models import (
    Booking,
    ParkBooking,
    BookingInvoice,
)
from commercialoperator.components.bookings.serializers import (
    BookingSerializer,
    ParkBookingSerializer,
)
from commercialoperator.helpers import is_customer, is_internal
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from commercialoperator.components.proposals.api import ProposalFilterBackend, ProposalRenderer

class BookingPaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = Booking.objects.none()
    serializer_class = BookingSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Booking.objects.all()
#        elif is_customer(self.request):
#            user_orgs = [org.id for org in self.request.user.commercialoperator_organisations.all()]
#            queryset =  Approval.objects.filter(Q(org_applicant_id__in = user_orgs) | Q(submitter = self.request.user))
#            return queryset
        return Booking.objects.none()

#    def list(self, request, *args, **kwargs):
#        response = super(ProposalPaginatedViewSet, self).list(request, args, kwargs)
#
#        # Add extra data to response.data
#        #response.data['regions'] = self.get_queryset().filter(region__isnull=False).values_list('region__name', flat=True).distinct()
#        return response

    @list_route(methods=['GET',])
    def bookings_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)

        To test:
            http://localhost:8000/api/booking_paginated/bookings_external/?format=datatables&draw=1&length=2
        """

        qs = Booking.objects.all()
#        ids = self.get_queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number').values_list('id', flat=True)
#        qs = Approval.objects.filter(id__in=ids)
#        qs = self.filter_queryset(qs)
#
#        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
#        applicant_id = request.GET.get('org_id')
#        if applicant_id:
#            qs = qs.filter(org_applicant_id=applicant_id)
#        submitter_id = request.GET.get('submitter_id', None)
#        if submitter_id:
#            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = BookingSerializer(result_page, context={'request':request}, many=True)
        return self.paginator.get_paginated_response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.none()
    serializer_class = BookingSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Booking.objects.all()
#        elif is_customer(self.request):
#            user_orgs = [org.id for org in self.request.user.commercialoperator_organisations.all()]
#            queryset =  Approval.objects.filter(Q(org_applicant_id__in = user_orgs) | Q(submitter = request.user))
#            return queryset
        return Booking.objects.none()


class ParkBookingViewSet(viewsets.ModelViewSet):
    queryset = ParkBooking.objects.none()
    serializer_class = ParkBookingSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return ParkBooking.objects.all()
#        elif is_customer(self.request):
#            user_orgs = [org.id for org in self.request.user.commercialoperator_organisations.all()]
#            queryset =  Approval.objects.filter(Q(org_applicant_id__in = user_orgs) | Q(submitter = request.user))
#            return queryset
        return ParkBooking.objects.none()


