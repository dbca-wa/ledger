from django.conf.urls import url

from wildlifelicensing.apps.applications.views.entry import SelectLicenceTypeView, EditApplicationView, CheckIdentificationRequiredView, \
    CreateSelectProfileView, EnterDetailsView, PreviewView

from wildlifelicensing.apps.applications.views.process import ProcessView, AssignOfficerView, SetIDCheckStatusView, SetCharacterCheckStatusView, \
    SetReviewStatusView, SendForAssessmentView

from wildlifelicensing.apps.applications.views.conditions import EnterConditionsView, SearchConditionsView


urlpatterns = [
    url('^select-licence-type$', SelectLicenceTypeView.as_view(), name='select_licence_type'),
    url('^([\w-]+)/edit-application/([0-9]+)/$', EditApplicationView.as_view(), name='edit_application'),
    url('^([\w-]+)/check_identification/$', CheckIdentificationRequiredView.as_view(), name='check_identification'),
    url('^([\w-]+)/profile/$', CreateSelectProfileView.as_view(), name='create_select_profile'),
    url('^([\w-]+)/profile/([0-9]+)/$', CreateSelectProfileView.as_view(), name='create_select_profile_existing_application'),
    url('^([\w-]+)/enter-details/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details_existing_application'),
    url('^([\w-]+)/preview/$', PreviewView.as_view(), name='preview'),
    url('^([\w-]+)/preview/([0-9]+)/$', PreviewView.as_view(), name='preview'),

    # process
    url(r'^process/([0-9]+)/$', ProcessView.as_view(), name='process'),
    url('^assign_officer/$', AssignOfficerView.as_view(), name='assign_officer'),
    url('^set_id_check_status/$', SetIDCheckStatusView.as_view(), name='set_id_check_status'),
    url('^set_character_check_status/$', SetCharacterCheckStatusView.as_view(), name='set_character_check_status'),
    url('^set_review_status/$', SetReviewStatusView.as_view(), name='set_review_status'),
    url('^send_for_assessment/$', SendForAssessmentView.as_view(), name='send_for_assessment'),

    # conditions
    url('^enter_conditions/([0-9]+)/$', EnterConditionsView.as_view(), name='enter_conditions'),
    url('^search_conditions/$', SearchConditionsView.as_view(), name='search_conditions'),
]
