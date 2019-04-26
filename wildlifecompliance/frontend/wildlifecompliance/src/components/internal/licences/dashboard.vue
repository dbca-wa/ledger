<template>
<div class="container" id="internalDash">
    <LicenceDashTable level="internal" :url="licences_url"/>
</div>
</template>
<script>
import LicenceDashTable from '@common-components/licences_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalLicenceDashboard',
    data() {
        let vm = this;
        return {
            licences_url: helpers.add_endpoint_join(api_endpoints.licences_paginated,'internal_datatable_list/?format=datatables'),
        }
    
    },
    watch: {},
    components: {
        LicenceDashTable,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
