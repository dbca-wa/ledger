<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" :num_files="num_documents()">{{label}}</label>
            <!--template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template-->

            <!--template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template-->

            <!--CommentBlock 
                :label="label"
                :name="name"
                :field_data="field_data"
                /-->

            <div v-if="files">
                <div v-for="v in documents">
                    <p>
                        File: <a :href="v.file" target="_blank">{{v.name}}</a> &nbsp;
                        <span v-if="!readonly">
                            <a @click="delete_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                        </span>
                    </p>
                </div>
                <div v-if="show_spinner"><i class='fa fa-2x fa-spinner fa-spin'></i></div>
            </div>
            <div v-if="!readonly" v-for="n in repeat">
                <div v-if="isRepeatable || (!isRepeatable && num_documents()==0)">
                    <input :name="name" type="file" :data-que="n" :accept="fileTypes" @change="handleChangeWrapper"/>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks';
//import CommentBlock from './comment_block.vue';
//import HelpText from './help_text.vue';
import Vue from 'vue';
import { mapGetters } from 'vuex';
export default {
    name: "FileField",
    props:{
        //application_id: null,
        name:String,
        label:String,
        id:String,
        //isRequired:String,
        //help_text:String,
        //field_data:Object,
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
        documentActionUrl: String,
        //createDocumentActionUrl: Function,
        parent_id: Number,
    },
    //components: {CommentBlock, HelpText},
    data:function(){
        return {
            repeat:1,
            files:[],
            show_spinner: false,
            documents:[],
            filename:null,
            help_text_url:'',
            commsLogId: null,
            document_action_url: this.documentActionUrl,
        }
    },
    computed: {
        csrf_token: function() {
            return helpers.getCookie('csrftoken')
        },
    },
    watch: {
        documents: {
            handler: async function () {
                await this.$emit('update-parent');
            },
            deep: true
        },
    },

    methods:{
        handleChange: function (e) {
            let vm = this;

            if (vm.isRepeatable && e.target.files) {
                let  el = $(e.target).attr('data-que');
                let avail = $('input[name='+e.target.name+']');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                console.log(avail);
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
                this.$nextTick(() => {
                    this.save_document(e);
                });
            }

        },

        get_documents: async function() {
            this.show_spinner = true;

            if (this.document_action_url) {
                var formData = new FormData();
                formData.append('action', 'list');
                if (this.commsLogId) {
                    formData.append('comms_log_id', this.commsLogId);
                }
                formData.append('input_name', this.name);
                formData.append('csrfmiddlewaretoken', this.csrf_token);
                let res = await Vue.http.post(this.document_action_url, formData)
                //let res = await Vue.http.post(this.documentActionUrl, formData)
                this.documents = res.body.filedata;
                this.commsLogId = res.body.comms_instance_id;
                //console.log(vm.documents);
            }
            this.show_spinner = false;

        },

        delete_document: async function(file) {
            this.show_spinner = true;

            var formData = new FormData();
            formData.append('action', 'delete');
            if (this.commsLogId) {
                formData.append('comms_log_id', this.commsLogId);
            }
            formData.append('document_id', file.id);
            formData.append('csrfmiddlewaretoken', this.csrf_token);
            if (this.document_action_url) {
                let res = await Vue.http.post(this.document_action_url, formData)
                console.log(res.body)
                this.documents = res.body.filedata;
                //this.documents = await this.get_documents()
                this.commsLogId = res.body.comms_instance_id;
            }
            //vm.documents = res.body;
            this.show_spinner = false;

        },
        cancel: async function(file) {
            this.show_spinner = true;

            let formData = new FormData();
            formData.append('action', 'cancel');
            if (this.commsLogId) {
                formData.append('comms_log_id', this.commsLogId);
            }
            formData.append('csrfmiddlewaretoken', this.csrf_token);
            if (this.document_action_url) {
                let res = await Vue.http.post(this.document_action_url, formData)
            }
            this.show_spinner = false;
        },
        
        uploadFile(e){
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

        handleChangeWrapper: async function(e) {
            console.log(this.document_action_url)
            if (!this.document_action_url) {
                // parameter must be passed to the parent method to ensure that parent object id is updated
                // and document_action_url is passed the correct string
                await this.$emit('create-parent', (done) => {
                    console.log("inside emit")
                    console.log(done)
                    this.handleChange(e);
                });
            } else {
                this.handleChange(e);
            }
        },

        save_document: async function(e) {
            this.show_spinner = true;

            if (this.document_action_url) {
                var formData = new FormData();
                formData.append('action', 'save');
                if (this.commsLogId) {
                    formData.append('comms_log_id', this.commsLogId);
                }
                formData.append('input_name', this.name);
                formData.append('filename', e.target.files[0].name);
                formData.append('_file', this.uploadFile(e));
                formData.append('csrfmiddlewaretoken', this.csrf_token);
                let res = await Vue.http.post(this.document_action_url, formData)
                
                this.documents = res.body.filedata;
                this.commsLogId = res.body.comms_instance_id;
                this.show_spinner = false;
            } else {
                console.log("no documentActionUrl");
            }

        },

        num_documents: function() {
            if (this.documents) {
                return this.documents.length;
            }
            return 0;
        },
    },
    mounted:function () {
        if (this.value) {
            //vm.files = (Array.isArray(vm.value))? vm.value : [vm.value];
            if (Array.isArray(this.value)) {
                this.value;
            } else {
                let file_names = this.value.replace(/ /g,'_').split(",")
                this.files = file_names.map(function( file_name ) { 
                      return {name: file_name}; 
                });
            }
        }
        this.$nextTick(async () => {
            console.log(this.document_action_url);
            await this.get_documents();
        });
    },
    //updated: async function() {
        //this.$nextTick(async () => {
            //await this.$emit('update-parent', (done) => {
              //  console.log("inside emit")
                //console.log(done)
            //});
      //  });
    //},
        
}

</script>

<style lang="css">
    input {
        box-shadow:none;
    }
</style>
