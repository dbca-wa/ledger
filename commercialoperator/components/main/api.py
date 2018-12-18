import traceback
from django.conf import settings
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes, parser_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from django.urls import reverse
from commercialoperator.components.main.models import Region, District, Tenure, ApplicationType, ActivityMatrix, Vehicle, AccessType, Park, Trail, ActivityCategory, Activity
from commercialoperator.components.main.serializers import RegionSerializer, DistrictSerializer, TenureSerializer, ApplicationTypeSerializer, ActivityMatrixSerializer, VehicleSerializer, AccessTypeSerializer, ParkSerializer, TrailSerializer, ActivitySerializer, ActivityCategorySerializer
from django.core.exceptions import ValidationError
from django.db.models import Q


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all().order_by('id')
    serializer_class = DistrictSerializer


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all().order_by('id')
    serializer_class = RegionSerializer


class ActivityMatrixViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = ActivityMatrix.objects.all().order_by('id')
    queryset = ActivityMatrix.objects.none()
    serializer_class = ActivityMatrixSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            return [ActivityMatrix.objects.filter(name='Commercial Operator').order_by('-version').first()]
        return ActivityMatrix.objects.none()

#    def list(self, request, *args, **kwargs):
#        matrix = ActivityMatrix.objects.filter(name='Commercial Operator').order_by('-version').first()
#        return Response( [activity['children'][0] for activity in matrix.schema] )


class TenureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tenure.objects.all().order_by('order')
    serializer_class = TenureSerializer

class ApplicationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = ApplicationType.objects.all().order_by('order')
    queryset = ApplicationType.objects.none()
    serializer_class = ApplicationTypeSerializer

    def get_queryset(self):
        return ApplicationType.objects.order_by('order').filter(visible=True)

class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vehicle.objects.all().order_by('id')
    serializer_class = VehicleSerializer

class AccessTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccessType.objects.all().order_by('id')
    serializer_class = AccessTypeSerializer

class ParkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Park.objects.all().order_by('id')
    serializer_class = ParkSerializer

class TrailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trail.objects.all().order_by('id')
    serializer_class = TrailSerializer

class LandActivitiesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.none()
    serializer_class = ActivitySerializer

    def get_queryset(self):
        categories=ActivityCategory.objects.filter(activity_type='land')
        activities=Activity.objects.filter(Q(activity_category__in = categories)& Q(visible=True))
        return activities

class MarineActivitiesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityCategory.objects.none()
    serializer_class = ActivityCategorySerializer

    def get_queryset(self):
        categories=ActivityCategory.objects.filter(activity_type='marine')
        return categories