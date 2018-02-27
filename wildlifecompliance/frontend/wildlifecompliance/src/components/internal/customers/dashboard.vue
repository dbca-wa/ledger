<template>
<div class="container" id="internalDash">
    <CustomerDashTable level="internal" :url="customers_url"/>
</div>
</template>
<script>
import CustomerDashTable from '@common-utils/customers_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalCustomerDashboard',
    data() {
        let vm = this;
        return {
            customers_url: api_endpoints.customers,
        }
    
    },
    watch: {},
    components: {
        CustomerDashTable,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
