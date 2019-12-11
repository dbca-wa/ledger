<template lang="html">
    <div id="internal-proposal-eclass">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Add new Commercial Operator E Class licence" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="eclassForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">

                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">

                                        <div class="radio">
                                            <input type="radio" value="user" name="applicant_type" v-model="applicant_type" @change="set_url"/> Individual <br>
                                            <input type="radio" value="org" name="applicant_type" v-model="applicant_type" @change="set_url"/> Organisation <br>
                                        </div>

                                        <TextFilteredField :url="filtered_url" :readonly="readonly" name="holder" label="Holder" id="id_holder" :isRequired="isRequired"/>
                                        <DateField :proposal_id="proposal_id" :readonly="readonly" name="issue_date" label="Issue Date" id="id_issue_date" :isRequired="isRequired"/>
                                        <DateField :proposal_id="proposal_id" :readonly="readonly" name="start_date" label="Start Date" id="id_start_date" :isRequired="isRequired"/>
                                        <DateField :proposal_id="proposal_id" :readonly="readonly" name="expiry_date" label="Expiry Date" id="id_expiry_date" :isRequired="isRequired"/>
                                        <!-- <FileField :document_url="document_url" :proposal_id="proposal_id" isRepeatable="true" name="eclass_file" label="Licence" id="id_file" @refreshFromResponse="refreshFromResponse"/> -->
                                        <!-- <RadioField :proposal_id="proposal_id" :readonly="readonly" name="applicant_type2" label="Applicant Type" id="id_applicant_type2" :options="radio_options" :conditions="radio_conditions"/> -->

                                        <div class="form-group">
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left"  for="Name">Attachments</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <template v-for="(f,i) in files">
                                                        <div :class="'row top-buffer file-row-'+i">
                                                            <div class="col-sm-4">
                                                                <span v-if="f.file == null" class="btn btn-info btn-file pull-left">
                                                                    Attach File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)" :required="isRequired"/>
                                                                </span>
                                                                <span v-else class="btn btn-info btn-file pull-left">
                                                                    Update File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)"/>
                                                                </span>
                                                            </div>
                                                            <div class="col-sm-4">
                                                                <span>{{f.name}}</span>
                                                            </div>
                                                            <div class="col-sm-4">
                                                                <button @click="removeFile(i)" class="btn btn-danger">Remove</button>
                                                            </div>
                                                        </div>
                                                    </template>
                                                    <!--
                                                    <a href="" @click.prevent="attachAnother"><i class="fa fa-lg fa-plus top-buffer-2x"></i></a>
                                                    -->
                                                </div>
                                            </div>
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
import Vue from 'vue'
//import vSelect from "vue-select"
//Vue.component('v-select', vSelect)

import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'

import TextArea from '@/components/forms/text-area.vue'
import TextField from '@/components/forms/text.vue'
import FileField from '@/components/forms/file.vue'
import DateField from '@/components/forms/date-field.vue'
import TextFilteredField from '@/components/forms/text-filtered.vue'
import RadioField from '@/components/forms/radio.vue'

import {helpers, api_endpoints} from "@/utils/hooks.js"
export default {
    //name:'referral-complete',
    name:'proposal-onhold',
    components:{
        TextArea,
        TextField,
        FileField,
        DateField,
        TextFilteredField,
        RadioField,
        modal,
        alert,
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
            _comments: '_comments',
            isRequired: true,
            files: [
                {
                    'file': null,
                    'name': ''
                }
            ],
            applicant_type: 'user',
            filtered_url: api_endpoints.filtered_users + '?search=',
            //radio_conditions: {},
            //radio_options: [
            //    {
            //      "value": "yes",
            //      "label": "Yes"
            //    },
            //    {
            //      "value": "no",
            //      "label": "No"
            //    }
            //],
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        document_url: function() {
            // location on media folder for the docs - to be passed to FileField
            //return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/process_qaofficer_document/` : '';
            return `/api/approvals/0/add_eclass_licence/`;
        },
        filtered_users_url: function() {
            return api_endpoints.filtered_users + '?search=';
        },
        filtered_organisations_url: function() {
            return api_endpoints.filtered_organisations + '?search=';
        },

    },
    methods:{

        set_url: function() {
            let vm = this;
            if (this.applicant_type == 'user') {
                vm.filtered_url = this.filtered_users_url;
            } else {
                vm.filtered_url = this.filtered_organisations_url;
            }
        },

        uploadFile(target,file_obj){
            let vm = this;
            let _file = null;
            var input = $('.'+target)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            file_obj.file = _file;
            file_obj.name = _file.name;
        },
        removeFile(index){
            let length = this.files.length;
            $('.file-row-'+index).remove();
            this.files.splice(index,1);
            this.$nextTick(() => {
                length == 1 ? this.attachAnother() : '';
            });
        },
        attachAnother(){
            this.files.push({
                'file': null,
                'name': ''
            })
        },

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

//        _onSearch(search, loading) {
//            loading(true);
//            this.search(loading, search, this);
//        },
//        _search: _.debounce((loading, search, vm) => {
//
//            vm.$http.get(vm.filtered_users_url+escape(search),{
//                emulateJSON: true
//            }).then(res=>{
//                //vm.options = JSON.parse(res.body);
//                vm.options = res.body;
//                console.log(vm.options);
//                loading(false);
//            });
//        }, 350),

        save: function(){
            let vm = this;
            let form = new FormData(vm.form); 
            vm.$http.post('/api/approvals/0/add_eclass_licence/',form,{
                emulateJSON: true
            }).then(res=>{
                vm.proposal = res.body;
                swal(
                    'New E Class Licence Created',
                    'New E Class Licence Created: ' + res.body['approval'],
                    'success'
                );
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
        }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.eclassForm;
       //vm.addFormValidations();
       this.$nextTick(()=>{
            vm.eventListerners();
        });
    //console.log(validate);
   }
}
</script>

<style lang="css">
</style>
