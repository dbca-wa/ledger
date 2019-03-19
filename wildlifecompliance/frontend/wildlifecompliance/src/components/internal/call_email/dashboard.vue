<template>
<div class="container" id="internalCallEmailDash">
    <CallEmailTableDash level="internal" :url="call_email_url"/>
</div>
</template>
<script>
import CallEmailTableDash from '@common-utils/call_email_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalCallEmailDashboard',
    data() {
        let vm = this;
        return {
            call_email_url: api_endpoints.call_email,
        }
    
    },
    watch: {},
    components: {
        CallEmailTableDash,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
