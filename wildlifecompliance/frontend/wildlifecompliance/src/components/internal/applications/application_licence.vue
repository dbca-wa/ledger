<template id="application_conditions">
    <div>
        <template v-if="isFinalised">
            <div>
                <ul class="nav nav-tabs" id="conditiontabs">
                    <li v-for="(activity, index) in application.licence_type_data.activity" v-bind:key="`licence_finalised_tabs_${index}`">
                        <a v-if="activity.processing_status.id=='accepted'" data-toggle="tab" :href="`#finalised_licence_${activity.id}`">{{activity.name}}
                            <span class="glyphicon glyphicon-ok"></span>
                        </a>
                        <a v-if="activity.processing_status.id=='declined'" data-toggle="tab" :href="`#finalised_licence_${activity.id}`">{{activity.name}}
                            <span class="glyphicon glyphicon-remove"></span>
                        </a>
                    </li>
                </ul>
            </div>
            <div class="tab-content">
                <div v-for="(activity, index) in application.licence_type_data.activity" v-bind:key="`licence_finalised_row_${index}`" :id="`finalised_licence_${activity.id}`" class="tab-pane fade">
                    <div v-if="activity.processing_status.id=='accepted'"> 
                        {{activity.name}} licence has been issued and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}}
                        <div v-for="(licence, licence_idx) in getLicencesForActivity(activity.id)"  v-bind:key="`licence_object_${licence_idx}`">
                            Expiry Date: {{licence.expiry_date}}
                        </div>
                    </div>
                    <div v-if="activity.processing_status.id=='declined'"> 
                        {{activity.name}} licence has been declined and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                </div>
            </div>
        </template>
       <template v-if="isPartiallyFinalised">
            <div>
                <ul class="nav nav-tabs" >
                    <li v-for="(activity, index) in application.licence_type_data.activity" v-bind:key="`licence_partially_finalised_tabs_${index}`">
                       <a v-if="activity.processing_status.id=='accepted'" data-toggle="tab" :href="`#partially_finalised_licence_${activity.id}`">{{activity.name}}
                            <span class="glyphicon glyphicon-ok"></span>
                        </a>
                        <a v-if="activity.processing_status.id=='declined'" data-toggle="tab" :href="`#partially_finalised_licence_${activity.id}`">{{activity.name}}
                            <span class="glyphicon glyphicon-remove"></span>
                        </a>
                        <a v-if="activity.processing_status.id=='with_assessor'" data-toggle="tab" :href="`#partially_finalised_licence_${activity.id}`">{{activity.name}}
                            <span class="glyphicon glyphicon-remove"></span>
                        </a>
                        <a v-if="activity.processing_status.id=='with_officer_conditions'" data-toggle="tab" :href="`#partially_finalised_licence_${activity.id}`">{{activity.name}}
                            <span class="glyphicon glyphicon-remove"></span>
                        </a>
                    </li>
                </ul>
            </div>
            <div class="tab-content">
                <div v-for="(activity, index) in application.licence_type_data.activity" v-bind:key="`licence_partially_finalised_row_${index}`" :id="`partially_finalised_licence_${activity.id}`" class="tab-pane fade">
                    <div v-if="activity.processing_status.id=='accepted'"> 
                        {{activity.name}} licence has been issued and emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                    <div v-if="activity.processing_status.id=='declined'"> 
                        {{activity.name}} licence has been declined and emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                    <div v-if="activity.processing_status.id=='with_assessor'"> 
                        {{activity.name}} licensed activity cannot be issued as this licensed activity is still with assessors for assessment.
                    </div>
                    <div v-if="activity.processing_status.id=='with_officer_conditions'"> 
                        {{activity.name}} licensed activity cannot be issued as the conditions have not been finalised yet. 
                    </div>
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
    name: 'InternalApplicationConditions',
    data: function() {
        let vm = this;
        return {
            proposedDecision: "application-decision-"+vm._uid,
            proposedLevel: "application-level-"+vm._uid,
        }
    },
    watch:{
    },
    components:{
    },
    computed:{
        ...mapGetters([
            'application',
            'checkActivityStatus',
            'isPartiallyFinalised',
            'isFinalised',
        ]),
    },
    methods: {
        hasActivityStatus: function(status_list, status_count=1, required_role=null) {
            return this.checkActivityStatus(status_list, status_count, required_role);
        },
        getLicencesForActivity: function(activity_id) {
            return this.application.licences.filter(licence => 
                licence.licence_activity_id == activity_id
            );
        },
        addCondition(){
            this.$refs.condition_detail.isModalOpen = true;
        },
        removeCondition(_id){
            let vm = this;
            swal({
                title: "Remove Condition",
                text: "Are you sure you want to remove this condition?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Remove Condition',
                confirmButtonColor:'#d9534f'
            }).then((result) => {
                if (result.value) {
                    vm.$http.delete(helpers.add_endpoint_json(api_endpoints.application_conditions,_id))
                    .then((response) => {
                        vm.$refs.conditions_datatable.vmDataTable.ajax.reload();
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
    },
    mounted: function(){
    }
}
</script>
<style scoped>
</style>
