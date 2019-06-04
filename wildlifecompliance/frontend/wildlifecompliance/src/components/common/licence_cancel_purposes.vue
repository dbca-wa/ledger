<template lang="html">
    <div id="cancelLicencePurpose">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="cancelPurposeForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <label class="control-label" for="Name">Select licensed purposes to Cancel</label>
                                        <div v-for="purpose in cancellableLicencePurposes">
                                            <div>
                                                <input type="checkbox" :value ="purpose.id" :id="purpose.id" v-model="cancel_licence.purpose">{{purpose.name}}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="cancellingPurposes" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i>Cancelling Purpose(s)</button>
                <button type="button" v-else class="btn btn-success" @click="ok">Cancel Purpose(s)</button>
                <button type="button" class="btn btn-default" @click="cancel">Close</button>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
import { mapGetters } from 'vuex'
export default {
    name:'CancelLicencePurposes',
    components:{
        modal,
        alert
    },
    props:{
        activity_purpose_ids: Array
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            cancel_licence:{
                purpose:[],
            },
            cancellingPurposes: false,
            validation_form: null,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
        }
    },
    computed: {
        ...mapGetters([
            'application_id',
        ]),
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            return 'Select purpose(s) to cancel';
        },
        cancellableLicencePurposes: function() {
            return this.activity_purpose_ids;
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
            this.cancel_licence = {
                purpose:[]
            };
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let cancel_licence = JSON.parse(JSON.stringify(vm.cancel_licence));
            vm.cancellingPurposes = true;
            if (cancel_licence.purpose.length > 0){
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.applications,vm.application_id+'/cancel_purposes'),JSON.stringify(vm.cancel_licence),{
                        emulateJSON:true,
                    }).then((response)=>{
                        swal(
                                'Propose Issue',
                                'The selected licenced purposes have been Cancelled.',
                                'success'
                        )
                        vm.cancellingPurposes = false;
                        vm.close();
                        vm.$emit('refreshFromResponse',response);
                    },(error)=>{
                        vm.errors = true;
                        vm.cancellingPurposes = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
            } else {
                vm.cancellingPurposes = false;
                swal(
                     'Cancel Purpose',
                     'Please select at least once licenced purpose to Cancel.',
                     'error'
                )
            }

        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules:  {
                    licence_details: "required",
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
   },
   mounted:function () {
        this.form = document.forms.cancelPurposeForm;
        this.addFormValidations();
   }
}
</script>
<style lang="css">
</style>
