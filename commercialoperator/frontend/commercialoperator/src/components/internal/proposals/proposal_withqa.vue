<template lang="html">
    <div id="internal-proposal-onhold">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Proposal With QA Officer" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="withqaForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">

                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <TextArea :proposal_id="proposal_id" :readonly="readonly" name="_comments" label="Comments" id="id_comments" />
                                        <FileField :document_url="document_url" :proposal_id="proposal_id" isRepeatable="true" name="_file" label="Add Document" id="id_file" @refreshFromResponse="refreshFromResponse"/>
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
            //var is_onhold = vm.processing_status == 'On Hold'? true: false;
            var is_with_qaofficer = vm.processing_status == 'With QA Officer'? true: false;
            var form = document.forms.onholdForm;
            var data = {
                //onhold: is_onhold ? 'False': 'True', // since wee need to do the reverse
                with_qaofficer: is_with_qaofficer ? 'False': 'True', // since wee need to do the reverse
                file_input_name: '_file',
                proposal: vm.proposal_id,
                text: form.elements['_comments'].value, // getting the value from the text-area.vue field
                //document_list: JSON.stringify(vm.document_list),
            }
            //vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/on_hold'),data,{
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal_id+'/with_qaofficer'),data,{
                emulateJSON: true
            }).then(res=>{
                if(!is_onhold){
                    swal(
                        'Send Proposal to QA Officer',
                        'Proposal to QA Officer',
                        'success'
                    );
                } else {
                    swal(
                        'Proposal QA Officer Assessment',
                        'Proposal QA Officer Assessment',
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
