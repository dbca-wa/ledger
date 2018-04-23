module.exports = {
    organisations: '/api/organisations.json',
    organisation_requests: '/api/organisation_requests.json',
    organisation_contacts: '/api/organisation_contacts.json',
    organisation_access_group_members: '/api/organisation_access_group_members',
    users: '/api/users',
    profile: '/api/profile',
    emailidentities: '/api/emailidentities',
    profiles: '/api/profiles',
    my_profiles: '/api/my_profiles',
    department_users: '/api/department_users',
    is_new_user: '/api/is_new_user',
    user_profile_completed: '/api/user_profile_completed',
    //other
    countries: "https://restcountries.eu/rest/v1/?fullText=true",
    application_type:"/api/application_type",
    applications:"/api/application.json",
    licences:"/api/licences.json",
    referrals:"/api/referrals.json",
    returns:"/api/returns.json",
    application_standard_conditions:"/api/application_standard_conditions.json",
    application_conditions:"/api/application_conditions.json",
    discard_application:function (id) {
      return `/api/application/${id}.json`;
    }

}
