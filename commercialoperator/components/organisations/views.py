from commercialoperator.components.organisations.models import Organisation
from reversion_compare.views import HistoryCompareDetailView


class OrganisationHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Organisation
    template_name = 'commercialoperator/reversion_history.html'
