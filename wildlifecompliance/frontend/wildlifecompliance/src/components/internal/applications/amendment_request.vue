<template lang="html">
    <div id="internal-application-amend">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Amendment Request" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="amendForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row">
                                <label class="control-label">Request Amendment for the application</label>
                            </div>
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">

                                    <label class="control-label"  for="Name">Licensed activity to amend </label>
                                    <div v-for="item in amendment.activity_name" v-model="amendment.activity_name">{{item}}</div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Reason</label>
                                        <select class="form-control" name="reason" ref="reason" v-model="amendment.reason">
                                            <option v-for="item in reason_choices" :value="item.key">{{item.value}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Details</label>
                                        <textarea class="form-control" name="name" v-model="amendment.text">{{amendment.text}}</textarea>
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
import {helpers, api_endpoints} from "@/utils/hooks.js"
import { mapGetters } from 'vuex'
export default {
    name:'amendment-request',
    components:{
        modal,
        alert
    },
    props:{
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            amendment: {
                reason:'',
                amendingApplication: false,
                application: this.$store.getters.application_id,
                text:null,
                activity_name:null,
                activity_id:[]
            },
            reason_choices: {},
            errors: false,
            errorString: '',
            validation_form: null,
        }
    },
    computed: {
        ...mapGetters([
            'application_id',
        ]),
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    methods:{
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }
        },
        cancel:function () {
            // let vm = this;
            // vm.close();
            this.isModalOpen = false;
            this.amendment = {
                reason: '',
                application: this.application_id,
                text:null,
                licence_activity:null,
                activity_name:null
            };
        },
        close:function () {
            this.isModalOpen = false;
            this.amendment = {
                reason: '',
                application: this.application_id,
                text:null,
                licence_activity:null,
                activity_name:null
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
            console.log('this is amendment object')
            console.log(vm.amendment)
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let amendment = JSON.parse(JSON.stringify(vm.amendment));
            vm.$http.post('/api/amendment.json',JSON.stringify(amendment),{
                        emulateJSON:true,
                    }).then((response)=>{
                        //vm.$parent.loading.splice('processing contact',1);
                        swal(
                             'Sent',
                             'An email has been sent to applicant with the request to amend this Application',
                             'success'
                        );
                        vm.amendingApplication = true;
                        vm.close();
                        //vm.$emit('refreshFromResponse',response);
                        Vue.http.get(`/api/application/${vm.application_id}/internal_application.json`).then((res)=>
                        {
                            vm.$emit('refreshFromResponse',res);
                            
                        },(error)=>{
                            console.log(error);
                        });

                    },(error)=>{
                        console.log(error);
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                        vm.amendingApplication = true;
                        
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
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.amendment.reason = selected.val();
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
