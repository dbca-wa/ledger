<template lang="html">
    <div class="row">
        <div class="">
            <div class="col-md-12">
                <div class="">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Workflow - Checklist <small v-if="assessment.referral_group">   Referral Group: {{assessment.referral_group_name}}</small>
                                <a class="panelClicker" :href="'#'+detailsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="detailsBody">
                                    <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                </a>
                            </h3> 
                        </div>
                        <div class="panel-body panel-collapse collapse in" :id="detailsBody">
                            <form class="form-horizontal">
                                <ul class="list-unstyled col-sm-12" v-for="q in assessment.checklist">
                                    <div class="row">
                                        <div class="col-sm-12">
                                        <li  class="col-sm-6" >
                                        <label class="control-label">{{q.question.text}}</label></li>
                                        <ul v-if="q.question.answer_type=='yes_no'" class="list-inline col-sm-6">
                                            <li class="list-inline-item">
                                                <input  class="form-check-input" v-model="q.answer" ref="Checkbox" type="radio" :name="'option'+q.id" :id="'answer_one'+q.id":value="true" data-parsley-required :disabled="readonly"/> Yes 
                                            </li>
                                            <li class="list-inline-item">
                                                <input  class="form-check-input" v-model="q.answer" ref="Checkbox" type="radio" :name="'option'+q.id" :id="'answer_two'+q.id" :value="false" data-parsley-required :disabled="readonly"/> No </li>
                                        </ul>
                                        <ul v-else class="list-inline col-sm-6">
                                            <li class="list-inline-item">
                                                <textarea :disabled="readonly" class="form-control" name="text_answer" placeholder="" v-model="q.text_answer"></textarea>                                                
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                                </ul>
                                <div v-if="hasAssessorMode || hasReferralMode" class="form-group col-sm-12">             
                                        <button class="btn btn-primary pull-right" style="margin-top:5px;" @click.prevent="update()">Update</button>                     
                                </div> 
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
    export default {
        //props:["type","name","id", "comment_value","value","isRequired","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly", "help_text_url", "help_text_assessor_url"],
        props:{
            proposal:{
                type: Object,
                required:true
            },
            assessment:{
                type: Object,
                required:true
            },
            hasAssessorMode:{
                type:Boolean,
                default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            is_referral:{
              type: Boolean,
              default: false
            },
            hasReferralMode:{
                type:Boolean,
                default: false
            },
        },
        data:function () {
            let vm=this;
            return{
                values:null,
                detailsBody: 'detailsBody'+vm._uid,
                addressBody: 'addressBody'+vm._uid,
                contactsBody: 'contactsBody'+vm._uid,
                panelClickersInitialised: false,
            }
        },
        computed:{
            readonly: function(){
                return !this.hasReferralMode && !this.hasAssessorMode ? true : false;
            }
        },
        methods:{
            update: function(){
                let vm=this;
                let assessment = JSON.parse(JSON.stringify(vm.assessment));
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.assessments,vm.assessment.id+'/update_assessment'),JSON.stringify(assessment),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.assessment=helpers.copyObject(response.body)
                        swal(
                        'Checklist update',
                        'Checklist has been updated',
                        'success'
                        )

                    },(error)=>{
                        
                        vm.errorString = helpers.apiVueResourceError(error);
                        swal(
                        'Checklist Error',
                        helpers.apiVueResourceError(error),
                        'error'
                        )
                    });
            },
        },
        mounted: function(){
            let vm=this;
            if (!vm.panelClickersInitialised){
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                },100);
            }); 
            vm.panelClickersInitialised = true;
            }
            this.$nextTick(() => {
                //vm.initialiseOrgContactTable();
                
            });
        }
    }
</script>

<style lang="css" scoped>
</style>

