from django.contrib import messages
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView
from django.core.urlresolvers import reverse_lazy

from preserialize.serialize import serialize

from ledger.accounts.models import EmailUser

from wildlifelicensing.apps.payments import utils as payment_utils
from wildlifelicensing.apps.main.models import Condition
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrAssessorRequiredMixin
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.applications.models import Application, ApplicationCondition, Assessment, \
    AssessmentCondition, ApplicationUserAction
from wildlifelicensing.apps.applications.utils import append_app_document_to_schema_data, convert_documents_to_url, \
    get_log_entry_to, format_application, format_assessment, ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES
from wildlifelicensing.apps.applications.emails import send_assessment_done_email, send_assessment_assigned_email
from wildlifelicensing.apps.applications.views.process import determine_processing_status
from wildlifelicensing.apps.applications.mixins import CanPerformAssessmentMixin
from wildlifelicensing.apps.applications.forms import ApplicationLogEntryForm


class EnterConditionsView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/conditions/enter_conditions.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        if application.hard_copy is not None:
            application.licence_type.application_schema, application.data = \
                append_app_document_to_schema_data(application.licence_type.application_schema, application.data,
                                                   application.hard_copy.file.url)

        convert_documents_to_url(application.data, application.documents.all(), '')

        #kwargs['application'] = serialize(application, posthook=format_application)
        kwargs['application'] = serialize(application,posthook=format_application,related={'applicant': {'exclude': ['residential_address','postal_address','billing_address']},'applicant_profile':{'fields':['email','id','institution','name']},'previous_application':{'exclude':['applicant','applicant_profile','previous_application','licence']}})
        kwargs['form_structure'] = application.licence_type.application_schema
        kwargs['assessments'] = serialize(Assessment.objects.filter(application=application),
                                          posthook=format_assessment,exclude=['application','applicationrequest_ptr'],
                                          related={'assessor_group':{'related':{'members':{'exclude':['residential_address']}}},
                                              'officer':{'exclude':['residential_address']},
                                              'assigned_assessor':{'exclude':['residential_address']}})

        kwargs['log_entry_form'] = ApplicationLogEntryForm(to=get_log_entry_to(application),
                                                           fromm=self.request.user.get_full_name())

        kwargs['payment_status'] = payment_utils.PAYMENT_STATUSES.get(payment_utils.
                                                                      get_application_payment_status(application))

        return super(EnterConditionsView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        if application.processing_status not in ['issued', 'declined'] and request.POST.get('submissionType') != 'save':
            application.processing_status = 'ready_to_issue'

        # remove existing conditions as there may be new conditions and/or changes of order
        application.conditions.clear()

        application.save()
        application.log_user_action(
            ApplicationUserAction.ACTION_ENTER_CONDITIONS,
            request)

        for order, condition_id in enumerate(request.POST.getlist('conditionID')):
            ApplicationCondition.objects.create(condition=Condition.objects.get(pk=condition_id),
                                                application=application, order=order)

        if request.POST.get('submissionType') == 'backToProcessing':
            return redirect('wl_applications:process', *args)
        elif request.POST.get('submissionType') == 'save':
            messages.warning(request, 'Conditions saved')
            return render(request, self.template_name, self.get_context_data())
        else:
            return redirect('wl_applications:issue_licence', *args, **kwargs)


class EnterConditionsAssessorView(CanPerformAssessmentMixin, TemplateView):
    template_name = 'wl/conditions/assessor_enter_conditions.html'
    success_url = reverse_lazy('wl_dashboard:home')

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])
        assessment = get_object_or_404(Assessment, pk=self.args[1])

        if application.hard_copy is not None:
            application.licence_type.application_schema, application.data = \
                append_app_document_to_schema_data(application.licence_type.application_schema, application.data,
                                                   application.hard_copy.file.url)

        convert_documents_to_url(application.data, application.documents.all(), '')

        #kwargs['application'] = serialize(application, posthook=format_application)
        kwargs['application'] = serialize(application,posthook=format_application,related={'applicant': {'exclude': ['residential_address','postal_address','billing_address']},'applicant_profile':{'fields':['email','id','institution','name']}})
        kwargs['form_structure'] = application.licence_type.application_schema

        kwargs['assessment'] = serialize(assessment, post_hook=format_assessment,
                                            exclude=['application','applicationrequest_ptr'],
                                            related={'assessor_group':{'related':{'members':{'exclude':['residential_address']}}},
                                                'officer':{'exclude':['residential_address']},
                                                'assigned_assessor':{'exclude':['residential_address']}})

        kwargs['other_assessments'] = serialize(Assessment.objects.filter(application=application).exclude(id=assessment.id).order_by('id'),
                                                posthook=format_assessment,exclude=['application','applicationrequest_ptr'],
                                                related={'assessor_group':{'related':{'members':{'exclude':['residential_address']}}},
                                                    'officer':{'exclude':['residential_address']},
                                                    'assigned_assessor':{'exclude':['residential_address']}})

        assessors = [{'id': assessor.id, 'text': assessor.get_full_name()} for assessor in
                     assessment.assessor_group.members.all().order_by('first_name')]
        assessors.insert(0, {'id': 0, 'text': 'Unassigned'})

        kwargs['assessors'] = assessors

        kwargs['log_entry_form'] = ApplicationLogEntryForm(to=get_log_entry_to(application),
                                                           fromm=self.request.user.get_full_name())

        return super(EnterConditionsAssessorView, self).get_context_data(**kwargs)

    def _check_read_only(self, assessment, request):
        if assessment.status == 'assessed':
            messages.warning(request, """This assessment has already been concluded and may only be viewed in
            read-only mode.""")
            return True
        elif assessment.status == 'assessment_expired':
            messages.warning(request, """The assessment period for this application has expired, likely due to the
                application having been issued or declined. The assessment may only be viewed in read-only mode""")
            return True

        return False

    def get(self, request, *args, **kwargs):
        assessment = get_object_or_404(Assessment, pk=args[1])

        if self._check_read_only(assessment, request):
            return redirect('wl_applications:view_assessment', *args)

        return super(EnterConditionsAssessorView, self).get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])
        assessment = get_object_or_404(Assessment, pk=self.args[1])

        if self._check_read_only(assessment, request):
            return redirect('wl_applications:view_assessment', *args)

        assessment.assessmentcondition_set.all().delete()
        for order, condition_id in enumerate(request.POST.getlist('conditionID')):
            AssessmentCondition.objects.create(condition=Condition.objects.get(pk=condition_id),
                                               assessment=assessment, order=order)

        # set the assessment request status to be 'assessed' if concluding
        user_action = ApplicationUserAction.ACTION_SAVE_ASSESSMENT_
        if 'conclude' in request.POST:
            assessment.status = 'assessed'
            user_action = ApplicationUserAction.ACTION_CONCLUDE_ASSESSMENT_
        application.log_user_action(
            user_action.format(assessment.assessor_group),
            request)

        comment = request.POST.get('comment', '')
        if len(comment.strip()) > 0:
            assessment.comment = comment

        purpose = request.POST.get('purpose', '')
        if len(purpose.strip()) > 0:
            assessment.purpose = purpose

        assessment.save()

        # set application status process
        application.processing_status = determine_processing_status(application)
        application.save()

        if 'conclude' in request.POST:
            send_assessment_done_email(assessment, request)

            messages.success(request, 'The application assessment has been forwarded back to the Wildlife Licensing '
                                      'office for review.')

            return redirect(self.success_url)
        else:
            messages.warning(request, 'The application assessment was saved.')

            return render(request, self.template_name, self.get_context_data())


