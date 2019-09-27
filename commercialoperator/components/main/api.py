import traceback
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.db import transaction
from wsgiref.util import FileWrapper
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes, parser_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from django.urls import reverse
from commercialoperator.components.main.models import Region, District, Tenure, ApplicationType, ActivityMatrix, AccessType, Park, Trail, ActivityCategory, Activity, RequiredDocument, Question, GlobalSettings
from commercialoperator.components.main.serializers import RegionSerializer, DistrictSerializer, TenureSerializer, ApplicationTypeSerializer, ActivityMatrixSerializer,  AccessTypeSerializer, ParkSerializer, ParkFilterSerializer, TrailSerializer, ActivitySerializer, ActivityCategorySerializer, RequiredDocumentSerializer, QuestionSerializer, GlobalSettingsSerializer, OracleSerializer, BookingSettlementReportSerializer, LandActivityTabSerializer, MarineActivityTabSerializer
from django.core.exceptions import ValidationError
from django.db.models import Q
from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.proposals.serializers import ProposalSerializer
from commercialoperator.components.bookings.utils import oracle_integration
from commercialoperator.components.bookings import reports
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, get_cookie_basket
from collections import namedtuple
import json
from decimal import Decimal

import logging
logger = logging.getLogger('payment_checkout')


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


class TenureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tenure.objects.all().order_by('order')
    serializer_class = TenureSerializer


class ApplicationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    #queryset = ApplicationType.objects.all().order_by('order')
    queryset = ApplicationType.objects.none()
    serializer_class = ApplicationTypeSerializer

    def get_queryset(self):
        return ApplicationType.objects.order_by('order').filter(visible=True)


class AccessTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccessType.objects.all().order_by('id')
    serializer_class = AccessTypeSerializer


class ParkFilterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Park.objects.all().order_by('id')
    serializer_class = ParkFilterSerializer


class GlobalSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GlobalSettings.objects.all().order_by('id')
    serializer_class = GlobalSettingsSerializer

class LandActivityTabViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing the various serialized viewsets in a single container
    """
    def list(self, request):
        #Container = namedtuple('ActivityLandTab', ('access_types', 'activity_types', 'regions'))
        Container = namedtuple('ActivityLandTab', ('access_types', 'land_activity_types', 'marine_activity_types', 'trails', 'marine_activities', 'land_required_documents', 'regions'))
        container = Container(
            access_types=AccessType.objects.all().order_by('id'),
            land_activity_types=Activity.objects.filter(activity_category__activity_type='land').order_by('id'),
            marine_activity_types=Activity.objects.filter(activity_category__activity_type='marine').order_by('id'),
            trails=Trail.objects.all().order_by('id'),
            marine_activities=ActivityCategory.objects.filter(activity_type='marine').order_by('id'),
            land_required_documents=RequiredDocument.objects.filter().order_by('id'),
            regions=Region.objects.all().order_by('id'),
        )
        serializer = LandActivityTabSerializer(container)
        return Response(serializer.data)


class MarineActivityTabViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing the various serialized viewsets in a single container
    """
    def list(self, request):
        #Container = namedtuple('ActivityLandTab', ('access_types', 'activity_types', 'regions'))
        Container = namedtuple('ActivityMarineTab', ('marine_activities', 'marine_parks', 'required_documents'))
        container = Container(
            #marine_activity_types=Activity.objects.filter(activity_category__activity_type='marine').order_by('id'),
            marine_activities=ActivityCategory.objects.filter(activity_type='marine').order_by('id'),
            #marine_parks=ActivityCategory.objects.filter(activity_type='marine').order_by('id'),
            marine_parks=Park.objects.filter(park_type='marine').order_by('id'),
            required_documents=RequiredDocument.objects.filter().order_by('id'),
        )
        serializer = MarineActivityTabSerializer(container)
        return Response(serializer.data)


class ParkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Park.objects.all().order_by('id')
    serializer_class = ParkSerializer

    @list_route(methods=['GET',])
    def filter_list(self, request, *args, **kwargs):
        serializer = ParkFilterSerializer(self.get_queryset(),context={'request':request}, many=True)
        return Response(serializer.data)

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

    @detail_route(methods=['GET',])
    def allowed_access(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.allowed_access.all()
        serializer = AccessTypeSerializer(qs,context={'request':request}, many=True)
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


class PaymentViewSet(viewsets.ModelViewSet):
    #queryset = Proposal.objects.all()
    queryset = Proposal.objects.none()
    #serializer_class = ProposalSerializer
    serializer_class = ProposalSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        response = super(PaymentViewSet, self).create(request, *args, **kwargs)
        # here may be placed additional operations for
        # extracting id of the object and using reverse()
        fallback_url = request.build_absolute_uri('/')
        return HttpResponseRedirect(redirect_to=fallback_url + '/success/')

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def park_payment(self, request, *args, **kwargs):

        try:
            with transaction.atomic():
                #instance = self.get_object()
                proposal = Proposal.objects.get(id=kwargs['id'])
                lines = self.create_lines(request)
                response = self.checkout(request, proposal, lines, invoice_text='Some invoice text')

                return response

                #data = [dict(key='My Response')]
                #return Response(data)

                #return Response(serializer.data)

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class BookingSettlementReportView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            #parse and validate data
            report = None
            data = {
                "date":request.GET.get('date'),
            }
            serializer = BookingSettlementReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'Booking Settlement Report-{}'.format(str(serializer.validated_data['date']))
            # Generate Report
            report = reports.booking_bpoint_settlement_report(serializer.validated_data['date'])
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()


#class BookingReportView(views.APIView):
#    renderer_classes = (JSONRenderer,)
#
#    def get(self,request,format=None):
#        try:
#            http_status = status.HTTP_200_OK
#            #parse and validate data
#            report = None
#            data = {
#                "date":request.GET.get('date'),
#            }
#            serializer = BookingSettlementReportSerializer(data=data)
#            serializer.is_valid(raise_exception=True)
#            filename = 'Booking Report-{}'.format(str(serializer.validated_data['date']))
#            # Generate Report
#            report = reports.bookings_report(serializer.validated_data['date'])
#            if report:
#                response = HttpResponse(FileWrapper(report), content_type='text/csv')
#                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
#                return response
#            else:
#                raise serializers.ValidationError('No report was generated.')
#        except serializers.ValidationError:
#            raise
#        except Exception as e:
#            traceback.print_exc()


class OracleJob(views.APIView):
    renderer_classes = [JSONRenderer,]
    def get(self, request, format=None):
        try:
            data = {
                "date":request.GET.get("date"),
                "override": request.GET.get("override")
            }
            serializer = OracleSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            oracle_integration(serializer.validated_data['date'].strftime('%Y-%m-%d'),serializer.validated_data['override'])
            data = {'successful':True}
            return Response(data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))



