<template lang="html">
    <div id="internal-application-sendAssessor">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Send to Assessor" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="assessorForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">To</label>
                                        <textarea readonly class="form-control" v-model="assessment.assessor_group_name"> </textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Details</label>
                                        <textarea class="form-control" name="name" v-model="assessment.text" ></textarea>
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
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
//import api_endpoints from '../api'
import {
    api_endpoints,
    helpers
} from "@/utils/hooks.js"
export default {
    name:'Add-Organisation-Contact',
    components:{
        modal,
        alert
    },
    props:{
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            assessment: {
                assessor_group_name:null,
                assessor_group:null,
                application: this.$store.getters.application_id,
                licence_activity:null,
            },
            assessor_group:null,
            assessingApplication:false,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
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
            // if($(vm.form).valid()){
                vm.sendData();
            // }
        },
        cancel:function () {
        },
        close:function () {
            this.isModalOpen = false;
            this.contact = {};
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let assessment = JSON.parse(JSON.stringify(vm.assessment));
            vm.$http.post('/api/assessment.json',JSON.stringify(assessment),{
                        emulateJSON:true,
                    }).then((response)=>{
                        //vm.$parent.loading.splice('processing contact',1);
                        swal(
                             'Send to Assessor',
                             'This application has been sent to the selected group for assessment.',
                             'success'
                        );
                        vm.assessingApplication = true;
                        // Refresh all assessorDatatables
                        for (var i=0;i<vm.$parent.$refs.assessorDatatable.length;i++){
                            vm.$parent.$refs.assessorDatatable[i].vmDataTable.ajax.reload();
                        }
                        vm.$http.get(helpers.add_endpoint_json(api_endpoints.applications,assessment.application+'/internal_application')).then((res) => {
                            vm.$emit('refreshFromResponse',res);
                        });
                        vm.close();
                    },(error)=>{
                        console.log(error);
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                        vm.amendingProposal = true;
                        
                    });
                
        },

        addFormValidations: function() {
            let vm = this;
            $(vm.form).validate({
                rules: {
                    arrival:"required",
                    departure:"required",
                    campground:"required",
                    campsite:{
                        required: {
                            depends: function(el){
                                return vm.campsites.length > 0;
                            }
                        }
                    }
                },
                messages: {
                    arrival:"field is required",
                    departure:"field is required",
                    campground:"field is required",
                    campsite:"field is required"
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
       }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.addContactForm;
       vm.addFormValidations();
   }
}
</script>

<style lang="css">
</style>
