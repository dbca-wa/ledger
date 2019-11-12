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
from ledger.accounts.models import EmailUser,OrganisationAddress
from ledger.address.models import Country
from datetime import datetime,timedelta, date
from disturbance.helpers import is_customer, is_internal
from disturbance.components.organisations.models import  (   
                                    Organisation,
                                    OrganisationContact,
                                    OrganisationRequest,
                                    OrganisationRequestUserAction,
                                    OrganisationContact,
                                    OrganisationAccessGroup,
                                    OrganisationRequestLogEntry,
                                    OrganisationAction,
                                    ledger_organisation,
                                )

from disturbance.components.organisations.serializers import (   
                                        OrganisationSerializer,
                                        OrganisationAddressSerializer,
                                        DetailsSerializer,
                                        OrganisationRequestSerializer,
                                        OrganisationContactSerializer,
                                        OrganisationRequestDTSerializer,
                                        OrganisationContactSerializer,
                                        OrganisationCheckSerializer,
                                        OrganisationPinCheckSerializer,
                                        OrganisationRequestActionSerializer,
                                        OrganisationActionSerializer,
                                        OrganisationRequestCommsSerializer,
                                        OrganisationCommsSerializer,
                                        OrganisationUnlinkUserSerializer,
                                        OrgUserAcceptSerializer,
                                        MyOrganisationsSerializer,
                                        OrganisationCheckExistSerializer,
                                        LedgerOrganisationFilterSerializer,
                                        OrganisationLogEntrySerializer,
                                    )
from disturbance.components.proposals.serializers import (
                                        DTProposalSerializer,
                                    )
from disturbance.components.organisations.emails import (
                        send_organisation_address_updated_email_notification,
                        send_organisation_id_upload_email_notification,
                        send_organisation_request_email_notification,
                    )

class OrganisationViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer

    def _get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Organisation.objects.all()
        elif is_customer(self.request):
            return user.disturbance_organisations.all()
        return Organisation.objects.none()

    @detail_route(methods=['GET',])
    def contacts(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrganisationContactSerializer(instance.contacts.all(),many=True)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def contacts_linked(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = OrganisationContactSerializer(qs,many=True)
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

    @detail_route(methods=['GET',])
    def contacts_exclude(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.contacts.exclude(user_status='draft')
            serializer = OrganisationContactSerializer(qs,many=True)
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

    @detail_route(methods=['POST',])
    def validate_pins(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrganisationPinCheckSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            ret = instance.validate_pins(serializer.validated_data['pin1'],serializer.validated_data['pin2'],request)

            if ret == None:
                # user has already been to this organisation - don't add again
                data = {'valid': ret}
                return Response({'valid' : 'User already exists'})

            data = {'valid': ret}
            if data['valid']:
                # Notify each Admin member of request.
                instance.send_organisation_request_link_notification(request)
            return Response(data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    # @detail_route(methods=['POST',])
    # def unlink_user(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         serializer = OrganisationUnlinkUserSerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         try:
    #             instance.delegates.get(id=request.user.id)
    #         except EmailUser.DoesNotExist:
    #             raise serializers.ValidationError('You are not permitted to perform this operation since you are not a member of this organisation.')
    #         instance.unlink_user(serializer.validated_data['user_obj'],request)
    #         serializer = self.get_serializer(instance)
    #         return Response(serializer.data);
    #     except serializers.ValidationError:
    #         print(traceback.print_exc())
    #         raise
    #     except ValidationError as e:
    #         print(traceback.print_exc())
    #         if hasattr(e,'error_dict'):
    #             raise serializers.ValidationError(repr(e.error_dict))
    #         else:
    #             raise serializers.ValidationError(repr(e[0].encode('utf-8')))
    #     except Exception as e:
    #         print(traceback.print_exc())
    #         raise serializers.ValidationError(str(e)) 

    @detail_route(methods=['POST', ])
    def accept_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data['email']
            )
            instance.accept_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
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
    def accept_declined_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email=serializer.validated_data['email']
            )
            instance.accept_declined_user(user_obj, request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def decline_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email = serializer.validated_data['email']
                )
            instance.decline_user(user_obj,request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def unlink_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email = serializer.validated_data['email']
                )
            instance.unlink_user(user_obj,request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))




    @detail_route(methods=['POST',])
    def make_admin_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email = serializer.validated_data['email']
                )
            instance.make_admin_user(user_obj,request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def make_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email = serializer.validated_data['email']
                )
            instance.make_user(user_obj,request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def make_consultant(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email = serializer.validated_data['email']
                )
            instance.make_consultant(user_obj,request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def suspend_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email = serializer.validated_data['email']
                )
            instance.suspend_user(user_obj,request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def reinstate_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email = serializer.validated_data['email']
                )
            instance.reinstate_user(user_obj,request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['POST',])
    def relink_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrgUserAcceptSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = EmailUser.objects.get(
                email = serializer.validated_data['email']
                )
            instance.relink_user(user_obj,request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


    @detail_route(methods=['GET',])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = OrganisationActionSerializer(qs,many=True)
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

    @detail_route(methods=['GET',])
    def proposals(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.proposals.all()
            serializer = DTProposalSerializer(qs,many=True)
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

    @detail_route(methods=['GET',])
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = OrganisationCommsSerializer(qs,many=True)
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

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                request.data['organisation'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = OrganisationLogEntrySerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents
                
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

    

    @list_route(methods=['POST',])
    def existance(self, request, *args, **kwargs):
        try:
            serializer = OrganisationCheckSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = Organisation.existance(serializer.validated_data['abn']) 
            data.update([('user', request.user.id)])
            data.update([('abn', request.data['abn'])])
            serializer = OrganisationCheckExistSerializer(data=data)
            serializer.is_valid(raise_exception=True)
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

    @detail_route(methods=['POST',])
    def update_details(self, request, *args, **kwargs):
        try:
            org = self.get_object()
            instance = org.organisation
            serializer = DetailsSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            org.update_organisation(request)
            instance = serializer.save()
            serializer = self.get_serializer(org)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET',])
    def contacts(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.update_contacts(request)
            serializer = OrganisationContactSerializer(instance.contacts.all(),many=True)
            return Response(serializer.data);
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST',])
    def update_address(self, request, *args, **kwargs):
        try:
            org = self.get_object()
            instance = org.organisation
            serializer = OrganisationAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            address, created = OrganisationAddress.objects.get_or_create(
                line1 = serializer.validated_data['line1'],
                locality = serializer.validated_data['locality'],
                state = serializer.validated_data['state'],
                country = serializer.validated_data['country'],
                postcode = serializer.validated_data['postcode'],
                organisation = instance
            )
            instance.postal_address = address
            org.update_address(request)
            instance.save()
            serializer = self.get_serializer(org)
            return Response(serializer.data);
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

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return OrganisationRequest.objects.all()
        elif is_customer(self.request):
            return user.organisationrequest_set.all()
        return OrganisationRequest.objects.none()


    @list_route(methods=['GET',])
    def datatable_list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = OrganisationRequestDTSerializer(qs,many=True)
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

    @list_route(methods=['GET',])
    def user_list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset().filter(requester = request.user, status='with_assessor')
            serializer = OrganisationRequestDTSerializer(qs,many=True)
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


    @list_route(methods=['GET', ])
    def get_pending_requests(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset().filter(requester=request.user, status='with_assessor')
            serializer = OrganisationRequestDTSerializer(qs, many=True)
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

    @list_route(methods=['GET', ])
    def get_amendment_requested_requests(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset().filter(requester=request.user, status='amendment_requested')
            serializer = OrganisationRequestDTSerializer(qs, many=True)
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


    @detail_route(methods=['GET',])
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_to(request.user,request)
            serializer = OrganisationRequestSerializer(instance)
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

    @detail_route(methods=['GET',])
    def unassign(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign(request)
            serializer = OrganisationRequestSerializer(instance)
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

    @detail_route(methods=['GET',])
    def accept(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept(request)
            serializer = OrganisationRequestSerializer(instance)
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

    @detail_route(methods=['GET',])
    def amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.amendment_request(request)
            serializer = OrganisationRequestSerializer(instance)
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

    @detail_route(methods=['GET',])
    def decline(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            reason=''
            instance.decline(reason, request)
            serializer = OrganisationRequestSerializer(instance)
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

    @detail_route(methods=['POST',])
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get('user_id',None)
            user = None
            if not user_id:
                raise serializers.ValiationError('A user id is required')
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise serializers.ValidationError('A user with the id passed in does not exist')
            instance.assign_to(user,request)
            serializer = OrganisationRequestSerializer(instance)
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

    @detail_route(methods=['GET',])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = OrganisationRequestActionSerializer(qs,many=True)
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

    @detail_route(methods=['GET',])
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = OrganisationRequestCommsSerializer(qs,many=True)
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

    @detail_route(methods=['POST',])
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                request.data['request'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = OrganisationRequestCommsSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents
                
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

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['requester'] = request.user
            if request.data['role'] == 'consultant':
                # Check if consultant can be relinked to org.
                data = Organisation.existance(request.data['abn'])
                data.update([('user', request.user.id)])
                data.update([('abn', request.data['abn'])])
                existing_org = OrganisationCheckExistSerializer(data=data)
                existing_org.is_valid(raise_exception=True)
            with transaction.atomic():
                instance = serializer.save()
                instance.log_user_action(OrganisationRequestUserAction.ACTION_LODGE_REQUEST.format(instance.id),request)
                instance.send_organisation_request_email_notification(request)
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

class OrganisationAccessGroupMembers(views.APIView):
    
    renderer_classes = [JSONRenderer,]
    def get(self,request, format=None):
        members = []
        group = OrganisationAccessGroup.objects.first()
        if group:
            for m in group.all_members:
                members.append({'name': m.get_full_name(),'id': m.id})
        else:
            for m in EmailUser.objects.filter(is_superuser=True,is_staff=True,is_active=True):
                members.append({'name': m.get_full_name(),'id': m.id})
        return Response(members)


class OrganisationContactViewSet(viewsets.ModelViewSet):
    serializer_class = OrganisationContactSerializer
    queryset = OrganisationContact.objects.all()

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return OrganisationContact.objects.all()
        elif is_customer(self.request):
            user_orgs = [org.id for org in user.disturbance_organisations.all()]
            return OrganisationContact.objects.filter( Q(organisation_id__in = user_orgs) )
        return OrganisationContact.objects.none()

class MyOrganisationsViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = MyOrganisationsSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Organisation.objects.all()
        elif is_customer(self.request):
            return user.disturbance_organisations.all()
        return Organisation.objects.none()

