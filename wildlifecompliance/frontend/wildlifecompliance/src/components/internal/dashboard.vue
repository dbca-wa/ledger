<template>
<div class="container" id="internalDash">
    <ApplicationDashTable level="internal" :url="applications_url"/>
    <ReferralDashTable v-if="wc_version != 1.0" />
</div>
</template>
<script>
import ApplicationDashTable from '@common-utils/applications_dashboard.vue'
import ReferralDashTable from '@common-utils/referrals_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalDashboard',
    data() {
        let vm = this;
        return {
            applications_url: api_endpoints.applications,
        }
    
    },
    watch: {},
    components: {
        ApplicationDashTable,
        ReferralDashTable
    },
    computed: {
        wc_version: function (){
            return this.$root.wc_version;
        }
    },
    methods: {},
    mounted: function () {
    }
}
</script>
