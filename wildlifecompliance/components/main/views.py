import traceback
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers, views
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from wildlifecompliance.components.main.utils import (
    search_keywords,
    search_reference,
    search_weak_links,
)
from wildlifecompliance.components.main.serializers import (
    SearchKeywordSerializer,
    SearchReferenceSerializer,
    RelatedItemsSerializer,
)
from wildlifecompliance.components.main.models import WeakLinks
from wildlifecompliance.components.main.related_items_utils import get_related_items
from django.contrib.auth.models import ContentType


class SearchKeywordsView(views.APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        qs = []
        search_words = request.data.get('searchKeywords')
        search_application = request.data.get('searchApplication')
        search_licence = request.data.get('searchLicence')
        search_returns = request.data.get('searchReturn')
        is_internal = request.data.get('is_internal')
        if search_words:
            qs = search_keywords(search_words, search_application, search_licence, search_returns, is_internal)
        serializer = SearchKeywordSerializer(qs, many=True)
        return Response(serializer.data)


class SearchWeakLinksView(views.APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        qs = []
        if request.data.get('searchText'): # modify as appropriate
            qs = search_weak_links(request.data)
        return_qs = qs[:10]
        return Response(return_qs)


class CreateWeakLinkView(views.APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        try:
            with transaction.atomic():
                first_content_type_str = request.data.get('first_content_type')
                first_object_id = request.data.get('first_object_id')
                second_content_type_str = request.data.get('second_content_type')
                second_object_id = request.data.get('second_object_id')
                
                # transform request data to create new Weak Links obj
                second_object_id_int = int(second_object_id)
                first_content_type = ContentType.objects.get(
                        app_label='wildlifecompliance', 
                        model=first_content_type_str)
                second_content_type = ContentType.objects.get(
                        app_label='wildlifecompliance', 
                        model=second_content_type_str)
                
                weak_link_instance, created = WeakLinks.objects.get_or_create(
                        first_content_type_id = first_content_type.id,
                        first_object_id = first_object_id,
                        second_content_type_id = second_content_type.id,
                        second_object_id = second_object_id_int
                        )
                # derive parent (calling) object instance from weak_link_instance
                calling_instance = weak_link_instance.first_content_type.model_class().objects.get(id=first_object_id)

                # get related items of calling_instance
                related_items = get_related_items(calling_instance)
                serializer = RelatedItemsSerializer(related_items, many=True)

                return Response(serializer.data)

        except Exception as e:
            print(traceback.print_exc())
            #raise serializers.ValidationError(str(e))
            raise e


class RemoveWeakLinkView(views.APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        print(request.data)
        try:
            with transaction.atomic():
                first_content_type_str = request.data.get('first_content_type')
                first_object_id = request.data.get('first_object_id')
                second_content_type_str = request.data.get('second_content_type')
                second_object_id = request.data.get('second_object_id')
                
                # transform request data to search for Weak Link obj to delete
                second_object_id_int = int(second_object_id)
                first_content_type = ContentType.objects.get(
                        app_label='wildlifecompliance', 
                        model=first_content_type_str)
                second_content_type = ContentType.objects.get(
                        app_label='wildlifecompliance', 
                        model=second_content_type_str)

                # If weak link obj not found, test for object with first and second fields reversed and delete that instead.
                weak_link_qs = WeakLinks.objects.filter(
                        first_content_type_id = first_content_type.id,
                        first_object_id = first_object_id,
                        second_content_type_id = second_content_type.id,
                        second_object_id = second_object_id_int
                        )
                if weak_link_qs:
                    weak_link_instance = weak_link_qs[0]
                    weak_link_instance.delete()
                else:
                    weak_link_qs = WeakLinks.objects.filter(
                            first_content_type_id = second_content_type.id,
                            first_object_id = second_object_id_int,
                            second_content_type_id = first_content_type.id,
                            second_object_id = first_object_id
                            )
                    if weak_link_qs:
                        weak_link_instance = weak_link_qs[0]
                        weak_link_instance.delete()

                # derive parent (calling) object instance from ContentType
                calling_instance = first_content_type.model_class().objects.get(id=first_object_id)

                # get related items of calling_instance
                related_items = get_related_items(calling_instance)
                serializer = RelatedItemsSerializer(related_items, many=True)

                return Response(serializer.data)
        except Exception as e:
            print(traceback.print_exc())
            #raise serializers.ValidationError(str(e))
            raise e


class SearchReferenceView(views.APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        try:
            qs = []
            reference_number = request.data.get('reference_number')
            if reference_number:
                qs = search_reference(reference_number)
            serializer = SearchReferenceSerializer(qs)
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
