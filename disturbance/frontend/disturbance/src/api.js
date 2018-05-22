//TODO: Need to figure out how to rqead the following from Django .env file
var site_url = 'http://localhost:8499'
//var site_url = 'https://via-dev-internal.dpaw.wa.gov.au/'
//var _site_url = process.env.SITE_URL || 'https://via-uat-internal.dpaw.wa.gov.au/'

module.exports = {
    organisations: '/api/organisations.json',
    organisation_requests: '/api/organisation_requests.json',
    organisation_contacts: '/api/organisation_contacts.json',
    organisation_access_group_members: '/api/organisation_access_group_members',
    users: '/api/users.json',
    profile: '/api/profile',
    department_users: '/api/department_users',
    //other
    countries: "https://restcountries.eu/rest/v1/?fullText=true",
    proposal_type:"/api/proposal_type",
    proposals:"/api/proposal.json",
    approvals:"/api/approvals.json",
    referrals:"/api/referrals.json",
    compliances:"/api/compliances.json",
    proposal_standard_requirements:"/api/proposal_standard_requirements.json",
    proposal_requirements:"/api/proposal_requirements.json",
    amendment_request:"/api/amendment_request.json",
    regions:"/api/regions.json",
    application_types:"/api/application_types.json",
    discard_proposal:function (id) {
      return `/api/proposal/${id}.json`;
    },
    site_url: site_url

}
