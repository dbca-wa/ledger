from datetime import date

from django.template.context_processors import csrf
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.utils import formats

from reversion import revisions
from reversion.models import Version
from preserialize.serialize import serialize

from ledger.accounts.models import EmailUser, Document

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrAssessorRequiredMixin
from wildlifelicensing.apps.main.helpers import get_all_officers, render_user_name
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.applications.models import Application, AmendmentRequest, Assessment, ApplicationUserAction
from wildlifelicensing.apps.applications.forms import IDRequestForm, ReturnsRequestForm, AmendmentRequestForm, \
    ApplicationLogEntryForm, ApplicationDeclinedDetailsForm
from wildlifelicensing.apps.applications.emails import send_amendment_requested_email, send_assessment_requested_email, \
    send_id_update_request_email, send_returns_request_email, send_assessment_reminder_email, \
    send_application_declined_email
from wildlifelicensing.apps.main.models import AssessorGroup
from wildlifelicensing.apps.returns.models import Return

from wildlifelicensing.apps.payments import utils as payment_utils

from wildlifelicensing.apps.applications.utils import PROCESSING_STATUSES, ID_CHECK_STATUSES, RETURNS_CHECK_STATUSES, \
    CHARACTER_CHECK_STATUSES, REVIEW_STATUSES, convert_documents_to_url, format_application, get_log_entry_to, \
    format_amendment_request, format_assessment, append_app_document_to_schema_data


