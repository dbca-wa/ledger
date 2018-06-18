<template>
<div class="container" id="internalDash">
    <ReturnDashTable level="internal" :url="returns_url"/>
</div>
</template>
<script>
import ReturnDashTable from '@common-utils/returns_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalReturnsDashboard',
    data() {
        let vm = this;
        return {
            returns_url: api_endpoints.returns,
        }
    
    },
    watch: {},
    components: {
        ReturnDashTable,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
