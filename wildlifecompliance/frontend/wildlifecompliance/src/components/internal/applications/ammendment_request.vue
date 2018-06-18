<template lang="html">
    <div id="internal-application-ammend">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Ammendment Request" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="ammedForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Reason</label>
                                        <select class="form-control" name="reason" v-model="ammendment.details">
                                            <option value="All">All</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Details</label>
                                        <textarea class="form-control" name="name" v-model="ammendment.details"></textarea>
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
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import api_endpoints from '../api'
import {helpers} from "@/utils/hooks.js"
export default {
    name:'Add-Organisation-Contact',
    components:{
        modal,
        alert
    },
    props:{
            application_id:{
                type:Number,
            },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            ammendment: {},
            errors: false,
            errorString: '',
            successString: '',
            success:false,
        }
    },
    computed: {
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
        },
        close:function () {
            this.isModalOpen = false;
            this.contact = {};
        },
        fetchContact: function(id){
            let vm = this;
            vm.$http.get(api_endpoints.contact(id)).then((response) => {
                vm.contact = response.body; vm.isModalOpen = true;
            },(error) => {
                console.log(error);
            } );
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            //vm.$parent.loading.push('processing contact');
            if (vm.contact.id){
                let contact = vm.contact;
                vm.$http.put(api_endpoints.organisation_contacts(contact.id),JSON.stringify(contact),{
                        emulateJSON:true,
                    }).then((response)=>{
                        //vm.$parent.loading.splice('processing contact',1);
                        vm.close();
                    },(error)=>{
                        console.log(error);
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                        //vm.$parent.loading.splice('processing contact',1);
                    });
            } else {
                let contact = JSON.parse(JSON.stringify(vm.contact));
                contact.organisation = vm.org_id;
                vm.$http.post(api_endpoints.organisation_contacts,JSON.stringify(contact),{
                        emulateJSON:true,
                    }).then((response)=>{
                        //vm.$parent.loading.splice('processing contact',1);
                        vm.close();
                        vm.$parent.addedContact();
                    },(error)=>{
                        console.log(error);
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                        //vm.$parent.loading.splice('processing contact',1);
                    });
                
            }
        },
        addFormValidations: function() {
            let vm = this;
            $(vm.form).validate({
                rules: {
                    arrival:"required",
                    departure:"required",
                    campground:"required",
                    campsite:{
                        required: {
                            depends: function(el){
                                return vm.campsites.length > 0;
                            }
                        }
                    }
                },
                messages: {
                    arrival:"field is required",
                    departure:"field is required",
                    campground:"field is required",
                    campsite:"field is required"
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
       }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.addContactForm;
       vm.addFormValidations();
       //console.log(validate);
   }
}
</script>

<style lang="css">
</style>
