import traceback
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.db import transaction
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import detail_route, list_route, renderer_classes, parser_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from django.urls import reverse
from commercialoperator.components.main.models import Region, District, Tenure, ApplicationType, ActivityMatrix, AccessType, Park, Trail, ActivityCategory, Activity, RequiredDocument, Question
from commercialoperator.components.main.serializers import RegionSerializer, DistrictSerializer, TenureSerializer, ApplicationTypeSerializer, ActivityMatrixSerializer,  AccessTypeSerializer, ParkSerializer, ParkFilterSerializer, TrailSerializer, ActivitySerializer, ActivityCategorySerializer, RequiredDocumentSerializer, QuestionSerializer
from django.core.exceptions import ValidationError
from django.db.models import Q
from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.proposals.serializers import ProposalSerializer
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, get_cookie_basket
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

class ParkFilterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Park.objects.all().order_by('id')
    serializer_class = ParkFilterSerializer

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
    #import ipdb; ipdb.set_trace()
    #queryset = Proposal.objects.all()
    queryset = Proposal.objects.none()
    #serializer_class = ProposalSerializer
    serializer_class = ProposalSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        #import ipdb; ipdb.set_trace()
        response = super(PaymentViewSet, self).create(request, *args, **kwargs)
        # here may be placed additional operations for
        # extracting id of the object and using reverse()
        fallback_url = request.build_absolute_uri('/')
        return HttpResponseRedirect(redirect_to=fallback_url + '/success/')

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def park_payment(self, request, *args, **kwargs):

        #import ipdb; ipdb.set_trace()
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


    def create_lines(self, request, invoice_text=None, vouchers=[], internal=False):
        """ Create the ledger lines - line items for invoice sent to payment system """

        lines = []
        tbody = json.loads(request.data['tbody'])
        for row in tbody:
            park_id = row[0]['value']
            arrival = row[1]
            no_adults = int(row[2]) if row[2] else 0
            no_children = int(row[3]) if row[3] else 0
            park= Park.objects.get(id=park_id)
            #ledger_description = arrival + '. ' + park.name + ' (' + row[2] + ' Adults' + ')'
            oracle_code = 'ABC123 GST'
            #price_incl_tax = str(park.adult * int(no_adults))
            quantity = 1

            if no_adults > 0:
                lines.append(dict(
                    ledger_description = arrival + '. ' + park.name + ' (' + str(no_adults) + ' Adults' + ')',
                    oracle_code = 'ABC123 GST',
                    price_incl_tax = Decimal(park.adult * no_adults),
                    quantity = 1
                ))
                print arrival + '. ' + park.name + '. Adults: ' + str(no_adults) + ', Price: ' + str(park.adult * no_adults)

            if no_children > 0:

                lines.append(dict(
                    ledger_description = arrival + '. ' + park.name + ' (' + str(no_children) + ' Children' + ')',
                    oracle_code = 'ABC123 GST',
                    price_incl_tax = Decimal(park.child * no_children),
                    quantity = 1
                ))
                print arrival + '. ' + park.name + '. Children: ' + str(no_children) + ', Price: ' + str(park.child * no_children)

        return lines

    def checkout(self, request, proposal, lines, invoice_text=None, vouchers=[], internal=False):
        #import ipdb; ipdb.set_trace()
        basket_params = {
            'products': lines,
            'vouchers': vouchers,
            'system': settings.PS_PAYMENT_SYSTEM_ID,
            'custom_basket': True,
        }

        basket, basket_hash = create_basket_session(request, basket_params)
        fallback_url = request.build_absolute_uri('/')
        checkout_params = {
            'system': settings.PS_PAYMENT_SYSTEM_ID,
            #'fallback_url': request.build_absolute_uri('/'),                                      # 'http://mooring-ria-jm.dbca.wa.gov.au/'
            #'return_url': request.build_absolute_uri(reverse('public_booking_success')),          # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
            #'return_preload_url': request.build_absolute_uri(reverse('public_booking_success')),  # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
            'fallback_url': fallback_url,
            'return_url': fallback_url + '/success/',
            'return_preload_url': fallback_url + '/success/',
            'force_redirect': True,
            'proxy': True if internal else False,
            'invoice_text': invoice_text,                                                         # 'Reservation for Jawaid Mushtaq from 2019-05-17 to 2019-05-19 at RIA 005'
        }
#    if not internal:
#        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
        if internal or request.user.is_anonymous():
            #checkout_params['basket_owner'] = booking.customer.id
            checkout_params['basket_owner'] = proposal.submitter_id


        create_checkout_session(request, checkout_params)

#    if internal:
#        response = place_order_submission(request)
#    else:
        response = HttpResponseRedirect(reverse('checkout:index'))
        # inject the current basket into the redirect response cookies
        # or else, anonymous users will be directionless
        response.set_cookie(
                settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
                max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
                secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
        )

#    if booking.cost_total < 0:
#        response = HttpResponseRedirect('/refund-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )
#
#    # Zero booking costs
#    if booking.cost_total < 1 and booking.cost_total > -1:
#        response = HttpResponseRedirect('/no-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )

        return response

