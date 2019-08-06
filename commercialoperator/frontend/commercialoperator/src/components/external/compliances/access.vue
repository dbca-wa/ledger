<template>
<div class="container" id="externalCompliance">
    <div v-if="isDiscarded" class="row" style="color:red;">
        <h3>You cannot access this Compliance with requirements as this has been discarded.</h3>
        
    </div>
    <div v-else class="row">
        <div v-if="!isFinalised">
            <div v-if="hasAmendmentRequest" class="row" style="color:red;">
                <div class="col-lg-12 pull-right">
                  <div class="panel panel-default">
                    <div class="panel-heading">

                        <h3 class="panel-title" style="color:red;">An amendment has been requested for this Compliance with Requirements
                          <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="oBody">
                                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                            </a>
                        </h3>
                      </div>
                      <div class="panel-body collapse in" :id="oBody">
                        <div v-for="a in amendment_request">                      
                          <p>Reason: {{a.reason}}</p>
                          <p>Details: {{a.text}}</p>                        
                      </div>
                    </div>
                  </div>
                </div>
              </div>
           </div>

        <h3><strong>Compliance with Requirements: {{ compliance.reference }}</strong></h3>

      
        
        <div class="col-md-12">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Compliance with Requirements
                                        <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                        </a>
                        </h3>
                    </div>
                  <div class="panel-body panel-collapse in" :id="pdBody">
                        <div class="row">
                           <div class="col-md-12"> 
                            <form class="form-horizontal" name="complianceForm" method="post">
                                <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                                
                                <div class="row">
                                        
                                            <div class="form-group">
                                             <label class="col-sm-3 control-label pull-left"  for="Name">Requirement:</label>
                                             <div class="col-sm-6">{{compliance.requirement}}</div>
                                            </div>
                                   
                                </div>

                                <div class="row">
                                    <div class="form-group">
                                            <label class="col-sm-3 control-label pull-left"  for="Name">Details:</label>
                                            <div class="col-sm-6">
                                            <textarea :disabled="isFinalised" class="form-control" name="detail" placeholder="" v-model="compliance.text"></textarea>
                                            </div>
                                        </div>                                 
                                </div>

                                <div class="row">
                                        
                                            <!--<div v-if="isFinalised && hasDocuments" class="form-group"> -->
                                            <div v-if="hasDocuments" class="form-group">
                                             <div class="col-sm-3 control-label pull-left" >  
                                             <label  for="Name">Documents:</label>
                                             </div> 
                                             <div class="col-sm-6">
                                                <div class="row" v-for="d in compliance.documents">
                                                    <a :href="d[1]" target="_blank" class="control-label pull-left">{{d[0]   }}</a>
                                                    <span v-if="!isFinalisedi && d.can_delete">
                                                        <a @click="delete_document(d)" class="fa fa-trash-o control-label" title="Remove file" style="cursor: pointer; color:red;"></a>
                                                    </span>
                                                    <span v-else >    <i class="fa fa-info-circle" aria-hidden="true" title="Previously submitted documents cannot be deleted" style="cursor: pointer;"></i></span>
                                                </div>
                                            </div>
                                            </div>
                                </div>

                                <div class="row">
                                    <div v-if="!isFinalised" class="form-group"> 
                                        <label class="col-sm-3 control-label pull-left"  for="Name">Attachments:</label>
                                    <div class="col-sm-6">
                                        <template v-for="(f,i) in files">
                                            <div :class="'row top-buffer file-row-'+i">
                                                <div class="col-sm-4">
                                                    <span v-if="f.file == null" class="btn btn-info btn-file pull-left" style="margin-bottom: 5px">
                                                        Attach File <input type="file" :name="'file-upload-'+i" :class="'file-upload-'+i" @change="uploadFile('file-upload-'+i,f)"/>
                                                    </span>
                                                    <span v-else class="btn btn-info btn-file pull-left" style="margin-bottom: 5px">
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
                                        <a href="" @click.prevent="attachAnother"><i class="fa fa-lg fa-plus top-buffer-2x"></i></a>
                                    </div>
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="form-group">
                                    <div class="col-lg-2 pull-right">
                                        <button v-if="!isFinalised" @click.prevent="submit()" class="btn btn-primary">Submit</button>
                                        <button v-if="!isFinalised" @click.prevent="close()" class="btn btn-primary">Close</button>
                                    </div>
                                   
                                </div>
                                </div>

                            </form>
                            </div>
                        </div>
                    </div> 
                </div>
            </div>
        </div>
    </div>

