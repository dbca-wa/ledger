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
from disturbance.models import  (   
                                    ProposalType,
                                )

from disturbance.serializers.proposal import   (   
                                                ProposalTypeSerializer,
                                            )
class GetProposalType(views.APIView):
    renderer_classes = [JSONRenderer,]
    def get(self, request, format=None):
        _type = ProposalType.objects.first()
        if _type:
            serializer  = ProposalTypeSerializer(_type)
            return Response(serializer.data)
        else:
            return Response({'error':'There is currently no proposal type.'},status=status.HTTP_404_NOT_FOUND)


