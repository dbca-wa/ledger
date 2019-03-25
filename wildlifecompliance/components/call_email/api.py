import traceback
import base64
import geojson
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
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.call_email.models import CallEmail, Classification
from wildlifecompliance.components.call_email.serializers import CallEmailSerializer, ClassificationSerializer


class CallEmailViewSet(viewsets.ModelViewSet):
    queryset = CallEmail.objects.all()
    serializer_class = CallEmailSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return CallEmail.objects.all()
        return CallEmail.objects.none()

    @list_route(methods=['GET', ])
    def datatable_list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = CallEmailSerializer(
                qs, many=True, context={'request': request})
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

    # @detail_route(methods=['post'])
    @renderer_classes((JSONRenderer,))
    def call_email_save(self, request, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        try:
            app_data = self.request.data
            print(app_data)
            if app_data.get('create_type') != 'call_email':
                raise serializers.ValidationError('ERROR: Not type call_email')
            else:
                print(type(self))
                print(app_data.get('status'))
                print(app_data.get('classification'))
                print(app_data.get('number'))
                print(app_data.get('caller'))
                print(app_data.get('assigned_to'))
                # CallEmail.objects.create(status=app_data.get('status'), 
                        # classification=(Classification.objects.filter(name=app_data.get('classification'))[0]),
                        # number=app_data.get('number'),
                        # caller=app_data.get('caller'),
                        # assigned_to=app_data.get('assigned_to')
                        #)
        
        except Exception as e:
                print(traceback.print_exc())
                raise serializers.ValidationError(str(e))

    def create(self, request, *args, **kwargs):
        print(request.data)
        req_data = {
                "status": request.data.get('status'),
                "classification": {
                    "name": request.data.get('classification')
                    },
                "lodgement_date": None,
                "number": request.data.get('number'),
                "caller": request.data.get('caller'),
                "assigned_to": request.data.get('assigned_to')
                }
        print(req_data)
        serializer = self.get_serializer(data=req_data)
        serializer.is_valid(raise_exception=True)
        print(serializer.is_valid())
        print("serializer" + serializer)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()
