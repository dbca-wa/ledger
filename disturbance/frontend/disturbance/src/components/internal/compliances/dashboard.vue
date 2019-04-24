<template>
<div class="container" id="internalDash">
    <ComplianceDashTable level="internal" :url="compliances_url"/>
</div>
</template>
<script>
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalCompliancesDashboard',
    data() {
        let vm = this;
        return {
            //compliances_url: api_endpoints.compliances,
            compliances_url: api_endpoints.compliances_paginated_external,
        }
    
    },
    watch: {},
    components: {
        ComplianceDashTable,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
