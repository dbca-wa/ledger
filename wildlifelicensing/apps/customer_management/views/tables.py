from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.dashboard.views import officer
from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.returns.models import Return


class DataTableApplicationView(officer.DataTableApplicationsOfficerView):
    def get_initial_queryset(self):
        return Application.objects.filter(applicant_profile__user=self.args[0]).exclude(processing_status='draft')


class DataTableLicencesView(officer.DataTableLicencesOfficerView):
    def get_initial_queryset(self):
        return WildlifeLicence.objects.filter(holder=self.args[0])


class DataTableReturnsView(officer.DataTableReturnsOfficerView):
    def get_initial_queryset(self):
        return Return.objects.filter(licence__holder=self.args[0]).exclude(status='future')
