from django.conf.urls import url

from wildlifelicensing.apps.applications.views.entry import NewApplicationView, SelectLicenceTypeView, \
    CreateSelectCustomer, EditApplicationView, CheckIdentificationRequiredView, CreateSelectProfileView, \
    EnterDetailsView, PreviewView, RenewLicenceView

from wildlifelicensing.apps.applications.views.process import ProcessView, AssignOfficerView, SetIDCheckStatusView, \
    IDRequestView, ReturnsRequestView, SetReturnsCheckStatusView, SetCharacterCheckStatusView, \
    SetReviewStatusView, AmendmentRequestView, SendForAssessmentView, RemindAssessmentView

from wildlifelicensing.apps.applications.views.conditions import EnterConditionsView, SearchConditionsView, \
    CreateConditionView, SetAssessmentConditionState, SubmitConditionsView, EnterConditionsAssessorView, \
    SubmitConditionsAssessorView

from wildlifelicensing.apps.applications.views.issue import IssueLicenceView, ReissueLicenceView, PreviewLicenceView

from wildlifelicensing.apps.applications.views.view import ViewReadonlyView, AssessorConditionsView, \
    AddApplicationLogEntryView, ApplicationLogListView


urlpatterns = [
    # application entry / licence renewal
    url('^new-application/$', NewApplicationView.as_view(), name='new_application'),
    url('^select-licence-type$', SelectLicenceTypeView.as_view(), name='select_licence_type'),
    url('^create-select-customer/$', CreateSelectCustomer.as_view(), name='create_select_customer'),
#     url('^([\w-]+)/edit-application/([0-9]+)/$', EditApplicationView.as_view(), name='edit_application'),
    url('^edit-application/([0-9]+)/$', EditApplicationView.as_view(), name='edit_application'),
#     url('^([\w-]+)/check-identification/$', CheckIdentificationRequiredView.as_view(), name='check_identification'),
    url('^check-identification/$', CheckIdentificationRequiredView.as_view(), name='check_identification'),
#     url('^([\w-]+)/profile/$', CreateSelectProfileView.as_view(), name='create_select_profile'),
    url('^profile/$', CreateSelectProfileView.as_view(), name='create_select_profile'),
#     url('^([\w-]+)/profile/([0-9]+)/$', CreateSelectProfileView.as_view(),
#         name='create_select_profile_existing_application'),
    url('^([\w-]+)/enter-details/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details_existing_application'),
    url('^([\w-]+)/preview/$', PreviewView.as_view(), name='preview'),
    url('^([\w-]+)/preview/([0-9]+)/$', PreviewView.as_view(), name='preview'),
    url('^renew-licence/([0-9]+)/$', RenewLicenceView.as_view(), name='renew_licence'),

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

    # conditions
    url('^enter-conditions/([0-9]+)/$', EnterConditionsView.as_view(), name='enter_conditions'),
    url('^enter-conditions/([0-9]+)/assessment/([0-9]+)/?$', EnterConditionsAssessorView.as_view(),
        name='enter_conditions_assessor'),
    url('^search-conditions/$', SearchConditionsView.as_view(), name='search_conditions'),
    url('^create-condition/$', CreateConditionView.as_view(), name='create_condition'),
    url('^set-assessment-condition-state/$', SetAssessmentConditionState.as_view(), name='set_assessment_condition_state'),
    url('^submit-conditions/([0-9]+)/$', SubmitConditionsView.as_view(), name='submit_conditions'),
    url('^submit-conditions/([0-9]+)/assessment/([0-9]+)/?$', SubmitConditionsAssessorView.as_view(),
        name='submit_conditions_assessor'),

    # issue
    url('^issue-licence/([0-9]+)/$', IssueLicenceView.as_view(), name='issue_licence'),
    url('^reissue-licence/([0-9]+)/$', ReissueLicenceView.as_view(), name='reissue_licence'),
    url('^preview-licence/([0-9]+)/$', PreviewLicenceView.as_view(), name='preview_licence'),

    # view
    url('^view-application/([0-9]+)/$', ViewReadonlyView.as_view(), name='view_application'),
    url('^view-assessment/([0-9]+)/assessment/([0-9]+)/$', AssessorConditionsView.as_view(), name='view_assessment')
]
