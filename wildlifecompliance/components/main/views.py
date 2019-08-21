import traceback
from django.core.exceptions import ValidationError
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
    SearchReferenceSerializer
)


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
        if request.data.get('searchTerm'): # modify as appropriate
            qs = search_weak_links(request.data)
        serializer = SearchWeakLinksSerializer(qs, many=True)
        return Response(serializer.data)

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
