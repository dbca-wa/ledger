<template lang="html">
    <div id="internal-proposal-amend">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Complete Referral" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="amendForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            

                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="referral_comment">Comment</label>
                                        <textarea class="form-control" name="referral_comment" v-model="referral_comment" required="true"></textarea>
                                    </div>
                                </div>
                            </div>

                        <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <!-- templated from from proposal_approval.vue -->
                                        <label class="control-label pull-left"  for="Name">Attach Document   </label>
                                        <div>
                                            <span v-if="!uploadedFile" class="btn btn-info btn-file pull-left">
                                                Attach File<input type="file" ref="uploadedFile" @change="readFile()"/>
                                            </span>
                                            <span v-else class="pull-left" style="margin-left:10px;margin-top:10px;">
                                                {{uploadedFileName()}}
                                            </span>
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
    //name:'amendment-request',
    name:'referral-complete',
    components:{
        modal,
        alert
    },
    props:{
            proposal_id:{
                type:Number,
            },
            referral_id:{
                type:Number,
            },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            amendment: {
            reason:'',
            reason_id: null,
            amendingProposal: false,
            proposal: vm.proposal_id 
            },
            reason_choices: {},
            errors: false,
            errorString: '',
            validation_form: null,
            uploadedFile: null,
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    methods:{

        readFile: function() {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.uploadedFile)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.uploadedFile = _file;
            //vm.save()
        },
        removeFile: function(){
            let vm = this;
            vm.uploadedFile = null;
            vm.save()
        },
        save: function(){
            let vm = this;
                let data = new FormData(vm.form);
                data.append('referral_document', vm.uploadedFile)
                //if (vm.proposal.approval_level_document) {
                //    data.append('referral_document_name', vm.proposal.referral_document[0])
                //}
                //vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/approval_level_document'),data,{
                //vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/referral_document'),data,{
                //vm.$http.post(helpers.add_endpoint_json(api_endpoints.referrals,vm.referral_id+'/referral_document'),data,{
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.referrals,vm.referral_id+'/complete'),data,{
                emulateJSON:true
            }).then(res=>{
                swal(
                    'Referral Complete',
                    'Referral Complete',
                    'success'
                );

                vm.proposal = res.body;
                vm.$emit('refreshFromResponse',res);
                vm.$router.push({ path: '/internal' }); //Navigate to dashboard after completing the referral

                },err=>{
                swal(
                    'Submit Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });
        },
        uploadedFileName: function() {
            return this.uploadedFile != null ? this.uploadedFile.name: '';
        },



        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                //vm.sendData();
                vm.save()
            }
        },
        cancel:function () {
            let vm = this;
            vm.close();
        },
        close:function () {
            this.isModalOpen = false;
            this.amendment = {
                reason: '',
                reason_id: null,
                proposal: this.proposal_id
            };
            this.errors = false;
            $(this.$refs.reason).val(null).trigger('change');
            $('.has-error').removeClass('has-error');
            
            this.validation_form.resetForm();
        },
        fetchAmendmentChoices: function(){
            let vm = this;
            vm.$http.get('/api/amendment_request_reason_choices.json').then((response) => {
                vm.reason_choices = response.body;
                
            },(error) => {
                console.log(error);
            } );
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let amendment = JSON.parse(JSON.stringify(vm.amendment));
            vm.$http.post('/api/amendment_request.json',JSON.stringify(amendment),{
                        emulateJSON:true,
                    }).then((response)=>{
                        //vm.$parent.loading.splice('processing contact',1);
                        swal(
                             'Sent',
                             'An email has been sent to applicant with the request to amend this Application',
                             'success'
                        );
                        vm.amendingProposal = true;
                        vm.close();
                        //vm.$emit('refreshFromResponse',response);
                        Vue.http.get(`/api/proposal/${vm.proposal_id}/internal_proposal.json`).then((response)=>
                        {
                            vm.$emit('refreshFromResponse',response);
                            
                        },(error)=>{
                            console.log(error);
                        });
                        vm.$router.push({ path: '/internal' }); //Navigate to dashboard after creating Amendment request
                     
                    },(error)=>{
                        console.log(error);
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                        vm.amendingProposal = true;
                        
                    });
                

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
            $(vm.$refs.reason).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Reason"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.amendment.reason = selected.val();
                vm.amendment.reason_id = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.amendment.reason = selected.val();
                vm.amendment.reason_id = selected.val();
            });
       }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.amendForm;
       vm.fetchAmendmentChoices();
       vm.addFormValidations();
       this.$nextTick(()=>{  
            vm.eventListerners();
        });
    //console.log(validate);
   }
}
</script>

<style lang="css">
</style>
