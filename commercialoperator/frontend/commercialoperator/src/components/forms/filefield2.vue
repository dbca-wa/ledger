<template lang="html">
    <div>
      <div class="col-sm-12">

        <!--<div v-if="uploaded_documents.length>0" class="form-group">-->
        <div v-if="has_uploaded_docs" class="form-group">
            <div class="row">
                <div class="col-sm-6">
                    <label class="control-label pull-left"  for="Name">Uploaded Documents</label>
                </div>
                <div class="col-sm-6">
                    <div class="input-group date" ref="due_date" style="width: 70%;">
                        <div v-for="v in uploaded_documents" class="row">
                            <span>
                                <a :href="v._file" target="_blank">{{v.name}}</a> &nbsp;
                                <a @click="delete_document(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="form-group">
            <div class="row">
                <div class="col-sm-12">
                    <div v-for="n in repeat">
                        <div v-if="isRepeatable || (!isRepeatable && num_documents()==0)">
                            <span class="btn btn-link btn-file">
                                <input :name="name" type="file" class="form-control" :data-que="n" :accept="fileTypes" @change="handleChange($event)" :required="isRequired"/>
                                <u>Attach Document</u>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="form-group">
            <div class="row">
                <!--
                <div class="col-sm-3">
                    <label v-if="label" :id="id" :num_files="num_documents()">{{label}}</label>
                </div>
                -->
                <div class="col-sm-9">
                    <div v-if="files">
                        <div v-for="v in files">
                            <p>
                                <!--File: <a target="_blank">{{v.name}}</a> &nbsp;-->
                                File:{{v.name}} &nbsp;
                                <a @click="pop_file(v)" class="fa fa-trash-o" title="Remove file" :filename="v.name" style="cursor: pointer; color:red;"></a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <span v-if="show_spinner"><i class='fa fa-2x fa-spinner fa-spin'></i></span>

    </div>
</template>

<script>
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'

export default {
    props:{
        proposal_id: null,
        required_doc_id:null,
        name:String,
        label:String,
        id:String,
        isRequired:String,
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
        delete_url: String,
        uploaded_documents: Array,
    },
    components: {},
    data:function(){
        return {
            repeat:1,
            files: [],
            _files: [
                {
                    'file': null,
                    'name': ''
                }
            ],
            showingComment: false,
            show_spinner: false,
            documents:[],
            filename:null,
        }
    },
    computed: {
        csrf_token: function() {
            return helpers.getCookie('csrftoken')
        },
        has_uploaded_docs: function() {
          return this.uploaded_documents ? true : false;
        }
    },

    methods:{
        reset_files(){
            this.files = [];
        },
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
        handleChange:function (e) {
            let vm = this;
            //console.log(e.target.name)
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
                $(e.target.parentElement).css({ 'display': 'none'});//to hide <span> element btn-link

            } else {
                vm.files = [];
            }
            vm.add_file(e)

        },
        add_file(e){
            let vm = this;
            var file_updated = false;
            for(var idx in vm.files) {
                for(var key in vm.files[idx]) {
                    var name = vm.files[idx][key];
                    if (name==e.target.files[0].name) {
                        // replace the file with new one with same name
                        vm.files[idx]['file'] = e.target.files[0];
                        file_updated = true;
                    }
                }
            }

            if (!file_updated) {
                vm.files.push( {name: e.target.files[0].name, file: e.target.files[0]} );
            }
        },
        pop_file(v){
            /* pops file from the local files array - client side (before it has been saved to the server) */
            let vm = this;
            for(var idx in vm.files) {
                for(var key in vm.files[idx]) {
                    var name = vm.files[idx][key];
                    if (name==v.name) {
                        // Remove the file from the array
                        vm.files.splice(idx, 1);
                        return;
                    }
                }
            }

            if (!file_updated) {
                vm.files.push( {name: e.target.files[0].name, file: e.target.files[0]} );
            }
        },
        delete_document: function(file) {
            /* deletes, previously saved file, from the server */
            let vm = this;
            vm.show_spinner = true;
            var data = {id:file.id, name:file.name}

            swal({
                title: "Delete Document",
                text: "Are you sure you want to delete this document?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Delete Document',
                confirmButtonColor:'#d9534f'
            }).then(() => {
                //vm.$http.post('/api/proposal_requirements/'+vm.requirement.id+'/delete_document/', data,{
                vm.$http.post(vm.delete_url, data,{
                    emulateJSON:true,
                }).then((response)=>{
                    vm.uploaded_documents = response.body;
                    vm.$emit('refreshFromResponse',response.body);
                    vm.show_spinner = false;
                },err=>{
                    console.log(err);
                });
            },(error) => {
            });
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
    }
}

</script>

<style lang="css">
    input {
        box-shadow:none;
    }
    .btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
</style>
