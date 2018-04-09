
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
from disturbance.components.compliances.models import (
   Compliance 
)
from disturbance.components.compliances.serializers import (
    ComplianceSerializer,
    SaveComplianceSerializer
)


class ComplianceViewSet(viewsets.ModelViewSet):
    serializer_class = ComplianceSerializer
    queryset = Compliance.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset() 
        # Filter by org
        org_id = request.GET.get('org_id',None)
        if org_id:
            queryset = queryset.filter(proposal__applicant_id=org_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        user_orgs = [org.id for org in request.user.disturbance_organisations.all()];
        qs = []
        qs.extend(list(self.get_queryset().filter(proposal__submitter = request.user).exclude(processing_status='approved')))
        #Remove filter to include 'Apporved Proposals in external dashboard .exclude(processing_status=Proposal.PROCESSING_STATUS_CHOICES[13][0])
        qs.extend(list(self.get_queryset().filter(proposal__applicant_id__in= user_orgs).exclude(processing_status='approved')))
        #Remove filter to include 'Apporved Proposals in external dashboard .exclude(processing_status=Proposal.PROCESSING_STATUS_CHOICES[13][0])
        queryset = list(set(qs))
        serializer = ComplianceSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            with transaction.atomic():  
                instance = self.get_object()          
                data = {
                'text': request.data.get('detail')
                }
                serializer = SaveComplianceSerializer(instance, data=data)               
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                instance.submit(request)
                serializer = self.get_serializer(instance)              
                # Save the files
                for f in request.FILES:
                    document = instance.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents'''
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