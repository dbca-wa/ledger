from django.http import HttpResponse,JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from disturbance.components.proposals.utils import create_data_from_form
from disturbance.components.proposals.models import Proposal, Referral, ProposalType, HelpPage
from disturbance.components.approvals.models import Approval
from disturbance.components.compliances.models import Compliance
import json,traceback

class ProposalView(TemplateView):
    template_name = 'disturbance/proposal.html'

    def post(self, request, *args, **kwargs):
        extracted_fields = []
        #import ipdb; ipdb.set_trace()
        try:
            proposal_id = request.POST.pop('proposal_id')
            proposal = Proposal.objects.get(proposal_id)
            schema = json.loads(request.POST.pop('schema')[0])
            extracted_fields = create_data_from_form(schema,request.POST, request.FILES)
            proposal.schema = schema;
            proposal.data = extracted_fields
            proposal.save()
            return redirect(reverse('external'))
        except:
            traceback.print_exc
            return JsonResponse({error:"something went wrong"},safe=False,status=400)


from reversion_compare.views import HistoryCompareDetailView
class ProposalHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Proposal
    template_name = 'disturbance/reversion_history.html'

class ReferralHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Referral
    template_name = 'disturbance/reversion_history.html'


class ApprovalHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Approval
    template_name = 'disturbance/reversion_history.html'


class ComplianceHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = Compliance
    template_name = 'disturbance/reversion_history.html'



class ProposalTypeHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = ProposalType
    template_name = 'disturbance/reversion_history.html'


class HelpPageHistoryCompareView(HistoryCompareDetailView):
    """
    View for reversion_compare
    """
    model = HelpPage
    template_name = 'disturbance/reversion_history.html'


class PreviewLicencePDFView(View):
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')

        proposal = self.get_object()
        details = json.loads(request.POST.get('formData'))

        response.write(proposal.preview_approval(request, details))
        return response

    def get_object(self):
        return get_object_or_404(Proposal, id=self.kwargs['proposal_pk'])