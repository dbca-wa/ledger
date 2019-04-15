import traceback
from django.conf import settings
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes, parser_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from django.urls import reverse
from commercialoperator.components.main.models import Region, District, Tenure, ApplicationType, ActivityMatrix, AccessType, Park, Trail, ActivityCategory, Activity, RequiredDocument, Question
from commercialoperator.components.main.serializers import RegionSerializer, DistrictSerializer, TenureSerializer, ApplicationTypeSerializer, ActivityMatrixSerializer,  AccessTypeSerializer, ParkSerializer, TrailSerializer, ActivitySerializer, ActivityCategorySerializer, RequiredDocumentSerializer, QuestionSerializer
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

# class VehicleViewSet(viewsets.ModelViewSet):
#     queryset = Vehicle.objects.all().order_by('id')
#     serializer_class = VehicleSerializer

#     @detail_route(methods=['post'])
#     def edit_vehicle(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = SaveVehicleSerializer(instance, data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data)
#         except serializers.ValidationError:
#             print(traceback.print_exc())
#             raise
#         except ValidationError as e:
#             if hasattr(e,'error_dict'):
#                 raise serializers.ValidationError(repr(e.error_dict))
#             else:
#                 raise serializers.ValidationError(repr(e[0].encode('utf-8')))
#         except Exception as e:
#             print(traceback.print_exc())
#             raise serializers.ValidationError(str(e))

#     def create(self, request, *args, **kwargs):
#         try:
#             #instance = self.get_object()
#             serializer = SaveVehicleSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data)
#         except serializers.ValidationError:
#             print(traceback.print_exc())
#             raise
#         except ValidationError as e:
#             if hasattr(e,'error_dict'):
#                 raise serializers.ValidationError(repr(e.error_dict))
#             else:
#                 raise serializers.ValidationError(repr(e[0].encode('utf-8')))
#         except Exception as e:
#             print(traceback.print_exc())
#             raise serializers.ValidationError(str(e))

class AccessTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccessType.objects.all().order_by('id')
    serializer_class = AccessTypeSerializer

class ParkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Park.objects.all().order_by('id')
    serializer_class = ParkSerializer

    @list_route(methods=['GET',])
    def marine_parks(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(park_type='marine')
        serializer = ParkSerializer(qs,context={'request':request}, many=True)
        return Response(serializer.data)

    @detail_route(methods=['GET',])
    def allowed_activities(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.allowed_activities.all()
        serializer = ActivitySerializer(qs,context={'request':request}, many=True)
        #serializer = ActivitySerializer(qs)
        return Response(serializer.data)

class TrailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trail.objects.all().order_by('id')
    serializer_class = TrailSerializer

    @detail_route(methods=['GET',])
    def allowed_activities(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.allowed_activities.all()
        serializer = ActivitySerializer(qs,context={'request':request}, many=True)
        #serializer = ActivitySerializer(qs)
        return Response(serializer.data)


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

class RequiredDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RequiredDocument.objects.all()
    serializer_class = RequiredDocumentSerializer

    # def get_queryset(self):
    #     categories=ActivityCategory.objects.filter(activity_type='marine')
    #     return categories

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer