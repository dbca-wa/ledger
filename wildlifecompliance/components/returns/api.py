import traceback

from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import detail_route, list_route, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.returns.utils import SpreadSheet
from wildlifecompliance.components.licences.models import (
    WildlifeLicence
)
from wildlifecompliance.components.returns.models import (
    Return,
    ReturnType,
)
from wildlifecompliance.components.returns.serializers import (
    ReturnSerializer,
    ReturnActionSerializer,
    ReturnCommsSerializer,
    ReturnTypeSerializer,
)


class ReturnViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReturnSerializer
    queryset = Return.objects.all()

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return Return.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in user.wildlifecompliance_organisations.all()]
            user_licences = [wildlifelicence.id for wildlifelicence in WildlifeLicence.objects.filter(
                Q(current_application__org_applicant_id__in=user_orgs) |
                Q(current_application__proxy_applicant=user) |
                Q(current_application__submitter=user))]
            return Return.objects.filter(Q(licence_id__in=user_licences))
        return Return.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get('org_id', None)
        if org_id:
            queryset = queryset.filter(current_application__org_applicant_id=org_id)
        # Filter by proxy_applicant
        proxy_applicant_id = request.GET.get('proxy_applicant_id', None)
        if proxy_applicant_id:
            queryset = queryset.filter(current_application__proxy_applicant_id=proxy_applicant_id)
        # Filter by submitter
        submitter_id = request.GET.get('submitter_id', None)
        if submitter_id:
            queryset = queryset.filter(current_application__submitter_id=submitter_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET', ])
    def user_list(self, request, *args, **kwargs):
        qs = self.get_queryset().exclude(processing_status='future')

        serializer = ReturnSerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(methods=['POST', ])
    @renderer_classes((JSONRenderer,))
    def update_details(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.has_data:
                instance.data.store(request)
            instance.set_submitted(request)
            instance.submitter = request.user
            instance.save()

            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                print e
                raise serializers.ValidationError(repr(e[0].encode('utf-8')))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET', ])
    def accept(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept(request)
            serializer = self.get_serializer(instance)
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
    def upload_details(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.method == 'POST':
                spreadsheet = SpreadSheet(
                    instance, request.FILES['spreadsheet']).factory()
                if not spreadsheet.is_valid():
                    return Response(
                        {'error': 'Enter data in correct format.'}, status=status.HTTP_404_NOT_FOUND)
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
    def sheet_details(self, request, *args, **kwargs):
        return_id = self.request.query_params.get('return_id')
        instance = Return.objects.get(id=return_id)
        return Response(instance.sheet.table)

    @detail_route(methods=['POST', ])
    def save(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if instance.has_data:
                instance.data.store(request)

            if instance.has_sheet:
                instance.sheet.store(request)

            instance.set_submitted(request)
            instance.submitter = request.user
            instance.save()
            serializer = self.get_serializer(instance)
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
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = ReturnCommsSerializer(qs, many=True)
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
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                request.data['compliance'] = u'{}'.format(instance.id)
                request.data['staff'] = u'{}'.format(request.user.id)
                serializer = ReturnCommsSerializer(data=request.data)
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

    @detail_route(methods=['GET', ])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ReturnActionSerializer(qs, many=True)
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


class ReturnTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReturnTypeSerializer
    queryset = ReturnType.objects.none()

    def get_queryset(self):
        if is_internal(self.request):
            return ReturnType.objects.all()
        return ReturnType.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
