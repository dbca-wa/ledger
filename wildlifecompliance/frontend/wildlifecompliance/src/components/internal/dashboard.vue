<template>
<div class="container" id="internalDash">
    <ApplicationDashTable level="internal" :url="applications_url"/>
    <ReferralDashTable v-if="wc_version != 1.0" />
    <ReturnDashTable level="internal" :url="returns_url" />

</div>
</template>
<script>
import ApplicationDashTable from '@common-utils/applications_dashboard.vue'
import ReferralDashTable from '@common-utils/referrals_dashboard.vue'
import ReturnDashTable from '@common-utils/returns_dashboard.vue'
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
            applications_url: helpers.add_endpoint_json(api_endpoints.applications,'internal_datatable_list'),
            returns_url:helpers.add_endpoint_json(api_endpoints.returns,'user_list'),
        }
    
    },
    watch: {},
    components: {
        ApplicationDashTable,
        ReferralDashTable,
        ReturnDashTable
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
