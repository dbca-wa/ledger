<template>
<div class="container" id="internalDash">
    <ApprovalDashTable level="internal" :url="approvals_url"/>
</div>
</template>
<script>
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalApprovalDashboard',
    data() {
        let vm = this;
        return {
            //approvals_url: api_endpoints.approvals,
            approvals_url: api_endpoints.approvals_paginated_external,
        }
    
    },
    watch: {},
    components: {
        ApprovalDashTable,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
