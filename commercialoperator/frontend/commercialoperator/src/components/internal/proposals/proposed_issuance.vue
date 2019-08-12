<template lang="html">
    <div id="proposedIssuanceApproval">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="approvalForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Start Date</label>
                                        <label v-else class="control-label pull-left"  for="Name">Proposed Start Date</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="start_date" style="width: 70%;">
                                            <input type="text" class="form-control" name="start_date" placeholder="DD/MM/YYYY" v-model="approval.start_date">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div class="row" v-show="showstartDateError">
                                    <alert  class="col-sm-12" type="danger"><strong>{{startDateErrorString}}</strong></alert>
                    
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Expiry Date</label>
                                        <label v-else class="control-label pull-left"  for="Name">Proposed Expiry Date</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="due_date" style="width: 70%;">
                                            <input type="text" class="form-control" name="due_date" placeholder="DD/MM/YYYY" ref="expiry_date" v-model="approval.expiry_date" :disabled="is_amendment">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div class="row" v-show="showtoDateError">
                                    <alert  class="col-sm-12" type="danger"><strong>{{toDateErrorString}}</strong></alert>
                    
                                </div>
                                
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">Details</label>
                                        <label v-else class="control-label pull-left"  for="Name">Proposed Details</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <textarea name="approval_details" class="form-control" style="width:70%;" v-model="approval.details"></textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label v-if="processing_status == 'With Approver'" class="control-label pull-left"  for="Name">CC email</label>
                                        <label v-else class="control-label pull-left"  for="Name">Proposed CC email</label>
                                    </div>
                                    <div class="col-sm-9">
                                            <input type="text" class="form-control" name="approval_cc" style="width:70%;" v-model="approval.cc_email">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>

            <p v-if="can_preview">Click <a href="#" @click.prevent="preview">here</a> to preview the licence document.</p>

            <div slot="footer">
                <button type="button" v-if="issuingApproval" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Processing</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Ok</button>
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
    name:'Proposed-Approval',
    components:{
        modal,
        alert
    },
    props:{
        proposal_id: {
            type: Number,
            required: true
        },
        processing_status: {
            type: String,
            required: true
        },
        proposal_type: {
            type: String,
            required: true
        }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            approval: {},
            state: 'proposed_approval',
            issuingApproval: false,
            validation_form: null,
            errors: false,
            toDateError:false,
            startDateError:false,
            errorString: '',
            toDateErrorString:'',
            startDateErrorString:'',
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
        csrf_token: function() {
          return helpers.getCookie('csrftoken')
        },
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        showtoDateError: function() {
            var vm = this;
            return vm.toDateError;
        },
        showstartDateError: function() {
            var vm = this;
            return vm.startDateError;
        },
        title: function(){
            return this.processing_status == 'With Approver' ? 'Issue Licence' : 'Propose to issue licence';
        },
        is_amendment: function(){
            return this.proposal_type == 'Amendment' ? true : false;
        },
        can_preview: function(){
            return this.processing_status == 'With Approver' ? true : false;
        },
        preview_licence_url: function() {
          return (this.proposal_id) ? `/preview/licence-pdf/${this.proposal_id}` : '';
        },
        

    },
    methods:{
        preview:function () {
            let vm =this;

            let formData = new FormData(vm.form)

            // convert formData to json
            let jsonObject = {};
            for (const [key, value] of formData.entries()) {
                jsonObject[key] = value;
            }

            vm.post_and_redirect(vm.preview_licence_url, {'csrfmiddlewaretoken' : vm.csrf_token, 'formData': JSON.stringify(jsonObject)});
        },

        post_and_redirect: function(url, postData) {
            /* http.post and ajax do not allow redirect from Django View (post method),
               this function allows redirect by mimicking a form submit.

               usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
            */
            var postFormStr = "<form method='POST' target='_blank' name='Preview Licence' action='" + url + "'>";

            for (var key in postData) {
                if (postData.hasOwnProperty(key)) {
                    postFormStr += "<input type='hidden' name='" + key + "' value='" + postData[key] + "'>";
                }
            }
            postFormStr += "</form>";
            var formElement = $(postFormStr);
            $('body').append(formElement);
            $(formElement).submit();
        },

        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
                //vm.$router.push({ path: '/internal' });
            }
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            this.approval = {};
            this.errors = false;
            this.toDateError = false;
            this.startDateError = false;
            $('.has-error').removeClass('has-error');
            $(this.$refs.due_date).data('DateTimePicker').clear();
            $(this.$refs.start_date).data('DateTimePicker').clear();
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
            let approval = JSON.parse(JSON.stringify(vm.approval));
            vm.issuingApproval = true;
            if (vm.state == 'proposed_approval'){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/proposed_approval'),JSON.stringify(approval),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingApproval = false;
                        vm.close();
                        vm.$emit('refreshFromResponse',response);
                        vm.$router.push({ path: '/internal' }); //Navigate to dashboard page after Propose issue.

                    },(error)=>{
                        vm.errors = true;
                        vm.issuingApproval = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            }
            else if (vm.state == 'final_approval'){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/final_approval'),JSON.stringify(approval),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingApproval = false;
                        vm.close();
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.issuingApproval = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            }
            
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    start_date:"required",
                    due_date:"required",
                    approval_details:"required",
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
                    if ($(vm.$refs.due_date).data('DateTimePicker').date() < $(vm.$refs.start_date).data('DateTimePicker').date()){
                        vm.toDateError = true;
                        vm.toDateErrorString = 'Please select Expiry date that is after Start date';
                        vm.approval.expiry_date = ""
                    }
                    else{
                        vm.toDateError = false;
                        vm.toDateErrorString = '';
                        vm.approval.expiry_date =  e.date.format('DD/MM/YYYY');
                    }
                    //vm.approval.expiry_date =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.due_date).data('date') === "") {
                    vm.approval.expiry_date = "";
                }
             });
            $(vm.$refs.start_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.start_date).on('dp.change', function(e){
                if ($(vm.$refs.start_date).data('DateTimePicker').date()) {

                    if (($(vm.$refs.due_date).data('DateTimePicker').date()!= null)&& ($(vm.$refs.due_date).data('DateTimePicker').date() < $(vm.$refs.start_date).data('DateTimePicker').date())){
                        vm.startDateError = true;
                        vm.startDateErrorString = 'Please select Start date that is before Expiry date';
                        vm.approval.start_date = ""
                    }
                    else{
                        vm.startDateError = false;
                        vm.startDateErrorString = '';
                        vm.approval.start_date =  e.date.format('DD/MM/YYYY');
                    }

                    //vm.approval.start_date =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.start_date).data('date') === "") {
                    vm.approval.start_date = "";
                }
             });
       }
   },
   mounted:function () {
        let vm =this;
        vm.form = document.forms.approvalForm;
        vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   }
}
</script>

<style lang="css">
</style>
