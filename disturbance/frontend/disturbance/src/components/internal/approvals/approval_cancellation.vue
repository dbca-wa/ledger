<template lang="html">
    <div id="approvalCancellation">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="approvalForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        
                                        <label class="control-label pull-left"  for="Name">Cancellation Date</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="cancellation_date" style="width: 70%;">
                                            <input type="text" class="form-control" name="cancellation_date" placeholder="DD/MM/YYYY" v-model="approval.cancellation_date">
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
                                        
                                        <label class="control-label pull-left"  for="Name">Cancellation Details</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <textarea name="cancellation_details" class="form-control" style="width:70%;" v-model="approval.cancellation_details"></textarea>
                                    </div>
                                </div>
                            </div>
                           
                        </div>
                    </form>
                </div>
            </div>
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
    name:'Cancel-Approval',
    components:{
        modal,
        alert
    },
    props:{
        approval_id: {
            type: Number,
            required: true
        },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            approval: {},
            approval_id: Number,
            state: 'proposed_approval',
            issuingApproval: false,
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
            return 'Cancel Approval';
        }
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
            this.approval = {};
            this.errors = false;
            $('.has-error').removeClass('has-error');
            $(this.$refs.cancellation_date).data('DateTimePicker').clear();
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
            
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.approvals,vm.approval_id+'/approval_cancellation'),JSON.stringify(approval),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.issuingApproval = false;
                        vm.close();
                        swal(
                             'Cancelled',
                             'An email has been sent to proponent about cancellation of this approval',
                             'success'
                        );
                        vm.$emit('refreshFromResponse',response);
                       

                    },(error)=>{
                        vm.errors = true;
                        vm.issuingApproval = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
                        
            
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    cancellation_date:"required",                    
                    cancellation_details:"required",
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
            
            $(vm.$refs.cancellation_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.cancellation_date).on('dp.change', function(e){
                if ($(vm.$refs.cancellation_date).data('DateTimePicker').date()) {
                    vm.approval.cancellation_date =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.cancellation_date).data('date') === "") {
                    vm.approval.cancellation_date = "";
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
