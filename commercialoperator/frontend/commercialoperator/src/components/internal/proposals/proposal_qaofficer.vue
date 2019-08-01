<template lang="html">
    <div id="internal-proposal-onhold">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Application With QA Officer" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="withqaForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">

                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <TextArea :proposal_id="proposal_id" :readonly="readonly" name="_comments" label="Comments" id="id_comments" />
                                        <div v-if="is_qaofficer_status">
                                            <FileField :document_url="document_url" :proposal_id="proposal_id" isRepeatable="true" name="qaofficer_file" label="Add Document" id="id_file" @refreshFromResponse="refreshFromResponse"/>
                                        </div>
                                        <div v-else>
                                            <FileField :document_url="document_url" :proposal_id="proposal_id" isRepeatable="true" name="assessor_qa_file" label="Add Document" id="id_file" @refreshFromResponse="refreshFromResponse"/>
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

import TextArea from '@/components/forms/text-area.vue'
import TextField from '@/components/forms/text.vue'
import FileField from '@/components/forms/file.vue'

import {helpers, api_endpoints} from "@/utils/hooks.js"
export default {
    //name:'referral-complete',
    name:'proposal-qaofficer',
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
            _file: '_file',
            _comments: '_comments',
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        document_url: function() {
            // location on media folder for the docs - to be passed to FileField
            return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/process_qaofficer_document/` : '';
        },
        is_qaofficer_status: function(){
            return this.processing_status == 'With QA Officer'? true: false;
        }

    },
    methods:{
        refreshFromResponse:function(document_list){
            let vm = this;
            vm.document_list = helpers.copyObject(document_list);
        },
        _refreshFromResponse:function(response){
            let vm = this;
            vm.document_list = helpers.copyObject(response.body);
            //vm.$nextTick(() => {
            //    vm.initialiseAssignedOfficerSelect(true);
            //    vm.updateAssignedOfficerSelect();
            //});
        },

        save: function(){
            let vm = this;
            var is_with_qaofficer = vm.processing_status == 'With QA Officer'? true: false;
            var form = document.forms.withqaForm;
            var data = {
                with_qaofficer: is_with_qaofficer ? 'False': 'True', // since wee need to do the reverse
                file_input_name: 'qaofficer_file',
                proposal: vm.proposal_id,
                text: form.elements['_comments'].value, // getting the value from the text-area.vue field
            }
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/with_qaofficer'),data,{
                emulateJSON: true
            }).then(res=>{
                if(!is_with_qaofficer){
                    swal(
                        'Send Application to QA Officer',
                        'Send Application to QA Officer',
                        'success'
                    );
                } else {
                    swal(
                        'Application QA Officer Assessment Completed',
                        'Application QA Officer Assessment Completed',
                        'success'
                    );
                }

                vm.proposal = res.body;
                vm.$router.push({ path: '/internal' }); //Navigate to dashboard after completing the referral

                },err=>{
                swal(
                    'Submit Error',
                    helpers.apiVueResourceError(err),
                    'error'
                )
            });
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
        addFormValidations: function() {
        },
        eventListerners:function () {
        }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.onholdForm;
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
