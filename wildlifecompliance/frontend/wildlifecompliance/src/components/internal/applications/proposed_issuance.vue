<template lang="html">
    <div id="proposedIssuanceLicence">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="licenceForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label class="control-label" for="Name">Select licensed activities to Propose Issue</label>
                                        <div v-for="activity in visibleLicenceActivities">
                                            <div>
                                                <input type="checkbox" :value ="activity.id" :id="activity.id" v-model="propose_issue.activity">{{activity.name}}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left" for="Name">Proposed Start Date</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="start_date" style="width: 70%;">
                                            <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY" v-model="propose_issue.start_date">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left" for="Name">Proposed Expiry Date</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="due_date" style="width: 70%;">
                                            <input type="text" class="form-control" name="due_date" placeholder="DD/MM/YYYY" v-model="propose_issue.expiry_date">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left" for="Name">Proposed Details</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <textarea name="licence_details" class="form-control" style="width:70%;" v-model="propose_issue.reason"></textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left" for="Name">Proposed CC email</label>
                                    </div>
                                    <div class="col-sm-9">
                                            <input type="text" class="form-control" name="licence_cc" style="width:70%;" v-model="propose_issue.cc_email">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="issuingLicence" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i>Proposing Issue</button>
                <button type="button" v-else class="btn btn-success" @click="ok">Propose Issue</button>
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
    name:'Proposed-Licence',
    components:{
        modal,
        alert
    },
    props:{
        application_id: {
            type: Number,
            required: true
        },
        processing_status: {
            type: Object,
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
            propose_issue:{
                activity:[],
                cc_email:null,
                reason:null,
                expiry_date:null,
                start_date:null
            },
            issuingLicence: false,
            validation_form: null,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
        // TODO: check what this is doing and what this.processing_status is referring to
            return this.processing_status.id == 'with_approver' ? 'Issue Licence' : 'Propose to issue licence';
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
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.propose_issue = {
                activity:[],
                cc_email:null,
                reason:null,
                expiry_date:null,
                start_date:null
            };
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
        },
        fetchContact: function(id){
            let vm = this;
            vm.$http.get(api_endpoints.contact(id)).then((response) => {
                vm.contact = response.body; vm.isModalOpen = true;
            },(error) => {
                console.log(error);
            } );
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let propose_issue = JSON.parse(JSON.stringify(vm.propose_issue));
            vm.issuingLicence = true;
            if (propose_issue.activity.length > 0){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application_id+'/proposed_licence'),JSON.stringify(vm.propose_issue),{
                        emulateJSON:true,
                    }).then((response)=>{
                        swal(
                                'Propose Issue',
                                'The selected licenced activities have been proposed for Issue.',
                                'success'
                        )
                        vm.issuingLicence = false;
                        vm.close();
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.issuingLicence = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            } else {
                vm.issuingLicence = false;
                swal(
                     'Propose Issue',
                     'Please select at least once licenced activity to Propose Issue.',
                     'error'
                )
            }
            
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    start_date:"required",
                    due_date:"required",
                    licence_details:"required",
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
       eventListeners:function () {
            let vm = this;
            // Initialise Date Picker
            $(vm.$refs.due_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.due_date).on('dp.change', function(e){
                if ($(vm.$refs.due_date).data('DateTimePicker').date()) {
                    vm.propose_issue.expiry_date =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.due_date).data('date') === "") {
                    vm.propose_issue.expiry_date = "";
                }
             });
            $(vm.$refs.start_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.start_date).on('dp.change', function(e){
                if ($(vm.$refs.start_date).data('DateTimePicker').date()) {
                    vm.propose_issue.start_date =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.start_date).data('date') === "") {
                    vm.propose_issue.start_date = "";
                }
             });
        },
        userHasRole: function(role, activity_id) {
            return this.application.user_roles.filter(
                role_record => role_record.role == role && (!activity_id || activity_id == role_record.activity_id)
            ).length;
        },
   },
   mounted:function () {
        let vm =this;
        vm.form = document.forms.licenceForm;
        vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   }
}
</script>

<style lang="css">
</style>
