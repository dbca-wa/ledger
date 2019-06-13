from rest_framework import viewsets, filters
from wildlifecompliance.components.offence.models import Offence, SectionRegulation
from wildlifecompliance.components.offence.serializers import OffenceSerializer, SectionRegulationSerializer


class OffenceViewSet(viewsets.ModelViewSet):
    queryset = Offence.objects.all()
    serializer_class = OffenceSerializer


class SearchSectionRegulation(viewsets.ModelViewSet):
    queryset = SectionRegulation.objects.all()
    serializer_class = SectionRegulationSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('act', 'name', 'offence_text',)
