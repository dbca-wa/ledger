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
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.licences.models import (
    WildlifeLicence,
    LicenceCategory
)
from wildlifecompliance.components.licences.serializers import (
    WildlifeLicenceSerializer,
    LicenceCategorySerializer
)


class LicenceViewSet(viewsets.ModelViewSet):
    queryset = WildlifeLicence.objects.all()
    serializer_class = WildlifeLicenceSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return WildlifeLicence.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            return WildlifeLicence.objects.filter(
                Q(current_application__org_applicant_id__in=user_orgs) |
                Q(current_application__proxy_applicant=user) |
                Q(current_application__submitter=user)
            )
        return WildlifeLicence.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get('org_id', None)
        if org_id:
            queryset = queryset.filter(current_application__org_applicant_id=org_id)
        # Filter by proxy_applicant
        proxy_applicant_id = request.GET.get('proxy_applicant_id', None)
        if proxy_applicant_id:
            queryset = queryset.filter(current_application__proxy_applicant_id=proxy_applicant_id)
        # Filter by submitter
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            queryset = queryset.filter(current_application__submitter_id=submitter_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET', ])
    def user_list(self, request, *args, **kwargs):
        user_orgs = [
            org.id for org in request.user.wildlifecompliance_organisations.all()]
        qs = []
        qs.extend(list(self.get_queryset().filter(current_application__submitter=request.user)))
        qs.extend(
            list(
                self.get_queryset().filter(
                    current_application__proxy_applicant=request.user)))
        qs.extend(
            list(
                self.get_queryset().filter(
                    current_application__org_applicant_id__in=user_orgs)))
        queryset = list(set(qs))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LicenceCategoryViewSet(viewsets.ModelViewSet):
    queryset = LicenceCategory.objects.all()
    serializer_class = LicenceCategorySerializer


class UserAvailableWildlifeLicencePurposesViewSet(viewsets.ModelViewSet):
    # Filters to only return purposes that are
    # available for selection when applying for
    # a new application
    queryset = LicenceCategory.objects.all()
    serializer_class = LicenceCategorySerializer

    def list(self, request, *args, **kwargs):
        print(self.request)
        print(self.request.GET)
        print(self.request.GET.get('org_applicant', None))
        queryset = self.get_queryset()
        serializer = LicenceCategorySerializer(queryset, many=True, context={'request':request})
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super(UserAvailableWildlifeLicencePurposesViewSet, self).get_serializer_context()
        context.update({
            "test": 'test context'
        })
        return context