</template>
<script>
import $ from 'jquery'
import Vue from 'vue'
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'externalCompliance',
  data() {
    let vm = this;
    return {
        form:null,
        loading: [],        
        compliance: {},
        original_compliance: {},
        amendment_request: [],
        hasAmendmentRequest: false,
        isFinalised: false,
        errors: false,
        errorString: '',
        pdBody: 'pdBody'+vm._uid,
        oBody: 'oBody'+vm._uid,
        isFinalised: false,
        pdBody: 'pdBody'+vm._uid,
        hasDocuments: false,
        validation_form: null,
        files: [
                {
                    'file': null,
                    'name': ''
                }
            ]
     
    }
  },
  watch: {
    
    isFinalised: function(){             
        return this.compliance && (this.compliance.customer_status == "Under Review" || this.compliance.customer_status == "Approved");
    },
    hasDocuments: function(){             
        return this.compliance && this.compliance.documents;
   }
  },
  filters: {
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY HH:mm:ss');
    }
  },
 
  components: {
    datatable,
    CommsLogs
  },
  computed: {
    showError: function() {
            var vm = this;
            return vm.errors;
        },
    isLoading: function () {
      return this.loading.length > 0;
    },
    isDiscarded: function(){         
        return this.compliance && (this.compliance.customer_status == "Discarded");
    },
    
  },
  methods: {
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
    submit:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }                
                //vm.sendData();
    },

    close:function () {
            let vm = this;           
            this.compliance = {};
            this.errors = false;
            $('.has-error').removeClass('has-error');
            this.validation_form.resetForm();
            let file_length = vm.files.length;
            this.files = [];
            for (var i = 0; i < file_length;i++){
                vm.$nextTick(() => {
                    $('.file-row-'+i).remove();
                });
            }
            this.attachAnother();
            vm.$router.push({ name: 'external-proposals-dash'}); //Navigate to dashboard
        },

    addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    detail: "required"
                    
                     
                },
                messages: {              
                    detail: "field is required",
                                         
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


    setAmendmentData: function(amendment_request){
      this.amendment_request = amendment_request;
      
      if (amendment_request.length > 0)
        this.hasAmendmentRequest = true;    
    },

    delete_document: function(doc){
        let vm= this;
        let data = {'document': doc}
        if(doc)
        {
          vm.$http.post(helpers.add_endpoint_json(api_endpoints.compliances,vm.compliance.id+'/delete_document'),JSON.stringify(data),{
                emulateJSON:true
                }).then((response)=>{
                    vm.refreshFromResponse(response);                   
                    vm.compliance = response.body;       
                },(error)=>{
                    vm.errors = true;
                    vm.errorString = helpers.apiVueResourceError(error);
                });              
        }
    },


    sendData:function(){
            let vm = this;
            vm.errors = false;
            let data = new FormData(vm.form);
            vm.addingComms = true;            
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.compliances,vm.compliance.id+'/submit'),data,{
                emulateJSON:true
                }).then((response)=>{
                    vm.addingCompliance = false;
                    vm.refreshFromResponse(response);                   
                    /*swal(
                     'Submit',
                     'Your Compliance with Requirement has been submitted',
                     'success'
                    );*/
                    vm.compliance = response.body;
                    vm.$router.push({
                    name: 'submit_compliance',
                    params: { compliance: vm.compliance} 
                });
                        
                },(error)=>{
                    vm.errors = true;
                    vm.addingCompliance = false;
                    vm.errorString = helpers.apiVueResourceError(error);
                });     
    },

    refreshFromResponse:function(response){
            let vm = this;
            vm.original_compliance = helpers.copyObject(response.body);
            vm.compliance = helpers.copyObject(response.body);
            if ( vm.compliance.customer_status == "Under Review" || vm.compliance.customer_status == "Approved" ) { vm.isFinalised = true }
            if (vm.compliance && vm.compliance.documents){ vm.hasDocuments = true}
           
    },  
  },
  mounted: function () {
    let vm = this;
    vm.form = document.forms.complianceForm;
    vm.addFormValidations();     
  },

 beforeRouteEnter: function(to, from, next){
    Vue.http.get(helpers.add_endpoint_json(api_endpoints.compliances,to.params.compliance_id)).then((response) => {
        next(vm => {
            vm.compliance = response.body 
            if ( vm.compliance.customer_status == "Under Review" || vm.compliance.customer_status == "Approved" ) { vm.isFinalised = true }
            if (vm.compliance && vm.compliance.documents){ vm.hasDocuments = true}

            Vue.http.get(helpers.add_endpoint_json(api_endpoints.compliances,to.params.compliance_id+'/amendment_request')).then((res) => {                     
                      vm.setAmendmentData(res.body);                  
                },
              err => {
                        console.log(err);
                  });
        })
    },(error) => {
        console.log(error);
    })
  }
}



</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
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
.top-buffer{margin-top: 0px;}
.top-buffer-2x{margin-top: 0px;}
</style>
