<template id="application_conditions">
    <div>
        
        <template v-if="isFinalised">
            <div v-for="item in application.licence_type_data">
                <ul class="nav nav-tabs" id="conditiontabs">
                    <li v-for="(item1,index) in item">
                        <a v-if="item1.processing_status.id=='accepted'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-ok"></span>
                        </a>
                        <a v-if="item1.processing_status.id=='declined'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-remove"></span>
                        </a>


                    </li>
                </ul>
    
            </div>   
            <div  class="tab-content">
                <div v-for="item in application.licence_type_data">
                    <div v-for="(item1,index) in item" v-if="item1.processing_status.id=='accepted'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licence has been issued and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} {{isFinalised}}
                        <div v-for="licence in application.licences" v-if="licence.licence_activity_id == item1.id">
                            Expiry Date: {{licence.expiry_date}}
                        </div>
                    </div>
                    <div v-for="(item1,index) in item" v-if="item1.processing_status.id=='declined'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licence has been declined and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                </div>
            </div>
        </template>
        <template v-if="isPartiallyFinalised">
            <div v-for="item in application.licence_type_data">
                <ul class="nav nav-tabs" >
                    <li v-for="(item1,index) in item">
                        <a v-if="item1.processing_status.id=='accepted'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-ok"></span>
                        </a>

                        <a v-if="item1.processing_status.id=='declined'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-remove"></span>
                        </a>
                        <a v-if="item1.processing_status.id=='with_assessor'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-remove"></span>
                        </a>
                        <a v-if="item1.processing_status.id=='with_officer_conditions'" data-toggle="tab" :href="`#${item1.id}`">{{item1.name}}
                            
                                <span class="glyphicon glyphicon-remove"></span>
                        </a>


                    </li>
                </ul>
    
            </div>   
            <div  class="tab-content">
                <div v-for="item in application.licence_type_data">
                    <div v-for="(item1,index) in item" v-if="item1.processing_status.id=='accepted'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licence has been issued and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                    <div v-for="(item1,index) in item" v-if="item1.processing_status.id=='declined'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licence has been declined and has been emailed to {{application.submitter.first_name}} {{application.submitter.last_name}} 
                    </div>
                    <div v-for="(item1,index) in item" v-if="item1.processing_status.id=='with_assessor'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licensed activity cannot be issued as this licensed activity is still with assessord for assessment. 
                    </div>
                    <div v-for="(item1,index) in item" v-if="item1.processing_status.id=='with_officer_conditions'" :id="`${item1.id}`" class="tab-pane fade active in"> 
                        The licensed activity cannot be issued as the conditions have not been finalised yet. 
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
export default {
    name: 'InternalApplicationConditions',
    props: {
        application: Object
    },
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
        isFinalised: function(){
            let vm=this;
            var flag=0;
            for(var i=0, len=vm.application.licence_type_data.activity.length; i<len; i++){
                if(vm.application.licence_type_data.activity[i].processing_status.id == 'declined' || vm.application.licence_type_data.activity[i].processing_status.id == 'accepted' ){
                    flag=flag+1;
                }

            }
            if(flag>0 && flag==len){
                return true;
            }
            else{
                return false;
            }
            
        },
        isPartiallyFinalised: function(){
            let vm=this;
            var flag=0;
            for(var i=0, len=vm.application.licence_type_data.activity.length; i<len; i++){
                if(vm.application.licence_type_data.activity[i].processing_status.id == 'declined' || vm.application.licence_type_data.activity[i].processing_status.id == 'accepted' ){
                    flag=flag+1;
                }

            }
            if(flag>0 && flag!=len){
                return true;
            }
            else{
                return false;
            }
            
        },
    },
    methods:{
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
        let vm = this;
    }
}
</script>
<style scoped>
</style>
