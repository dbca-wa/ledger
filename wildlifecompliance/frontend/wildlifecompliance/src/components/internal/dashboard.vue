<template>
<div class="container" id="internalDash">
    <ApplicationDashTable level="internal" :url="applications_url"/>
    <AssessmentDashTable />
    <ReturnDashTable level="internal" :url="returns_url" />
</div>
</template>
<script>
import ApplicationDashTable from '@common-utils/applications_dashboard.vue'
import AssessmentDashTable from '@common-utils/assessments_dashboard.vue'
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
            applications_url: helpers.add_endpoint_join(api_endpoints.applications_paginated,'internal_datatable_list/?format=datatables'),
            returns_url:helpers.add_endpoint_json(api_endpoints.returns,'user_list'),
        }
    
    },
    watch: {},
    components: {
        ApplicationDashTable,
        AssessmentDashTable,
        ReturnDashTable
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
