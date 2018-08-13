<template lang="html">
    <div>
        <div class="form-group">

            <!-- using num_files to determine if files have been uploaded for this question/label (used in disturbance/frontend/disturbance/src/components/external/proposal.vue) -->
            <label :id="id" :num_files="files.length">{{label}}</label>
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
            <div v-if="files">
                <!--
                <div v-for="v in files">
                    <p>
                        File: <a :href="docsUrl+v.name" target="_blank">{{v.name}}</a> &nbsp;
                        <span v-if="!readonly">
                            <a @click="delete_file(v.name)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                        </span>
                    </p>
                    <input :name="name+'-existing'" type="hidden" :value="value"/>
                </div>
                
                <div v-for="v in documents">
                    <p>
                        Doc: <a :href="v.file" target="_blank">{{v.name}}</a> &nbsp;
                        <span v-if="!readonly">
                            <a @click="delete_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                        </span>
                    </p>
                </div>
                -->
                <div v-for="v in documents">
                    <p>
                        Doc: <a :href="v.file" target="_blank">{{v.name}}</a> &nbsp;
                        <span v-if="!readonly">
                            <a @click="delete_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                        </span>
                    </p>
                </div>


                <!--<span v-if="show_spinner"><i class="fa fa-circle-o-notch fa-spin fa-fw"></i></span>-->
                <span v-if="show_spinner"><i class='fa fa-2x fa-spinner fa-spin'></i></span>
            </div>
            <div v-if="!readonly" v-for="n in repeat">
                <div v-if="isRepeatable || (!isRepeatable && documents.length==0)">
                    <input :name="name" type="file" class="form-control" :data-que="n" :accept="fileTypes" @change="handleChange" :required="isRequired"/>
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
                return "image/*,application/pdf,text/csv,application/msword"
            }
        },
        isRepeatable:Boolean,
        readonly:Boolean,
        docsUrl: String,
        document_id: String,
    },
    components: {Comment, HelpText},
    data:function(){
        return {
            repeat:1,
            files:[],
            showingComment: false,
            show_spinner: false,
            documents:[],
            filename:null,
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
        proposal_update_url: function() {
          return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/update_files.json` : '';
        },
        proposal_list_docs: function() {
          return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/list_documents/?input_name=${this.name}` : '';
        },
        proposal_delete_doc: function() {
          return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/delete_document/` : '';
        },
        proposal_save_doc: function() {
          //return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/process_document?action=save&input_name=${this.name}&filename=${this.files[0].name}` : '';
          return (this.proposal_id) ? `/api/proposal/${this.proposal_id}/process_document/` : '';
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
            if (this.isRepeatable) {
                let  el = $(e.target).attr('data-que');
                let avail = $('input[name='+e.target.name+']');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                avail.pop();
                if (this.repeat == 1) {
                    this.repeat+=1;
                }else {
                    if (avail.indexOf(el) < 0 ){
                        this.repeat+=1;
                    }
                }
                $(e.target).css({ 'display': 'none'});

            } else {
                this.files = [];
            }
            this.files.push(e.target.files[0]);

            if (e.target.files.length > 0) {
                //this.upload_file(e)
                this.save_document(e);
            }

            if (!this.isRepeatable) {
				/* reset value of 'Choose File' button to null, for non-repeatable file upload buttons */
				$(e.target).val('');
			}
			$(e.target).val('');

            this.$nextTick(() => {
                //this.documents = this.get_documents();
            });
        },

        upload_file: function(e) {
            let vm = this;
            $("[id=save_and_continue_btn][value='Save Without Confirmation']").trigger( "click" );
        },
        /*
        removeImage: function (filename) {
            let vm = this;
            //var filename = e.target.getAttribute('filename');
            if (filename) {
                vm.files.pop(filename);
                $('input[name='+vm.name+']').val(null);

                this.$nextTick(() => {
                    $("[id=save_and_continue_btn][value='Save Without Confirmation']").trigger( "click" );
                });
            }
        },
		*/
        delete_file: function (filename) {
            let vm = this;
            vm.show_spinner = true;

            var file_names = [] /* file names of remaining */
            for (var idx in vm.files) { 
                if (vm.files[idx].name==filename){ 
                    // pop filename from array
                    //this.files = vm.files.filter(function(item) { return item !== filename })
                } else {
                    file_names.push(this.files[idx].name)
                }

            }

            var formData = new FormData();
            formData.append('proposal_id', vm.proposal_id);
            formData.append(vm.name, file_names.join());
            formData.append(vm.name + '_' + 'delete_file', filename);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);
            vm.$http.post(vm.proposal_update_url,formData)
                .then(function(){
                    vm.files = vm.files.filter(function(item) { return item.name !== filename }); // pop filename from array
                    vm.show_spinner = false;
                });

            /*
            vm.$http.post(vm.proposal_update_url,formData);
            vm.files = vm.files.filter(function(item) { return item.name !== filename }); // pop filename from array
            vm.show_spinner = false;
            */
        },

        get_documents: function() {
            let vm = this;

            var formData = new FormData();
            formData.append('action', 'list');
            formData.append('input_name', vm.name);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);
            //vm.$http.get(vm.proposal_list_docs)
            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = res.body;
                    //console.log(vm.documents);
                });

        },

        delete_document: function(file) {
            let vm = this;

            var formData = new FormData();
            formData.append('action', 'delete');
            formData.append('document_id', file.id);
            formData.append('csrfmiddlewaretoken', vm.csrf_token);

            //vm.$http.post(vm.proposal_delete_doc, formData)
            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = vm.get_documents()
                    //vm.documents = res.body;
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

            var formData = new FormData();
            formData.append('action', 'save');
            formData.append('proposal_id', vm.proposal_id);
            formData.append('input_name', vm.name);
            formData.append('filename', e.target.files[0].name);
            formData.append('_file', vm.uploadFile(e));
            formData.append('csrfmiddlewaretoken', vm.csrf_token);

            //vm.$http.post(vm.proposal_save_doc, formData)
            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = res.body;
                },err=>{
                });

        }

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
