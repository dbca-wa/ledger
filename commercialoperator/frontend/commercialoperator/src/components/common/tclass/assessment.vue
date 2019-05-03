<template lang="html">
    <div class="row">
        <div class="col-sm-12">
            <div class="col-md-12">
                <div class="">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Workflow - Checklist
                                <a class="panelClicker" :href="'#'+detailsBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="detailsBody">
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
                                        <ul class="list-inline col-sm-6">
                                            <li class="list-inline-item">
                                                <input  class="form-check-input" v-model="q.answer" ref="Checkbox" type="radio" :name="'option'+q.id" :id="'answer_one'+q.id":value="true" data-parsley-required /> Yes 
                                            </li>
                                            <li class="list-inline-item">
                                                <input  class="form-check-input" v-model="q.answer" ref="Checkbox" type="radio" :name="'option'+q.id" :id="'answer_two'+q.id" :value="false" data-parsley-required/> No </li>
                                        </ul>
                                    </div>
                                </div>
                                </ul>
                                <div v-if="hasAssessorMode" class="form-group col-sm-12">             
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
            }
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
        
        },
        methods:{
            update: function(){
                let vm=this;
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

