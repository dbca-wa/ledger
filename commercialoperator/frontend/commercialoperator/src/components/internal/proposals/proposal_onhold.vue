<template lang="html">
    <div id="internal-proposal-onhold">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Put Proposal On-hold" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="onholdForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">

                            <!--
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Attach Document</label>
										<div>
											<span v-if="!uploadedFile" class="btn btn-info btn-file pull-left">
											    Attach File <input type="file" ref="uploadedFile" @change="readFile()"/>
                                            </span>
                                            <span v-else class="pull-left" style="margin-left:10px;margin-top:10px;">
                                                {{uploadedFileName()}}
                                            </span>
										</div>
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="onhold_comment">Comment</label>
                                        <textarea class="form-control" name="onhold_comment" v-model="onhold_comment" required="true"></textarea>
                                    </div>
                                </div>
                            </div>
                            -->

                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <TextArea :proposal_id="proposal_id" :readonly="readonly" name="on_hold_comments" label="Comments" id="id_comments" />
                                        <FileField :proposal_id="proposal_id" isRepeatable="true" name="on_hold_file" label="Add Document" id="id_file" @refreshFromResponse="refreshFromResponse"/>
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

import TextArea from '@/components/forms/text-area.vue'
import TextField from '@/components/forms/text.vue'
import FileField from '@/components/forms/file.vue'

import {helpers, api_endpoints} from "@/utils/hooks.js"
export default {
    //name:'referral-complete',
    name:'proposal-onhold',
    components:{
        TextArea,
        TextField,
        FileField,
        modal,
        alert
    },
    props:{
            proposal_id:{
                type:Number,
            },
            processing_status:{
                type:String,
            },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            errors: false,
            errorString: '',
            validation_form: null,
            onhold_comment: null,
            on_hold_file: 'on_hold_file',
            on_hold_comments: 'on_hold_comments',
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    methods:{
        refreshFromResponse:function(response){
            let vm = this;
            vm.document_list = helpers.copyObject(response.body);
            vm.document_res = helpers.copyObject(response);
            //vm.$nextTick(() => {
            //    vm.initialiseAssignedOfficerSelect(true);
            //    vm.updateAssignedOfficerSelect();
            //});
        },

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
            var form = document.forms.onholdForm;
            var data = {
                onhold: 'True',
                file_input_name: 'on_hold_file',
                proposal_id: vm.proposal_id,
                onhold_comment: form.elements['on_hold_comments'].value, // getting the value from the text-area.vue field
                document_list: JSON.stringify(vm.document_list),
                document_list2: JSON.stringify(vm.document_res),
            }
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/on_hold'),data,{
                emulateJSON: true
            }).then(res=>{
                swal(
                    'Put Proposal On-hold',
                    'Proposal On-hold',
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

        _save: function(){
            let vm = this;
                let data = new FormData(vm.form);
                data.append('onhold', true)
                data.append('onhold_document', vm.uploadedFile)
                data.append('onhold_comment', vm.onhold_comment)
                //if (vm.proposal.approval_level_document) {
                //    data.append('referral_document_name', vm.proposal.referral_document[0])
                //}
                //vm.$http.post(helpers.add_endpoint_json(api_endpoints.referrals,vm.referral_id+'/complete'),data,{
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/on_hold'),data,{
                //vm.$http.post(api_endpoints.proposals+'/on_hold',data,{
                emulateJSON:true
            }).then(res=>{
                swal(
                    'Put Proposal On-hold',
                    'Proposal On-hold',
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
                             'An email has been sent to applicant with the request to amend this Proposal',
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
