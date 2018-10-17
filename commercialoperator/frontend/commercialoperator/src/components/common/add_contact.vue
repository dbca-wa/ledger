<template lang="html">
    <div id="change-contact">
        <modal @ok="ok()" @cancel="cancel()" title="Add Contact" large>
            <form class="form-horizontal" name="addContactForm">
                <div class="row">
                    <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                    <div class="col-lg-12">
                        <div class="row">
                            <div class="form-group">
                                <label class="col-md-2 control-label pull-left"  for="Name">Given Name(s): </label>
                                <div class="col-md-10">
                                    <input type="text" class="form-control" name="name" v-model="contact.first_name" />
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="form-group">
                                <label class="col-md-2 control-label pull-left"  for="Name">Surname: </label>
                                <div class="col-md-10">
                                    <input type="text" class="form-control" name="name" v-model="contact.last_name" />
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="form-group">
                                <label class="col-md-2 control-label pull-left"  for="Phone">Phone: </label>
                                <div class="col-md-10">
                                    <input type="text" class="form-control" name="phone" v-model="contact.phone_number" />
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="form-group">
                                <label class="col-md-2 control-label pull-left"  for="Mobile">Mobile: </label>
                                <div class="col-md-10">
                                    <input type="text" class="form-control" name="mobile" v-model="contact.mobile_number" />
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="form-group">
                                <label class="col-md-2 control-label pull-left"  for="Fax">Fax: </label>
                                <div class="col-md-10">
                                    <input type="text" class="form-control" name="fax" v-model="contact.fax_number" />
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="form-group">
                                <label class="col-md-2 control-label pull-left"  for="Email">Email: </label>
                                <div class="col-md-10">
                                    <input type="text" class="form-control" name="email" v-model="contact.email" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
export default {
    name:'Add-Organisation-Contact',
    components:{
        modal,
        alert
    },
    props:{
            org_id:{
                type:Number,
            },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            contact: {},
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
            this.errors = false;
            this.form.reset();
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
