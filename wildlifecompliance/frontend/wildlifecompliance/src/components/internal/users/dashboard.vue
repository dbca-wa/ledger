<template>
<div class="container" id="internalDash">
    <UserDashTable level="internal" :url="users_url"/>
</div>
</template>
<script>
import UserDashTable from '@common-utils/users_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'InternalUserDashboard',
    data() {
        let vm = this;
        return {
            users_url: api_endpoints.users,
        }
    
    },
    watch: {},
    components: {
        UserDashTable,
    },
    computed: {
    },
    methods: {},
    mounted: function () {
    }
}
</script>
