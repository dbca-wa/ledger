<template lang="html">
    <div id="application-assessment-select">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Select the group for assessment" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="assessmentForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row">
                                <label class="control-label">Please select the assessment for activity type <strong>{{licence_activity_type_name}}</strong></label>
                            </div>
                            <div class="row">
                                <div class="col-sm-9">
                                    <div v-for="(assessment,index) in assessments" class="radio">
                                        <div v-if="assessment.licence_activity_type == licence_activity_type">
                                            <label class="radio-inline control-label"><input type="radio" name="recurrenceSchedule" :value="assessment.id" v-model="selected_assessment">{{assessment.assessor_group.display_name}}</label>
                                        </div>
                                    </div>
                                    
                                </div>
                            </div>
                        
                        </div>
                    </form>
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import Vue from 'vue'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers, api_endpoints} from "@/utils/hooks.js"
export default {
    name:'assessment-select',
    components:{
        modal,
        alert
    },
    props:{
            application_id:{
                type:Number,
            }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            assessments: {},
            selected_assessment:null,
            licence_activity_type:null,
            licence_activity_type_name:null,
            reason_choices: {},
            errors: false,
            errorString: '',
            validation_form: null,
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    methods:{
        ok:function () {
            let vm =this;
            vm.$parent.selected_assessment_id=vm.selected_assessment
            vm.$parent.toggleConditions();
            vm.close();
            
        },
        cancel:function () {
            
            this.isModalOpen = false;
            this.assessments = {}           
            
        },
        close:function () {
            this.isModalOpen = false;
            this.assessments = {} 
            this.errors = false;
        },
        fetchAssessments: function(){
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,(vm.application_id+'/assessments')))
            .then((response) => {
                vm.assessments = response.body;
                console.log(vm.assessments)
                
            }, (error) => {
                
                swal(
                    'Application Error',
                    helpers.apiVueResourceError(error),
                    'error'
                )
            });
        },
        sendData:function(){
            let vm = this;
           
                
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    reason: "required"
                    
                     
                },
                messages: {              
                    reason: "field is required",
                                         
                },
                showErrors: function(errorMap, errorList) {
                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);
                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });
                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");
                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
       },
       eventListerners:function () {
            let vm = this;
            
            // Intialise select2
            // $(vm.$refs.reason).select2({
            //     "theme": "bootstrap",
            //     allowClear: true,
            //     placeholder:"Select Reason"
            // }).
            // on("select2:select",function (e) {
            //     var selected = $(e.currentTarget);
            //     vm.amendment.reason = selected.val();
            // }).
            // on("select2:unselect",function (e) {
            //     var selected = $(e.currentTarget);
            //     vm.amendment.reason = selected.val();
            // });
       }
   },
   mounted:function () {
       let vm =this;
       console.log("inside mounted")
       vm.form = document.forms.assessmentForm;
       console.log("PRINTING FORM FROM ASSESSMENT SELECT")
       console.log(document.forms.assessmentForm)
       vm.fetchAssessments();
   }
}
</script>

<style lang="css">
</style>