class SearchConditionsView(OfficerOrAssessorRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')

        if query is not None:
            q = (Q(code__icontains=query) | Q(text__icontains=query)) & Q(one_off=False)
            qs = Condition.objects.filter(q)
        else:
            qs = Condition.objects.none()
        conditions = serialize(qs)

        return JsonResponse(conditions, safe=False, encoder=WildlifeLicensingJSONEncoder)


class CreateConditionView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            condition = Condition.objects.create(code=request.POST.get('code'), text=request.POST.get('text'),
                                                 one_off=not request.POST.get('addToGeneralList', False))
            if len(self.args) > 0:
                application = get_object_or_404(Application, pk=self.args[0])
                application.log_user_action(
                    ApplicationUserAction.ACTION_CREATE_CONDITION_.format(condition),
                    request
                )
            response = serialize(condition)
        except IntegrityError:
            response = 'This code has already been used. Please enter a unique code.'

        return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetAssessmentConditionState(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        assessment_condition = get_object_or_404(AssessmentCondition, pk=request.POST.get('assessmentConditionID'))

        assessment_condition.acceptance_status = request.POST.get('acceptanceStatus')
        assessment_condition.save()

        response = ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES[assessment_condition.acceptance_status]

        return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)


class AssignAssessorView(OfficerOrAssessorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        assessment = get_object_or_404(Assessment, pk=request.POST['assessmentID'])

        try:
            assessment.assigned_assessor = EmailUser.objects.get(pk=request.POST['userID'])
        except EmailUser.DoesNotExist:
            assessment.assigned_assessor = None

        assessment.save()

        if assessment.assigned_assessor is not None:
            name = assessment.assigned_assessor.get_full_name()
            assigned_assessor = {'id': assessment.assigned_assessor.id, 'text': name}
            assessment.application.log_user_action(
                ApplicationUserAction.ACTION_ASSESSMENT_ASSIGN_TO_.format(name),
                request)
            if assessment.assigned_assessor != request.user:
                send_assessment_assigned_email(assessment, request)
        else:
            assigned_assessor = {'id': 0, 'text': 'Unassigned'}
            assessment.application.log_user_action(
                ApplicationUserAction.ACTION_ASSESSMENT_UNASSIGN,
                request)

        return JsonResponse({'assigned_assessor': assigned_assessor},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)
