from django.conf.urls import url

from wildlifelicensing.apps.applications.views.entry import DeleteApplicationSessionView, NewApplicationView, \
    SelectLicenceTypeView, CreateSelectCustomer, EditApplicationView, CheckIdentificationRequiredView, \
    CreateSelectProfileView, EnterDetailsView, PreviewView, ApplicationCompleteView, RenewLicenceView, \
    AmendLicenceView, CheckSeniorCardView, DiscardApplicationView

from wildlifelicensing.apps.applications.views.process import ProcessView, AssignOfficerView, SetIDCheckStatusView, \
    IDRequestView, ReturnsRequestView, SetReturnsCheckStatusView, SetCharacterCheckStatusView, \
    SetReviewStatusView, AmendmentRequestView, SendForAssessmentView, RemindAssessmentView

from wildlifelicensing.apps.applications.views.conditions import EnterConditionsView, SearchConditionsView, \
    CreateConditionView, SetAssessmentConditionState, EnterConditionsAssessorView, AssignAssessorView

from wildlifelicensing.apps.applications.views.issue import IssueLicenceView, ReissueLicenceView, PreviewLicenceView

from wildlifelicensing.apps.applications.views.view import ViewReadonlyView, ViewPDFView, ViewReadonlyOfficerView, \
    ViewReadonlyAssessorView, AddApplicationLogEntryView, ApplicationLogListView, ApplicationUserActionListView


urlpatterns = [
    # application entry / licence renewal/amendment
    url('^delete-application-session/$', DeleteApplicationSessionView.as_view(), name='delete_application_session'),
    url('^new-application/$', NewApplicationView.as_view(), name='new_application'),
    url('^select-licence-type$', SelectLicenceTypeView.as_view(), name='select_licence_type'),
    url('^select-licence-type/([0-9]+)$', SelectLicenceTypeView.as_view(), name='select_licence_type'),
    url('^create-select-customer/$', CreateSelectCustomer.as_view(), name='create_select_customer'),
    url('^edit-application/([0-9]+)/$', EditApplicationView.as_view(), name='edit_application'),
    url('^discard-application/([0-9]+)/$', DiscardApplicationView.as_view(), name='discard_application'),
    url('^check-identification/$', CheckIdentificationRequiredView.as_view(), name='check_identification'),
    url('^check-senior-card/$', CheckSeniorCardView.as_view(), name='check_senior_card'),
    url('^profile/$', CreateSelectProfileView.as_view(), name='create_select_profile'),
    url('^enter-details/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^preview/$', PreviewView.as_view(), name='preview'),
    url('^complete/$$', ApplicationCompleteView.as_view(), name='complete'),
    url('^renew-licence/([0-9]+)/$', RenewLicenceView.as_view(), name='renew_licence'),
    url('^amend-licence/([0-9]+)/$', AmendLicenceView.as_view(), name='amend_licence'),

    # process
    url(r'^process/([0-9]+)/$', ProcessView.as_view(), name='process'),
    url('^assign-officer/$', AssignOfficerView.as_view(), name='assign_officer'),
    url('^set-id-check-status/$', SetIDCheckStatusView.as_view(), name='set_id_check_status'),
    url('^id-request/$', IDRequestView.as_view(), name='id_request'),
    url('^returns-request/$', ReturnsRequestView.as_view(), name='returns_request'),
    url('^set-returns-check-status/$', SetReturnsCheckStatusView.as_view(), name='set_returns_check_status'),
    url('^set-character-check-status/$', SetCharacterCheckStatusView.as_view(), name='set_character_check_status'),
    url('^set-review-status/$', SetReviewStatusView.as_view(), name='set_review_status'),
    url('^amendment-request/$', AmendmentRequestView.as_view(), name='amendment_request'),
    url('^send-for-assessment/$', SendForAssessmentView.as_view(), name='send_for_assessment'),
    url('^remind-assessment/$', RemindAssessmentView.as_view(), name='remind_assessment'),

    # communication log
    url('^add-log-entry/([0-9]+)/$', AddApplicationLogEntryView.as_view(), name='add_log_entry'),
    url('^log-list/([0-9]+)/$', ApplicationLogListView.as_view(), name='log_list'),

    # action log
    url('^action-list/([0-9]+)/$', ApplicationUserActionListView.as_view(), name='action_list'),

    # conditions
    url('^enter-conditions/([0-9]+)/$', EnterConditionsView.as_view(), name='enter_conditions'),
    url('^enter-conditions/([0-9]+)/assessment/([0-9]+)/?$', EnterConditionsAssessorView.as_view(),
        name='enter_conditions_assessor'),
    url('^search-conditions/$', SearchConditionsView.as_view(), name='search_conditions'),
    url('^create-condition/([0-9]+)/$', CreateConditionView.as_view(), name='create_condition'),
    url('^enter-conditions/([0-9]+)/assign-officer/$', AssignOfficerView.as_view(), name='assign_officer'),
    url('^set-assessment-condition-state/$', SetAssessmentConditionState.as_view(), name='set_assessment_condition_state'),
    url('^assign-assessor/$', AssignAssessorView.as_view(), name='assign_assessor'),

    # issue
    url('^issue-licence/([0-9]+)/$', IssueLicenceView.as_view(), name='issue_licence'),
    url('^reissue-licence/([0-9]+)/$', ReissueLicenceView.as_view(), name='reissue_licence'),
    url('^preview-licence/([0-9]+)/$', PreviewLicenceView.as_view(), name='preview_licence'),

    # view
    url('^view-application/([0-9]+)/$', ViewReadonlyView.as_view(), name='view_application'),
    url('^view-application-pdf/([0-9]+)/$', ViewPDFView.as_view(), name='view_application_pdf'),
    url('^view-application-officer/([0-9]+)/$', ViewReadonlyOfficerView.as_view(), name='view_application_officer'),
    url('^view-assessment/([0-9]+)/assessment/([0-9]+)/$', ViewReadonlyAssessorView.as_view(), name='view_assessment')
]
