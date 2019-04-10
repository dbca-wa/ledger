<template lang="html" :id="id">
<div>
    <label>I am here</label>
    <label>I am here too</label>
    <div>
                <fieldset class="scheduler-border">
                    <legend class="scheduler-border">{{accreditation.accreditation_type}}</legend>
                    <div class="form-group">
                        <div class="row">
                            <div class="col-sm-3">
                                <label class="control-label pull-right"  for="Name">Expiry Date</label>
                            </div>
                            <div class="col-sm-9">
                                <div class="input-group date" ref="accreditation_expiry" style="width: 70%;">
                                    <input type="text" class="form-control" v-model="accreditation.accreditation_expiry" name="accreditation_expiry" placeholder="DD/MM/YYYY">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-3">
                                <label class="control-label pull-left"  for="Name">Accreditation certificates</label>
                            </div>
                            <div class="col-sm-9">
                                <FileField :proposal_id="proposal_id" isRepeatable="false" name="accreditation_certificate" :id="'accreditation'+accreditation_type+proposal_id"></FileField>
                            </div>
                        </div>
                    </div>
                </fieldset>
            </div>  
</div>
</template>

<script>
import FileField from '@/components/forms/filefield.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'

export default {
    name:"accreditation",
    props:{
        proposal_id: null,
        accreditation: {
                type: Object,
                required:true
            },
        id:String,
        assessor_readonly: Boolean,
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
        readonly:Boolean,
    },
    components: {
        FileField,
    },
    data:function(){
        return {
            repeat:1,
        }
    },

    //computed: {
    //    csrf_token: function() {
    //        return helpers.getCookie('csrftoken')
    //    }
    //},

    computed: {
        
    },

    methods:{
        

        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
        handleChange:function (e) {
            let vm = this;
            console.log(e.target.name)
            vm.show_spinner = true;
            if (vm.isRepeatable) {
                let  el = $(e.target).attr('data-que');
                let avail = $('input[name='+e.target.name+']');

                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                avail.pop();
                console.log('el', el, 'avail',avail.indexOf(el))
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
            vm.files.push(e.target.files[0]);

            if (e.target.files.length > 0) {
                //vm.upload_file(e)
                vm.save_document(e);
            }

            vm.show_spinner = false;
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
            formData.append('required_doc_id', vm.required_doc_id);
            //formData.append('csrfmiddlewaretoken', vm.csrf_token);
            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = res.body;
                    //console.log(vm.documents);
                    vm.show_spinner = false;
                });

        },

        delete_document: function(file) {
            let vm = this;
            vm.show_spinner = true;

            var formData = new FormData();
            formData.append('action', 'delete');
            formData.append('document_id', file.id);
            formData.append('required_doc_id', vm.required_doc_id);
            //formData.append('csrfmiddlewaretoken', vm.csrf_token);

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

            var formData = new FormData();
            formData.append('action', 'save');
            formData.append('proposal_id', vm.proposal_id);
            formData.append('input_name', vm.name);
            formData.append('filename', e.target.files[0].name);
            formData.append('_file', vm.uploadFile(e));
            formData.append('required_doc_id', vm.required_doc_id);
            //formData.append('csrfmiddlewaretoken', vm.csrf_token);

            vm.$http.post(vm.proposal_document_action, formData)
                .then(res=>{
                    vm.documents = res.body;
                },err=>{
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
        let vm = this;
        // vm.documents = vm.get_documents();
        // if (vm.value) {
        //     //vm.files = (Array.isArray(vm.value))? vm.value : [vm.value];
        //     if (Array.isArray(vm.value)) {
        //         vm.value;
        //     } else {
        //         var file_names = vm.value.replace(/ /g,'_').split(",")
        //         vm.files = file_names.map(function( file_name ) { 
        //               return {name: file_name}; 
        //         });
        //     }
        // }
    }
}

</script>

<style lang="css">
    fieldset.scheduler-border {
        border: 1px groove #ddd !important;
        padding: 0 1.4em 1.4em 1.4em !important;
        margin: 0 0 1.5em 0 !important;
        -webkit-box-shadow:  0px 0px 0px 0px #000;
                box-shadow:  0px 0px 0px 0px #000;
    }
    legend.scheduler-border {
        width:inherit; /* Or auto */
        padding:0 10px; /* To give a bit of padding on the left and right */
        border-bottom:none;
    }
</style>
