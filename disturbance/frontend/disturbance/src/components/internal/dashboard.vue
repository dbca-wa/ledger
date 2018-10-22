<template>
<div class="container" id="internalDash">
    <ProposalDashTable level="internal" :url="proposals_url"/>
    <ReferralDashTable />
</div>
</template>
<script>
import ProposalDashTable from '@common-utils/proposals_dashboard.vue'
import ReferralDashTable from '@common-utils/referrals_dashboard.vue'
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
            proposals_url: api_endpoints.proposals,
        }
    
    },
    watch: {},
    components: {
        ProposalDashTable,
        ReferralDashTable
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
