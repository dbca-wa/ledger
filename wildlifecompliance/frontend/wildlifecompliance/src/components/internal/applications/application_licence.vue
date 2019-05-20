<template id="application_conditions">
    <div>
        <template v-if="isFinalised || isPartiallyFinalised">
            <div class="panel panel-default" >
                <div class="panel-heading">
                    <h3 class="panel-title">Licence Details
                        <a :href="'#licence_details'" class="panelClicker" data-toggle="collapse" expanded="true" :aria-controls="'licence_details'">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="'licence_details'">
                    <ul>
                        <li v-for="(activity, index) in finalisedActivities" v-bind:key="`licence_row_${index}`" :id="`licence_${activity.id}`">
                            <div v-if="activity.processing_status.id=='accepted'">
                                <b>{{activity.name}}:</b> issued ({{format(activity.start_date)}} - {{format(activity.expiry_date)}}).
                            </div>
                            <div v-if="activity.processing_status.id=='declined'">
                                <b>{{activity.name}}:</b> declined.
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </template>
    </div>
</template>
<script>
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import { mapGetters } from 'vuex'
export default {
    name: 'InternalApplicationLicenceDetails',
    watch:{
    },
    components:{
    },
    computed:{
        ...mapGetters([
            'application',
            'isPartiallyFinalised',
            'licenceActivities',
            'isFinalised',
        ]),
        finalisedActivities: function() {
            return this.licenceActivities(['accepted', 'declined']);
        },
    },
    methods: {
        format: function(activity_date) {
            return moment(activity_date).format('DD/MM/YYYY');
        },
    },
}
</script>
<style scoped>
</style>
