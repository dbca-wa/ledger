var site_url = location.origin

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
    proposals_paginated:"/api/proposal/user_list_paginated/?format=datatables",
    proposals_paginated_internal:"/api/proposal/list_paginated/?format=datatables",
    list_proposals:"/api/proposal/list_proposal.json",
    approvals:"/api/approvals.json",
    approvals_paginated:"/api/approvals/user_list_paginated/?format=datatables",
    referrals:"/api/referrals.json",
    compliances:"/api/compliances.json",
    compliances_paginated:"/api/compliances/user_list_paginated/?format=datatables",
    proposal_standard_requirements:"/api/proposal_standard_requirements.json",
    proposal_requirements:"/api/proposal_requirements.json",
    amendment_request:"/api/amendment_request.json",
    regions:"/api/regions.json",
    activity_matrix:"/api/activity_matrix.json",
    application_types:"/api/application_types.json",
    discard_proposal:function (id) {
      return `/api/proposal/${id}.json`;
    },
    site_url: site_url

}
