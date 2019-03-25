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
from rest_framework.decorators import detail_route, list_route, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address, Profile, EmailIdentity, EmailUserAction, query_emailuser_by_args
from ledger.address.models import Country
from datetime import datetime, timedelta, date
from wildlifecompliance.components.organisations.models import (
    OrganisationRequest,
)

from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.users.serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserAddressSerializer,
    PersonalSerializer,
    ContactSerializer,
    EmailIdentitySerializer,
    EmailUserActionSerializer
)
from wildlifecompliance.components.organisations.serializers import (
    OrganisationRequestDTSerializer,
)


class GetProfile(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class GetUser(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        serializer = PersonalSerializer(request.user)
        return Response(serializer.data)


class IsNewUser(views.APIView):
    def get(self, request, format=None):
        is_new = 'False'
        try:
            is_new = request.session['is_new']
        except BaseException:
            pass
        return HttpResponse(is_new)


class UserProfileCompleted(views.APIView):
    def get(self, request, format=None):
        request.session['is_new'] = False
        request.session['new_to_wildlifecompliance'] = False
        return HttpResponse('OK')


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Profile.objects.all()
        elif is_customer(self.request):
            return Profile.objects.filter(user=user)
        return Profile.objects.none()

    @detail_route(methods=['POST', ])
    def update_profile(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserProfileSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer = UserSerializer(instance)
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


class MyProfilesViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class UserViewSet(viewsets.ModelViewSet):
    queryset = EmailUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        """
        Optionally restrict the query if the following parameters are in the URL:
                - first_name
                - last_name
                - dob
                - email
        """
        user = self.request.user
        if is_internal(self.request):
            queryset = EmailUser.objects.all()
        elif is_customer(self.request):
            queryset = EmailUser.objects.filter(id=user.id)
        else:
            queryset = EmailUser.objects.none()
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        dob = self.request.query_params.get('dob', None)
        email = self.request.query_params.get('email', None)
        if first_name is not None:
            queryset = queryset.filter(first_name__iexact=first_name)
        if last_name is not None:
            queryset = queryset.filter(last_name__iexact=last_name)
        if email is not None:
            queryset = queryset.filter(email__iexact=email)
        if dob is not None and dob is not u'':
            queryset = queryset.filter(dob=dob)
        return queryset

    def list(self, request, **kwargs):
        if request.query_params:
            try:
                users = query_emailuser_by_args(**request.query_params)
                serializer = UserSerializer(users['items'], many=True)
                result = dict()
                result['data'] = serializer.data
                result['draw'] = int(users['draw'])
                result['recordsTotal'] = users['total']
                result['recordsFiltered'] = users['count']
                return Response(result)
            except Exception as e:
                return Response(e)
        else:
            try:
                return super(UserViewSet, self).list(request, **kwargs)

            except Exception as e:
                return Response(e)

    @detail_route(methods=['GET', ])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = EmailUserActionSerializer(qs, many=True)
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

    @detail_route(methods=['GET', ])
    def profiles(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserProfileSerializer(
                instance.profiles.all(), many=True)
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

    @detail_route(methods=['POST', ])
    def update_personal(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = PersonalSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                instance = serializer.save()
                instance.log_user_action(
                    EmailUserAction.ACTION_PERSONAL_DETAILS_UPDATE.format(
                        '{} {} ({})'.format(
                            instance.first_name,
                            instance.last_name,
                            instance.email)),
                    request)
            serializer = UserSerializer(instance)
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

    @detail_route(methods=['POST', ])
    def update_contact(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ContactSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                instance = serializer.save()
                instance.log_user_action(
                    EmailUserAction.ACTION_CONTACT_DETAILS_UPDATE.format(
                        '{} {} ({})'.format(
                            instance.first_name,
                            instance.last_name,
                            instance.email)),
                    request)
            serializer = UserSerializer(instance)
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

    @detail_route(methods=['POST', ])
    def update_address(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = UserAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            address, created = Address.objects.get_or_create(
                line1=serializer.validated_data['line1'],
                locality=serializer.validated_data['locality'],
                state=serializer.validated_data['state'],
                country=serializer.validated_data['country'],
                postcode=serializer.validated_data['postcode'],
                user=instance
            )
            instance.residential_address = address
            with transaction.atomic():
                instance.save()
                instance.log_user_action(
                    EmailUserAction.ACTION_POSTAL_ADDRESS_UPDATE.format(
                        '{} {} ({})'.format(
                            instance.first_name,
                            instance.last_name,
                            instance.email)),
                    request)
            serializer = UserSerializer(instance)
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

    @detail_route(methods=['POST', ])
    def upload_id(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.upload_identification(request)
            with transaction.atomic():
                instance.save()
                instance.log_user_action(
                    EmailUserAction.ACTION_ID_UPDATE.format(
                        '{} {} ({})'.format(
                            instance.first_name,
                            instance.last_name,
                            instance.email)),
                    request)
            serializer = UserSerializer(instance, partial=True)
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

    @detail_route(methods=['GET', ])
    def pending_org_requests(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrganisationRequestDTSerializer(
                instance.organisationrequest_set.filter(
                    status=OrganisationRequest.ORG_REQUEST_STATUS_WITH_ASSESSOR), many=True)
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


class EmailIdentityViewSet(viewsets.ModelViewSet):
    queryset = EmailIdentity.objects.all()
    serializer_class = EmailIdentitySerializer

    def get_queryset(self):
        """
        Optionally restrict the query if the following parameters are in the URL:
                - email
        """
        user = self.request.user
        if is_internal(self.request):
            queryset = EmailIdentity.objects.all()
        elif is_customer(self.request):
            queryset = user.emailidentity_set.all()
        else:
            queryset = EmailIdentity.objects.none()
        email = self.request.query_params.get('email', None)
        exclude_user = self.request.query_params.get('exclude_user', None)
        if email is not None:
            queryset = queryset.filter(email__iexact=email)
        if exclude_user is not None:
            queryset = queryset.exclude(user=exclude_user)
        return queryset
