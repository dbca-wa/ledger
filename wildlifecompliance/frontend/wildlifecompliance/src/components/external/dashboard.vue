<template>
<div class="container" id="externalDash">
    <div class="row">
        <div class="col-sm-12">
            <div class="well well-sm">
                <p>
                    Welcome to the Wildlife Licensing online system dashboard.<br/><br/> Here you can access your existing licences, view any applications in progress, lodge new<br/> applications or submit information required to comply with conditions listed
                    on your licence
                </p>
            </div>
        </div>
    </div>
    <ApplicationDashTable level='external' :url='applications_url'/>
    <div>
        <LicenceDashTable level='external' :url='licences_url'/>
        <ReturnDashTable level='external' :url='returns_url'/>
    </div>
</div>
</template>
<script>

import datatable from '@/utils/vue/datatable.vue'
import ApplicationDashTable from '@common-components/applications_dashboard.vue'
import LicenceDashTable from '@common-components/licences_dashboard.vue'
import ReturnDashTable from '@common-components/returns_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'ExternalDashboard',
    data() {
        let vm = this;
        return {
            applications_url: helpers.add_endpoint_join(api_endpoints.applications_paginated,'external_datatable_list/?format=datatables'),
            licences_url: helpers.add_endpoint_join(api_endpoints.licences_paginated,'external_datatable_list/?format=datatables'),
            returns_url: helpers.add_endpoint_join(api_endpoints.returns_paginated,'user_datatable_list/?format=datatables'),
            empty_list: '/api/empty_list',
        }
    },
    components:{
        ApplicationDashTable,
        LicenceDashTable,
        ReturnDashTable
    },
    watch: {},
    computed: {
    },
    methods: {
    },
    mounted: function () {
    }
}
</script>
