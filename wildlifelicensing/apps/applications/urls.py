from django.conf.urls import url

from wildlifelicensing.apps.applications.views.entry import SelectLicenceTypeView, EditApplicationView, \
    CheckIdentificationRequiredView, \
    CreateSelectProfileView, EnterDetailsView, PreviewView

from wildlifelicensing.apps.applications.views.process import ProcessView, AssignOfficerView, SetIDCheckStatusView, \
    IDRequestView, SetCharacterCheckStatusView, SetReviewStatusView, AmendmentRequestView, SendForAssessmentView, \
    RemindAssessmentView, AddLogEntryView, CommunicationLogListView

from wildlifelicensing.apps.applications.views.conditions import EnterConditionsView, SearchConditionsView, \
    CreateConditionView, SetAssessmentConditionState, SubmitConditionsView, EnterConditionsAssessorView, \
    SubmitConditionsAssessorView

from wildlifelicensing.apps.applications.views.issue import IssueLicenceView

urlpatterns = [
    url('^select-licence-type$', SelectLicenceTypeView.as_view(), name='select_licence_type'),
    url('^([\w-]+)/edit-application/([0-9]+)/$', EditApplicationView.as_view(), name='edit_application'),
    url('^([\w-]+)/check_identification/$', CheckIdentificationRequiredView.as_view(), name='check_identification'),
    url('^([\w-]+)/profile/$', CreateSelectProfileView.as_view(), name='create_select_profile'),
    url('^([\w-]+)/profile/([0-9]+)/$', CreateSelectProfileView.as_view(),
        name='create_select_profile_existing_application'),
    url('^([\w-]+)/enter-details/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details_existing_application'),
    url('^([\w-]+)/preview/$', PreviewView.as_view(), name='preview'),
    url('^([\w-]+)/preview/([0-9]+)/$', PreviewView.as_view(), name='preview'),

    # process
    url(r'^process/([0-9]+)/$', ProcessView.as_view(), name='process'),
    url('^assign_officer/$', AssignOfficerView.as_view(), name='assign_officer'),
    url('^set_id_check_status/$', SetIDCheckStatusView.as_view(), name='set_id_check_status'),
    url('^id_request/$', IDRequestView.as_view(), name='id_request'),
    url('^set_character_check_status/$', SetCharacterCheckStatusView.as_view(), name='set_character_check_status'),
    url('^set_review_status/$', SetReviewStatusView.as_view(), name='set_review_status'),
    url('^amendment_request/$', AmendmentRequestView.as_view(), name='amendment_request'),
    url('^send_for_assessment/$', SendForAssessmentView.as_view(), name='send_for_assessment'),
    url('^remind_assessment/$', RemindAssessmentView.as_view(), name='remind_assessment'),
    # communication log
    url('^add_log_entry/([0-9]+)/', AddLogEntryView.as_view(), name='add_log_entry'),
    url('log_list/([0-9]+)/$', CommunicationLogListView.as_view(), name='log_list'),

    # conditions
    url('^enter_conditions/([0-9]+)/$', EnterConditionsView.as_view(), name='enter_conditions'),
    url('^enter_conditions/([0-9]+)/assessment/([0-9]+)/?$', EnterConditionsAssessorView.as_view(),
        name='enter_conditions_assessor'),
    url('^search_conditions/$', SearchConditionsView.as_view(), name='search_conditions'),
    url('^create_condition/$', CreateConditionView.as_view(), name='create_condition'),
    url('^set_assessment_condition_state/$', SetAssessmentConditionState.as_view(), name='set_assessment_condition_state'),
    url('^submit_conditions/([0-9]+)/$', SubmitConditionsView.as_view(), name='submit_conditions'),
    url('^submit_conditions/([0-9]+)/assessment/([0-9]+)/?$', SubmitConditionsAssessorView.as_view(),
        name='submit_conditions_assessor'),

    # issue
    url('^issue_licence/([0-9]+)/$', IssueLicenceView.as_view(), name='issue_licence'),
]
