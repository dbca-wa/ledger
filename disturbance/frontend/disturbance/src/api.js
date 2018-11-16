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
    //list_proposals:"/api/proposal/list_proposal.json",
    approvals:"/api/approvals.json",
    referrals:"/api/referrals.json",
    compliances:"/api/compliances.json",
    proposal_standard_requirements:"/api/proposal_standard_requirements.json",
    proposal_requirements:"/api/proposal_requirements.json",
    amendment_request:"/api/amendment_request.json",
    regions:"/api/regions.json",
    activity_matrix:"/api/activity_matrix.json",
    application_types:"/api/application_types.json",


    // used in internal and external dashboards
    proposals_paginated_external:   "/api/proposal_paginated/proposals_external/?format=datatables",
    approvals_paginated_external:   "/api/approval_paginated/approvals_external/?format=datatables",
    compliances_paginated_external: "/api/compliance_paginated/compliances_external/?format=datatables",
    proposals_paginated_internal:   "/api/proposal_paginated/proposals_internal/?format=datatables",
    referrals_paginated_internal:   "/api/proposal_paginated/referrals_internal/?format=datatables",
    //filter_list:                    "/api/proposal_paginated/filter_list.json",
    filter_list:                    "/api/proposal/filter_list.json",
    filter_list_approvals:          "/api/approvals/filter_list.json",
    filter_list_compliances:        "/api/compliances/filter_list.json",
    filter_list_referrals:          "/api/referrals/filter_list.json",

    //approvals_paginated:"/api/approvals/user_list_paginated/?format=datatables",
    //compliances_paginated:"/api/compliances/user_list_paginated/?format=datatables",
    //list_proposals:"/api/list_proposal/?format=datatables",
    //list_referrals:"/api/list_proposal/referral_list/?format=datatables",

    discard_proposal:function (id) {
      return `/api/proposal/${id}.json`;
    },
    site_url: site_url,
    //dep_name: 'Department of Biodiversity, Conservation and Attractions',
    //dep_name_short: 'DBCA',
    system_name: 'Disturbance Approval System',
    //system_name_short: 'DAS',

}
