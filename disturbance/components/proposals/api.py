import traceback
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
from ledger.accounts.models import EmailUser, Address, Document
from ledger.address.models import Country
from disturbance import utils
from datetime import datetime, timedelta, date
from disturbance.utils import create_data_from_form
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from disturbance.components.proposals.models import (
    ProposalType,
    Proposal
)

from disturbance.components.proposals.serializers import (
    ProposalTypeSerializer,
    ProposalSerializer,
    InternalProposalSerializer,
    SaveProposalSerializer,
    DTProposalSerializer
)


class GetProposalType(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        _type = ProposalType.objects.first()
        if _type:
            serializer = ProposalTypeSerializer(_type)
            return Response(serializer.data)
        else:
            return Response({'error': 'There is currently no proposal type.'}, status=status.HTTP_404_NOT_FOUND)


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset() 
        serializer = DTProposalSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        user_orgs = [org.id for org in request.user.disturbance_organisations.all()];
        qs = []
        qs.extend(list(self.get_queryset().filter(submitter = request.user).exclude(processing_status='discarded').exclude(processing_status=Proposal.PROCESSING_STATUS_CHOICES[0][0])))
        qs.extend(list(self.get_queryset().filter(applicant_id__in = user_orgs).exclude(processing_status='discarded').exclude(processing_status=Proposal.PROCESSING_STATUS_CHOICES[0][0])))
        queryset = list(set(qs))
        serializer = DTProposalSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET',])
    def internal_proposal(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InternalProposalSerializer(instance)
        return Response(serializer.data)

    @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def draft(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            lookable_fields = ['isTitleColumnForDashboard','isActivityColumnForDashboard','isRegionColumnForDashboard']
            extracted_fields,special_fields = create_data_from_form(
                instance.schema, request.POST, request.FILES,special_fields=lookable_fields)
            instance.data = extracted_fields
            data = {
                'region': special_fields.get('isRegionColumnForDashboard',None),
                'title': special_fields.get('isTitleColumnForDashboard',None),
                'activity': special_fields.get('isActivityColumnForDashboard',None),
                'data': extracted_fields,
                'processing_status': instance.PROCESSING_STATUS_CHOICES[1][0],
                'submitter': request.user.id,
            }
            serializer = SaveProposalSerializer(instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
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
        try:
            http_status = status.HTTP_200_OK
            data = {
                'schema': ProposalType.objects.first().schema,
                'submitter': request.user.id,
                'applicant': request.data.get('behalf_of')
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
            serializer = self.get_serializer(instance,{'processing_status':'discarded'},partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data,status=http_status)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
