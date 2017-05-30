import traceback
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
from rest_framework.decorators import detail_route, list_route,renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser,Address
from ledger.address.models import Country
from disturbance import utils
from datetime import datetime,timedelta, date
from disturbance.models import  (   Organisation,
                                    OrganisationRequest,
                                    OrganisationContact
                                )

from disturbance.serializers.organisations import (   
                                        OrganisationSerializer,
                                        OrganisationRequestSerializer,
                                        OrganisationContactSerializer,
                                        OrganisationCheckSerializer,
                                        OrganisationPinCheckSerializer,
                                    )

class OrganisationViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer

    @detail_route(methods=['GET',])
    def contacts(self, request, *args, **kwargs):
        pass

    @detail_route(methods=['POST',])
    def validate_pins(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrganisationPinCheckSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = {'valid': instance.validate_pins(serializer.validated_data['pin1'],serializer.validated_data['pin2'])} 
            return Response(data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @list_route(methods=['POST',])
    def existance(self, request, *args, **kwargs):
        try:
            serializer = OrganisationCheckSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = Organisation.existance(serializer.validated_data['abn']) 
            return Response(data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))
    
class OrganisationRequestsViewSet(viewsets.ModelViewSet):
    queryset = OrganisationRequest.objects.all()
    serializer_class = OrganisationRequestSerializer

