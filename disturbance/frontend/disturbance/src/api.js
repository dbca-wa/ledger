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
    referrals:"/api/referrals.json",
    discard_proposal:function (id) {
      return `/api/proposal/${id}.json`;
    }

}
