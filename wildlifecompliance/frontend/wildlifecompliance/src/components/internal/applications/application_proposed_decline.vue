<template lang="html">
    <div id="change-contact">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="declineForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label class="control-label" for="Name">Select licensed activities to Propose Decline</label>
                                        <div v-for="activity in visibleLicenceActivities">
                                            <div>
                                                <input type="checkbox" :value ="activity.id" :id="activity.id" v-model="propose_decline.activity">{{activity.name}}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label class="control-label" for="Name">Provide Reason for the proposed decline </label>
                                        <textarea style="width: 70%;"class="form-control" name="reason" v-model="propose_decline.reason"></textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label class="control-label" for="Name">Proposed CC email</label>
                                        <input type="text" style="width: 70%;"class="form-control" name="cc_email" v-model="propose_decline.cc_email"/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="decliningApplication" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i>Proposing Decline</button>
                <button type="button" v-else class="btn btn-danger" @click="ok">Propose Decline</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
export default {
    name:'ProposedDecline',
    components:{
        modal,
        alert
    },
    props:{
            application_id:{
                type:Number,
                required: true
            },
            processing_status:{
                type:Object,
                required: true
            },
            application_licence_type:{
                type:Object,
                required:true
            },
            application: {
                type: Object,
                required: true
            }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            propose_decline:{
                activity:[],
                cc_email:null,
                reason:null,
            },
            selected_activity:null,
            decliningApplication: false,
            errors: false,
            validation_form: null,
            errorString: '',
            successString: '',
            success:false,
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            return 'Proposed Decline';
        },
        visibleLicenceActivities: function() {
            return this.application.licence_type_data.activity.filter(
                activity => ['with_officer_conditions'].includes(activity.processing_status.id)
                    && activity.name && this.userHasRole('licensing_officer', activity.id)
            )
        },
    },
    methods:{
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }
        },
        cancel:function () {
            this.close();
        },
        close:function () {
            this.isModalOpen = false;
            this.propose_decline = {
                activity:[],
                cc_email:null,
                reason:null,
            };
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let propose_decline = JSON.parse(JSON.stringify(vm.propose_decline));
            vm.decliningApplication = true;
            if (propose_decline.activity.length > 0){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application_id+'/proposed_decline'),JSON.stringify(propose_decline),{
                        emulateJSON:true,
                    }).then((response)=>{
                        swal(
                                'Propose Decline',
                                'The selected licenced activities have been proposed for Decline.',
                                'success'
                        )
                        vm.decliningApplication = false;
                        vm.close();
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.decliningApplication = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            } else {
                vm.decliningApplication = false;
                swal(
                     'Propose Decline',
                     'Please select at least once licenced activity to Propose Decline.',
                     'error'
                )
            }
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    reason:"required",
                },
                messages: {
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
        },
        userHasRole: function(role, activity_id) {
            return this.application.user_roles.filter(
                role_record => role_record.role == role && (!activity_id || activity_id == role_record.activity_id)
            ).length;
        },
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.declineForm;
       vm.addFormValidations();
   }
}
</script>

<style lang="css">
</style>
