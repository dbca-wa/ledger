<template lang="html">
    <div id="change-booking">
        <modal @ok="ok()" @cancel="cancel()" title="Change Booking" large>
            <form class="form-horizontal" name="changebookingForm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="form-group">
                            <label class="col-md-2 control-label pull-left"  for="Dates">Dates: </label>
                            <div class="col-md-4">
                                <div class="input-group">
                                    <input type="text" class="form-control" name="arrival" placeholder="DD/MM/YYYY">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="input-group">
                                    <input type="text" class="form-control" name="depature" placeholder="DD/MM/YYYY">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-md-2 control-label pull-left"  for="Campground">Campground: </label>
                            <div class="col-md-4">
                                <select class="form-control" name="campground" v-model="selectedCampground">
                                    <option value="">Select Campground</option>
                                    <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group" v-show="selectedCampground">
                            <label class="col-md-2 control-label pull-left"  for="Campsite">Campsite: </label>
                            <div class="col-md-4">
                                <select class="form-control" name="campsite"  >
                                    <option value="">Select Campsite</option>
                                    <option v-for="campsite in campsites" :value="campsite.id">{{campsite.name}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </modal>
    </div>
</template>

<script>
import modal from '../utils/bootstrap-modal.vue'
import {$,api_endpoints,datetimepicker} from "../../hooks.js"
export default {
    name:'change-booking',
    components:{
        modal
    },
    props:{
            booking:{
                type:Object,
                default:function () {
                    return{

                    }
                }
            },
            campgrounds:{
                type:Array,
                default:function () {
                    return [];
                }
            }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            selectedCampground:"",
            campsites:[],
            form:null
        }
    },
    watch:{
            selectedCampground:function () {
                let vm =this;
                if (vm.selectedCampground) {
                    vm.$http.get(api_endpoints.campgroundCampsites(vm.selectedCampground)).then((response)=>{
                        vm.campsites = response.body;
                    },(response) => {
                        console.log(response);
                    });
                }else {
                    vm.campsites = [];
                }
            }
    },
    methods:{
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.close();
            }
        },
        cancel:function () {
        },
        close:function () {
            this.isModalOpen = false;
        },
        addFormValidations: function() {
            let vm = this;
            $(vm.form).validate({
                rules: {
                    arrival:"required",
                    depature:"required",
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
                    depature:"field is required",
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
       }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.changebookingForm;
       vm.addFormValidations();
       let datepickerOptions = {
           minDate:new Date(),
           format: 'DD/MM/YYYY',
           showClear:true
       };
       $(vm.form.arrival).datetimepicker(datepickerOptions);
       $(vm.form.depature).datetimepicker(datepickerOptions);
   }
}
</script>

<style lang="css">
</style>
