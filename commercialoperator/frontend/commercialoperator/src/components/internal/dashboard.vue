<template>
<div class="container" id="internalDash">
    <ProposalDashTable level="internal" :url="proposals_url"/>
    <ReferralDashTable :url="referrals_url"/>
    <QAOfficerDashTable v-if="is_qaofficer" level="internal" :url="qaofficer_url"/>
</div>
</template>
<script>
import ProposalDashTable from '@common-utils/proposals_dashboard.vue'
import ReferralDashTable from '@common-utils/referrals_dashboard.vue'
import QAOfficerDashTable from '@common-utils/qaofficer_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'ExternalDashboard',
    data() {
        let vm = this;
        return {
            proposals_url: api_endpoints.proposals_paginated_internal,
            referrals_url: api_endpoints.referrals_paginated_internal,
            qaofficer_url: api_endpoints.qaofficer_paginated_internal,
            is_qaofficer: false,
        }
    
    },
    watch: {},
    components: {
        ProposalDashTable,
        ReferralDashTable,
        QAOfficerDashTable
    },
    computed: {
        dashboard_url: function(){
            return '/api/proposal_paginated/qaofficer_info/'
        },
    },
    methods: {
        check_qaofficer_membership: function(){
            let vm = this;

            //vm.$http.get(api_endpoints.filter_list).then((response) => {
            vm.$http.get(vm.dashboard_url).then((response) => {
                vm.is_qaofficer = response.body.data['QA_Officer'];
            },(error) => {
                console.log(error);
            })
        },
    },
    mounted: function () {
        this.check_qaofficer_membership();
    }
}
</script>
