module.exports = {
    organisations: '/api/organisations.json',
    organisation_requests: '/api/organisation_requests.json',
    organisation_contacts: '/api/organisation_contacts.json',
    organisation_access_group_members: '/api/organisation_access_group_members',
    users: '/api/users.json',
    profile: '/api/profile',
    profiles: '/api/profiles',
    department_users: '/api/department_users',
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
