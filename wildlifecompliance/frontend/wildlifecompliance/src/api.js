var site_url = location.origin

module.exports = {
    organisations: '/api/organisations/',
    organisation_requests: '/api/organisation_requests/',
    organisation_contacts: '/api/organisation_contacts/',
    organisation_access_group_members: '/api/organisation_access_group_members/',
    users: '/api/users/',
    profile: '/api/profile/',
    assessor_group:'/api/assessor_group/',
    emailidentities: '/api/emailidentities/',
    profiles: '/api/profiles/',
    my_profiles: '/api/my_profiles/',
    assessment:'/api/assessment/',
    amendment:'/api/amendment/',
    is_new_user: '/api/is_new_user/',
    user_profile_completed: '/api/user_profile_completed/',
    countries: "https://restcountries.eu/rest/v1/?fullText=true/",
    application_type:"/api/application_type/",
    applications:"/api/application/",
    licences:"/api/licences/",
    call_email:"/api/call_email/",
    returns:"/api/returns/",
    application_standard_conditions:"/api/application_standard_conditions/",
    return_types:"/api/return_types/",
    application_conditions:"/api/application_conditions/",
    discard_application:function (id) {
      return `/api/application/${id}/`;
    },
    site_url: site_url,
    system_name: 'Wildlife Licensing System',
}

