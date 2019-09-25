<template lang="html">
    <div>
        <div class="form-group">

            <!-- using num_files to determine if files have been uploaded for this question/label (used in disturbance/frontend/disturbance/src/components/external/proposal.vue) -->
            <label :id="id" :num_files="num_documents()">{{label}}</label>
            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>
            <template v-if="help_text_assessor && assessorMode">
                <HelpText :help_text="help_text_assessor" assessorMode={assessorMode} isForAssessor={true} />
            </template> 

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>
            <template v-if="help_text_assessor_url && assessorMode">
                <HelpTextUrl :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
            </template> 


            <template v-if="assessorMode && !assessor_readonly">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>
            <span v-if="show_spinner"><i class='fa fa-2x fa-spinner fa-spin'></i></span>
            <!-- <i id="file-spinner" class=""></i> -->
            <div v-if="files">
                <div v-for="v in documents">
                    <p>
                        File: <a :href="v.file" target="_blank">{{v.name}}</a> &nbsp;
                        <span v-if="!readonly && v.can_delete">
                            <a @click="delete_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                        </span>
                        <span v-else-if="!readonly && !v.can_delete && v.can_hide">
                            <a @click="hide_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                        </span>
                        <span v-else>
                            <span v-if="!assessorMode">
                                <i class="fa fa-info-circle" aria-hidden="true" title="Previously submitted documents cannot be deleted" style="cursor: pointer;"></i>
                            </span>
                        </span>
                    </p>
                </div>
            </div>
            <div v-if="!readonly" v-for="n in repeat">
                <div v-if="isRepeatable || (!isRepeatable && num_documents()==0)">
                    <input :name="name" type="file" class="form-control" :data-que="n" :accept="fileTypes" @change="handleChange" :required="isRequired"/>
                    <alert :show.sync="showError" type="danger" style="color: red"><strong>{{errorString}}</strong></alert>
                </div>
            </div>

        </div>
        <Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value" :required="isRequired"/> 
    </div>
</template>

<script>
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
import Comment from './comment.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'
export default {
    props:{
        proposal_id: null,
        name:String,
        label:String,
        id:String,
        isRequired:String,
        comment_value: String,
        assessor_readonly: Boolean,
        help_text:String,
        help_text_assessor:String,
        help_text_url:String,
        help_text_assessor_url:String,
        assessorMode:{
            default:function(){
                return false;
            }
        },
        value:{
            default:function () {
                return null;
            }
        },
        fileTypes:{
            default:function () {
                var file_types = 
                    "image/*," + 
                    "video/*," +
                    "audio/*," +
                    "application/pdf,text/csv,application/msword,application/vnd.ms-excel,application/x-msaccess," +
                    "application/x-7z-compressed,application/x-bzip,application/x-bzip2,application/zip," + 
                    ".dbf,.gdb,.gpx,.prj,.shp,.shx," + 
                    ".json,.kml,.gpx";
                return file_types;
            }
        },
        isRepeatable:Boolean,
        readonly:Boolean,
        docsUrl: String,
    },
    components: {Comment, HelpText, HelpTextUrl},
    data:function(){
        return {
            repeat:1,
            files:[],
            showingComment: false,
            show_spinner: false,
            documents:[],
            filename:null,
            showError:false,
            errorString:'',
        }
    },

    //computed: {
    //    csrf_token: function() {
    //        return helpers.getCookie('csrftoken')
    //    }
    //},

    computed: {
        csrf_token: function() {
            return helpers.getCookie('csrftoken')
        },
        proposal_document_action: function() {
          return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/process_document/` : '';
        }
    },

    methods:{

        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
        handleChange:function (e) {
            let vm = this;
            vm.showError=false;
            vm.errorString='';
            //vm.show_spinner = true;
            if (vm.isRepeatable) {
                let  el = $(e.target).attr('data-que');
                let avail = $('input[name='+e.target.name+']');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                avail.pop();
                if (vm.repeat == 1) {
                    vm.repeat+=1;
                }else {
                    if (avail.indexOf(el) < 0 ){
                        vm.repeat+=1;
                    }
                }
                $(e.target).css({ 'display': 'none'});

            } else {
                vm.files = [];
            }
            vm.files.push(e.target.files[0]);

            if (e.target.files.length > 0) {
                //vm.upload_file(e)
                vm.save_document(e);
            }

            //vm.show_spinner = false;
        },

        /*
        upload_file: function(e) {
            let vm = this;
            $("[id=save_and_continue_btn][value='Save Without Confirmation']").trigger( "click" );
        },
		*/

        get_documents: function() {
            let vm = this;

            var formData = new FormData();
            formData.append('action', 'list');
            formData.append('input_name', vm.name);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);
            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = res.body;
                    //console.log(vm.documents);
                });

        },

        delete_document: function(file) {
            let vm = this;

            vm.show_spinner = true;
            var formData = new FormData();
            formData.append('action', 'delete');
            formData.append('document_id', file.id);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);

            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = vm.get_documents()
                    //vm.documents = res.body;
                    vm.show_spinner = false;
                });

        },

        hide_document: function(file) {
            let vm = this;

            vm.show_spinner = true;
            var formData = new FormData();
            formData.append('action', 'hide');
            formData.append('document_id', file.id);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);

            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = vm.get_documents()
                    //vm.documents = res.body;
                    vm.show_spinner = false;
                });

        },
        
        uploadFile(e){
            let vm = this;
            let _file = null;

            if (e.target.files && e.target.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(e.target.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = e.target.files[0];
            }
            return _file
        },

        save_document: function(e) {
            let vm = this; 
            //var $spinner = $("#file-spinner");
            //$spinner.toggleClass("fa fa-cog fa-spin");
            vm.show_spinner = true;
            if(e.target.files[0].name.length > 255){
                vm.show_spinner=false;
                vm.showError=true;
                vm.errorString='File name exceeds maximum file name length limit';
            }
            else{
            vm.showError=false;
            vm.errorString='';
            var formData = new FormData();
            formData.append('action', 'save');
            formData.append('proposal_id', vm.proposal_id);
            formData.append('input_name', vm.name);
            formData.append('filename', e.target.files[0].name);
            formData.append('_file', vm.uploadFile(e));
            formData.append('csrfmiddlewaretoken', vm.csrf_token);

            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = res.body;
                    //$spinner.toggleClass("fa fa-cog fa-spin");
                    vm.show_spinner = false;
                },err=>{
                });
            }
        },

        num_documents: function() {
            let vm = this;
            if (vm.documents) {
                return vm.documents.length;
            }
            return 0;
        },

    },
    mounted:function () {
        let vm = this;
        vm.documents = vm.get_documents();
        if (vm.value) {
            //vm.files = (Array.isArray(vm.value))? vm.value : [vm.value];
            if (Array.isArray(vm.value)) {
                vm.value;
            } else {
                var file_names = vm.value.replace(/ /g,'_').split(",")
                vm.files = file_names.map(function( file_name ) { 
                      return {name: file_name}; 
                });
            }
        }
    }
}

</script>

<style lang="css">
    input {
        box-shadow:none;
    }
</style>
