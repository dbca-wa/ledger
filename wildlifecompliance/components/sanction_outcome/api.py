from rest_framework import viewsets

from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome
from wildlifecompliance.components.sanction_outcome.serializers import SanctionOutcomeSerializer
from wildlifecompliance.helpers import is_internal


class SanctionOutcomeViewSet(viewsets.ModelViewSet):
    queryset = SanctionOutcome.objects.all()
    serializer_class = SanctionOutcomeSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return SanctionOutcome.objects.all()
        return SanctionOutcome.objects.none()
