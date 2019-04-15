<template>
<div class="container" id="internalDash">
    <ApplicationDashTable level="internal" :url="applications_url"/>
    <AssessmentDashTable v-if="wc_version != 1.0" />
</div>
</template>
<script>
import ApplicationDashTable from '@common-utils/applications_dashboard.vue'
import AssessmentDashTable from '@common-utils/assessments_dashboard.vue'
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
        }
    
    },
    watch: {},
    components: {
        ApplicationDashTable,
        AssessmentDashTable
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
