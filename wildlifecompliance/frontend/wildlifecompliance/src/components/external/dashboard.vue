<template>
<div class="container" id="externalDash">
    <div class="row">
        <div class="col-sm-12">
            <div class="well well-sm">
                <p>
                    Welcome to the Wildlife Compliance online system dashboard.<br/><br/> Here you can access your existing licences, view any applications in progress, lodge new<br/> applications or submit information required to comply with conditions listed
                    on your licence
                </p>
            </div>
        </div>
    </div>
    <ApplicationDashTable level='external' :url='applications_url'/>
    <div v-if="wc_version != 1.0">
        <LicenceDashTable level='external' :url='licences_url'/>
        <ReturnDashTable level='external' :url='returns_url'/>
    </div>
</div>
</template>
<script>

import datatable from '@/utils/vue/datatable.vue'
import ApplicationDashTable from '@common-utils/applications_dashboard.vue'
import LicenceDashTable from '@common-utils/licences_dashboard.vue'
import ReturnDashTable from '@common-utils/returns_dashboard.vue'
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
            applications_url: helpers.add_endpoint_json(api_endpoints.applications,'user_list'),
            licences_url: helpers.add_endpoint_json(api_endpoints.licences,'user_list'),
            returns_url:helpers.add_endpoint_json(api_endpoints.returns,'user_list'),
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
        wc_version: function (){
            return this.$root.wc_version;
        }
    },
    methods: {
    },
    mounted: function () {
    }
}
</script>
