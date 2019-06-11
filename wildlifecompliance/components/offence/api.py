from rest_framework import viewsets
from wildlifecompliance.components.offence.models import Offence
from wildlifecompliance.components.offence.serializers import OffenceSerializer


class OffenceViewSet(viewsets.ModelViewSet):
    queryset = Offence.objects.all()
    serializer_class = OffenceSerializer