class ProcessView(OfficerOrAssessorRequiredMixin, TemplateView):
    template_name = 'wl/process/process_app.html'

    def _build_data(self, request, application):
        officers = [{'id': officer.id, 'text': render_user_name(officer)} for officer in get_all_officers()]
        officers.insert(0, {'id': 0, 'text': 'Unassigned'})

        current_ass_groups = [ass_request.assessor_group for ass_request in
                              Assessment.objects.filter(application=application)]

        ass_groups = [{'id': ass_group.id, 'text': ass_group.name} for ass_group in
                      AssessorGroup.objects.all().exclude(id__in=[ass_group.pk for ass_group in current_ass_groups]).
                          order_by('name')]

        # extract and format the previous lodgements of the application
        previous_lodgements = []
        for revision in Version.objects.get_for_object(application).filter(revision__comment='Details Modified').order_by(
                '-revision__date_created'):
            previous_lodgement = revision._object_version.object

            if previous_lodgement.hard_copy is not None:
                previous_lodgement.licence_type.application_schema, previous_lodgement.data = \
                    append_app_document_to_schema_data(previous_lodgement.licence_type.application_schema,
                                                       previous_lodgement.data,
                                                       previous_lodgement.hard_copy.file.url)

            # reversion won't reference the previous many-to-many sets, only the latest one, so need to get documents as per below
            previous_lodgement_documents = Document.objects.filter(pk__in=revision.field_dict['documents'])

            convert_documents_to_url(previous_lodgement.data, previous_lodgement_documents, '')
            previous_lodgements.append({'lodgement_number': '{}-{}'.format(previous_lodgement.lodgement_number,
                                                                           previous_lodgement.lodgement_sequence),
                                        'date': formats.date_format(revision.revision.date_created, 'd/m/Y', True),
                                        'data': previous_lodgement.data})

        previous_application_returns_outstanding = False
        if application.previous_application is not None:
            previous_application_returns_outstanding = Return.objects.filter(
                licence=application.previous_application.licence). \
                exclude(status='accepted').exclude(status='submitted').exists()

        if application.hard_copy is not None:
            application.licence_type.application_schema, application.data = \
                append_app_document_to_schema_data(application.licence_type.application_schema, application.data,
                                                   application.hard_copy.file.url)

        convert_documents_to_url(application.data, application.documents.all(), '')

        data = {
            'user': serialize(request.user, exclude='residential_address'),
            #'application': serialize(application, posthook=format_application),
            'application': serialize(application,posthook=format_application,
                                        related={
                                            'applicant': {'exclude': ['residential_address','postal_address','billing_address']},
                                            'applicant_profile':{'fields':['email','id','institution','name']},
                                            'previous_application':{'exclude':['applicant','applicant_profile','previous_application','licence']},
                                            'licence':{'related':{
                                               'holder':{'exclude': ['residential_address','postal_address','billing_address']},
                                               'issuer':{'exclude': ['residential_address','postal_address','billing_address']},
                                               'profile':{'related': {'user': {'exclude': ['residential_address','postal_address','billing_address']}},
                                                   'exclude': ['postal_address']}
                                               },'exclude':['holder','issuer','profile','licence_ptr']}
                                        }),
            'form_structure': application.licence_type.application_schema,
            'officers': officers,
            'amendment_requests': serialize(AmendmentRequest.objects.filter(application=application),
                                            posthook=format_amendment_request),
            'assessor_groups': ass_groups,
            'assessments': serialize(Assessment.objects.filter(application=application),
                                     posthook=format_assessment,exclude=['application','applicationrequest_ptr'],
                                     related={'assessor_group':{'related':{'members':{'exclude':['residential_address']}}},
                                         'officer':{'exclude':['residential_address']},
                                         'assigned_assessor':{'exclude':['residential_address']}}),
            'previous_versions': serialize(previous_lodgements),
            'returns_outstanding': previous_application_returns_outstanding,
            'payment_status': payment_utils.PAYMENT_STATUSES.get(payment_utils.
                                                                 get_application_payment_status(application)),
            'csrf_token': str(csrf(request).get('csrf_token'))
        }

        return data

    def _process_decline(self, application):
        request = self.request
        mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST['application'] = application.pk
        request.POST._mutable = mutable
        if 'officer' not in request.POST:
            request.POST['officer'] = request.user.pk
        form = ApplicationDeclinedDetailsForm(request.POST)
        if form.is_valid():
            details = form.save()
            application.customer_status = 'declined'
            application.processing_status = 'declined'
            Assessment.objects.filter(application=application, status='awaiting_assessment'). \
                update(status='assessment_expired')
            application.save()
            application.log_user_action(
                ApplicationUserAction.ACTION_DECLINE_APPLICATION,
                request
            )
            recipient = send_application_declined_email(details, request)
            return True, "Application declined and email sent to {}".format(recipient)
        else:
            return False, str(form.errors)

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])
        if 'data' not in kwargs:
            kwargs['data'] = self._build_data(self.request, application)
        kwargs['id_request_form'] = IDRequestForm(application=application, officer=self.request.user)
        kwargs['returns_request_form'] = ReturnsRequestForm(application=application, officer=self.request.user)
        kwargs['amendment_request_form'] = AmendmentRequestForm(application=application, officer=self.request.user)
        kwargs['log_entry_form'] = ApplicationLogEntryForm(to=get_log_entry_to(application),
                                                           fromm=self.request.user.get_full_name())
        kwargs['application_declined_details_form'] = \
            ApplicationDeclinedDetailsForm(application=application, officer=self.request.user)

        return super(ProcessView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        if 'enterConditions' in request.POST:
            application.processing_status = 'ready_for_conditions'
            application.save()

            return redirect('wl_applications:enter_conditions', *args, **kwargs)
        elif 'decline' in request.POST:
            success, message = self._process_decline(application)
            if success:
                messages.success(request, message)
                return redirect('wl_dashboard:tables_applications_officer')
            else:
                messages.error(request, "Error while declining application: " + message)
                return redirect('wl_applications:process', application.pk, **kwargs)
        else:
            return redirect('wl_applications:process', application.pk, **kwargs)


class AssignOfficerView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])

        try:
            application.assigned_officer = EmailUser.objects.get(pk=request.POST['userID'])
        except EmailUser.DoesNotExist:
            application.assigned_officer = None

        application.processing_status = determine_processing_status(application)
        application.save()

        if application.assigned_officer is not None:
            name = render_user_name(application.assigned_officer)
            assigned_officer = {'id': application.assigned_officer.id, 'text': name}
            application.log_user_action(
                ApplicationUserAction.ACTION_ASSIGN_TO_.format(name),
                request)
        else:
            assigned_officer = {'id': 0, 'text': 'Unassigned'}
            application.log_user_action(
                ApplicationUserAction.ACTION_UNASSIGN,
                request)

        return JsonResponse({'assigned_officer': assigned_officer,
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetIDCheckStatusView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        previous_status = application.id_check_status
        application.id_check_status = request.POST['status']

        application.customer_status = determine_customer_status(application)
        application.processing_status = determine_processing_status(application)
        application.save()

        if application.id_check_status != previous_status:
            # log action
            status = application.id_check_status
            user_action = "ID check:" + status  # default action
            if status == 'accepted':
                user_action = ApplicationUserAction.ACTION_ACCEPT_ID
            elif status == 'not_checked':
                user_action = ApplicationUserAction.ACTION_RESET_ID
            application.log_user_action(user_action, request)

        return JsonResponse({'id_check_status': ID_CHECK_STATUSES[application.id_check_status],
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


class IDRequestView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id_request_form = IDRequestForm(request.POST)
        if id_request_form.is_valid():
            id_request = id_request_form.save()

            application = id_request.application
            application.id_check_status = 'awaiting_update'
            application.customer_status = determine_customer_status(application)
            application.processing_status = determine_processing_status(application)
            application.save()
            application.log_user_action(ApplicationUserAction.ACTION_ID_REQUEST_UPDATE, request)
            send_id_update_request_email(id_request, request)

            response = {'id_check_status': ID_CHECK_STATUSES[application.id_check_status],
                        'processing_status': PROCESSING_STATUSES[application.processing_status]}

            return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)
        else:
            return JsonResponse(id_request_form.errors, safe=False, encoder=WildlifeLicensingJSONEncoder)


class ReturnsRequestView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        returns_request_form = ReturnsRequestForm(request.POST)
        if returns_request_form.is_valid():
            returns_request = returns_request_form.save()

            application = returns_request.application
            application.returns_check_status = 'awaiting_returns'
            application.customer_status = determine_customer_status(application)
            application.processing_status = determine_processing_status(application)
            application.save()
            send_returns_request_email(returns_request, request)

            response = {'returns_check_status': RETURNS_CHECK_STATUSES[application.returns_check_status],
                        'processing_status': PROCESSING_STATUSES[application.processing_status]}

            return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)
        else:
            return JsonResponse(returns_request_form.errors, safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetReturnsCheckStatusView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        application.returns_check_status = request.POST['status']

        application.customer_status = determine_customer_status(application)
        application.processing_status = determine_processing_status(application)
        application.save()

        return JsonResponse({'returns_check_status': CHARACTER_CHECK_STATUSES[application.returns_check_status],
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetCharacterCheckStatusView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        previous_status = application.character_check_status
        application.character_check_status = request.POST['status']

        application.processing_status = determine_processing_status(application)
        application.save()

        if application.character_check_status != previous_status:
            # log action
            status = application.character_check_status
            user_action = "Character check:" + status  # default action
            if status == 'accepted':
                user_action = ApplicationUserAction.ACTION_ACCEPT_CHARACTER
            elif status == 'not_checked':
                user_action = ApplicationUserAction.ACTION_RESET_CHARACTER
            application.log_user_action(user_action, request)

        return JsonResponse({'character_check_status': CHARACTER_CHECK_STATUSES[application.character_check_status],
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetReviewStatusView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        previous_status = application.review_status
        application.review_status = request.POST['status']

        application.customer_status = determine_customer_status(application)
        application.processing_status = determine_processing_status(application)
        application.save()

        if application.review_status != previous_status:
            # log action
            status = application.review_status
            user_action = "Character check:" + status  # default action
            if status == 'accepted':
                user_action = ApplicationUserAction.ACTION_ACCEPT_REVIEW
            elif status == 'not_reviewed':
                user_action = ApplicationUserAction.ACTION_RESET_REVIEW
            application.log_user_action(user_action, request)

        response = {'review_status': REVIEW_STATUSES[application.review_status],
                    'processing_status': PROCESSING_STATUSES[application.processing_status]}

        return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)


class AmendmentRequestView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        amendment_request_form = AmendmentRequestForm(request.POST)
        if amendment_request_form.is_valid():
            amendment_request = amendment_request_form.save()

            application = amendment_request.application
            application.review_status = 'awaiting_amendments'
            application.customer_status = determine_customer_status(application)
            application.processing_status = determine_processing_status(application)
            application.save()
            application.log_user_action(ApplicationUserAction.ACTION_ID_REQUEST_AMENDMENTS, request)
            send_amendment_requested_email(amendment_request, request=request)

            response = {'review_status': REVIEW_STATUSES[application.review_status],
                        'processing_status': PROCESSING_STATUSES[application.processing_status],
                        'amendment_request': serialize(amendment_request, posthook=format_amendment_request)}

            return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)
        else:
            return JsonResponse(amendment_request_form.errors, safe=False, encoder=WildlifeLicensingJSONEncoder)


class SendForAssessmentView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])

        ass_group = get_object_or_404(AssessorGroup, pk=request.POST['assGroupID'])
        assessment = Assessment.objects.get_or_create(
            application=application,
            assessor_group=ass_group,
            defaults={
                'officer': self.request.user
            }
        )[0]

        assessment.status = 'awaiting_assessment'

        assessment.save()

        application.processing_status = determine_processing_status(application)
        application.save()
        application.log_user_action(
            ApplicationUserAction.ACTION_SEND_FOR_ASSESSMENT_TO_.format(ass_group),
            request)

        send_assessment_requested_email(assessment, request)

        # need to only set and save this after the email was sent in case the email fails whereby it should remain null
        assessment.date_last_reminded = date.today()

        assessment.save()

        return JsonResponse({'assessment': serialize(assessment, posthook=format_assessment,exclude=['application','applicationrequest_ptr'],
                                                                 related={'assessor_group':{'related':{'members':{'exclude':['residential_address']}}},
                                                                     'officer':{'exclude':['residential_address']},
                                                                     'assigned_assessor':{'exclude':['residential_address']}}),
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


class RemindAssessmentView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        assessment = get_object_or_404(Assessment, pk=request.POST['assessmentID'])

        assessment.application.log_user_action(
            ApplicationUserAction.ACTION_SEND_ASSESSMENT_REMINDER_TO_.format(assessment.assessor_group),
            request
        )

        send_assessment_reminder_email(assessment, request)

        assessment.date_last_reminded = date.today()

        assessment.save()

        return JsonResponse('ok', safe=False, encoder=WildlifeLicensingJSONEncoder)


def determine_processing_status(application):
    status = 'ready_for_action'

    if application.id_check_status == 'awaiting_update' or application.review_status == 'awaiting_amendments':
        status = 'awaiting_applicant_response'

    if Assessment.objects.filter(application=application).filter(status='awaiting_assessment').exists():
        if status == 'awaiting_applicant_response':
            status = 'awaiting_responses'
        else:
            status = 'awaiting_assessor_response'

    return status


def determine_customer_status(application):
    status = 'under_review'

    if application.id_check_status == 'awaiting_update':
        if application.returns_check_status == 'awaiting_returns':
            if application.review_status == 'awaiting_amendments':
                status = 'id_and_returns_and_amendment_required'
            else:
                status = 'id_and_returns_required'
        elif application.review_status == 'awaiting_amendments':
            status = 'id_and_amendment_required'
        else:
            status = 'id_required'
    elif application.returns_check_status == 'awaiting_returns':
        if application.review_status == 'awaiting_amendments':
            status = 'returns_and_amendments_required'
        else:
            status = 'returns_required'
    elif application.review_status == 'awaiting_amendments':
        status = 'amendment_required'

    return status
