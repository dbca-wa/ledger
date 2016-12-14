<template lang="html" id="bulkpricing">
   <div class="panel panel-default" id="applications">
     <div class="panel-heading" role="tab" id="applications-heading">
         <h4 class="panel-title">
             <a role="button" data-toggle="collapse" href="#applications-collapse"
                aria-expanded="false" aria-controls="applications-collapse">
                 <h3>Bulk Pricing</h3>
             </a>
         </h4>
     </div>
     <div id="applications-collapse" class="panel-collapse collapse in" role="tabpanel"
          aria-labelledby="applications-heading">
        <div class="panel-body">
                  <alert :show.sync="showError" type="danger">{{errorString}}</alert>
                  <div class="well well-sm">
                      <div class="row">
                          <div class="col-lg-12">
                              <div class="col-md-3">
                                  <div class="radio">
                                    <label for="">Set price per : </label>
                                  </div>
                              </div>
                              <!--<div class="col-md-3">
                                  <div class="radio">
                                    <label for="">
                                        <input type="radio" :value="priceOptions[0]" v-model="setPrice">
                                        Price Tariff
                                    </label>
                                  </div>
                              </div>-->
                              <div class="col-md-3">
                                  <div class="radio">
                                    <label for="">
                                        <input type="radio" :value="priceOptions[1]" v-model="setPrice">
                                        Park/Campground
                                    </label>
                                  </div>
                              </div>
                              <div class="col-md-3">
                                  <div class="radio">
                                    <label for="">
                                        <input type="radio" :value="priceOptions[2]" v-model="setPrice">
                                        Campsite Type
                                    </label>
                                  </div>
                              </div>
                          </div>
                      </div>
                  </div>
                  <div class="well well-sm">
                      <div class="row">
                        <div class="col-lg-12">
                            <h3>Add new Pricing Period For Campgrounds</h3><br/>
                            <form name="bulkpricingForm" class="form-horizontal">
                              <div class="form-group">
                                  <div class="col-md-2">
                                      <label class="control-label" >{{setPrice}}</label>
                                  </div>
                                  <div class="col-md-4" v-show="setPrice == priceOptions[0]">
                                      <select class="form-control" >
                                          <option >Price Tarriff</option>
                                      </select>
                                  </div>
                                  <div class="col-md-4" v-show="setPrice == priceOptions[1]">
                                      <select name="tmpPark" v-show="!parks.length > 0" class="form-control" >
                                          <option >Loading...</option>
                                      </select>
                                      <select name="park" v-if="parks.length > 0" class="form-control" v-model="bulkpricing.park">
                                          <option v-for="park in parks" :value="park.url">{{ park.name }}</option>
                                      </select>
                                  </div>
                                  <div class="col-md-4" v-show="setPrice == priceOptions[2]">
                                      <select name="tmpPark" v-show="!campsiteTypes.length > 0" class="form-control" >
                                          <option >Loading...</option>
                                      </select>
                                      <select name="park" v-if="campsiteTypes.length > 0" @change="selectCampsiteType" class="form-control" v-model="bulkpricing.campsiteType">
                                          <option v-for="ct  in campsiteTypes" :value="ct.url">{{ ct.name }}</option>
                                      </select>
                                  </div>
                              </div>
                              <div class="form-group" v-show="setPrice != priceOptions[2] && campgrounds.length > 0">
                                  <div class="col-md-2">
                                      <label class="control-label" >Campground</label>
                                  </div>
                                  <div class="col-md-4">
                                      <select name="tmpCampground" v-show="!parks.length > 0" class="form-control" >
                                          <option >Loading...</option>
                                      </select>
                                      <select name="campground" id="bulkpricingCampgrounds" v-if="parks.length > 0" class="form-control" v-model="bulkpricing.campgrounds" multiple="multiple">
                                          <option v-for="campground in campgrounds" :value="campground.id">{{ campground.name }}</option>
                                      </select>
                                  </div>
                              </div>
                              <div class="form-group">
                                  <div class="col-md-2">
                                      <label>Select Rate: </label>
                                  </div>
                                  <div class="col-md-4">
                                      <select name="rate" v-model="selected_rate" class="form-control" title="testing">
                                          <option value="">Manual Entry</option>
                                          <option v-for="r in rates":value="r.id">{{r.name}}</option>
                                      </select>
                                  </div>
                                    <div class="helper"><i class="fa fa-question-circle"data-toggle="tooltip" data-placement="right" title="Select a rate to prefill the price fields otherwise use the manual entry"></i></div>
                              </div>
                              <div class="form-group">
                                  <div class="col-md-2">
                                      <label>Adult Price: </label>
                                  </div>
                                  <div class="col-md-4">
                                      <input :readonly="selected_rate != ''" name="adult"  v-model="bulkpricing.adult" type='text' class="form-control" />
                                  </div>
                              </div>
                              <div class="form-group">
                                  <div class="col-md-2">
                                      <label>Concession Price: </label>
                                  </div>
                                  <div class="col-md-4">
                                      <input :readonly="selected_rate != ''" name="concession"  v-model="bulkpricing.concession" type='text' class="form-control" />
                                  </div>
                              </div>
                              <div class="form-group">
                                  <div class="col-md-2">
                                      <label>Child Price: </label>
                                  </div>
                                  <div class="col-md-4">
                                      <input :readonly="selected_rate != ''" name="child"  v-model="bulkpricing.child" type='text' class="form-control" />
                                  </div>
                              </div>
                              <div class="form-group">
                                  <div class="col-md-2">
                                      <label>Period start: </label>
                                  </div>
                                  <div class="col-md-4">
                                      <div class='input-group date'>
                                          <input  name="period_start"  v-model="bulkpricing.period_start" type='text' class="form-control" />
                                          <span class="input-group-addon">
                                              <span class="glyphicon glyphicon-calendar"></span>
                                          </span>
                                      </div>
                                  </div>
                              </div>
                              <reason type="price" v-model="bulkpricing.reason" style="margin:0px 0px;"></reason>
                              <div v-show="requireDetails">
                                  <div class="form-group">
                                      <div class="col-md-2">
                                          <label>Details: </label>
                                      </div>
                                      <div class="col-md-5">
                                          <textarea name="details" v-model="bulkpricing.details" class="form-control"></textarea>
                                      </div>
                                  </div>
                              </div>
                              <div class="btn-group btn-group-sm">
                                  <button type="button" class="btn btn-primary" style="margin-right:10px;" @click.prevent="sendData()">Save</button>
                                  <button type="button" class="btn btn-default" @click="goBack()" >Cancel</button>
                              </div>
                        </div>
                      </div>
                    </form>
                  </div>
        </div>
    </div>
    </div>
</template>

<script>
import {
    $,
    api_endpoints,
    helpers,
    select2
}
from '../../hooks.js'
import alert from '../utils/alert.vue'
import reason from '../utils/reasons.vue'

export default {
    name:"bulkpricing",
    data: function() {
        let vm = this;
        return {
            priceOptions:['Price Tariff','Park/Campground','Campsite Type'],
            setPrice:'',
            id:'',
            selected_rate: '',
            title: '',
            rates: [],
            current_closure: '',
            closeStartPicker: '',
            showDetails: false,
            closeEndPicker: '',
            errors: false,
            errorString: '',
            form: '',
            bulkpricing: {
                reason: '',
                campgrounds:[]
            },
            parks: [],
            selectedPark: {},
            campgrounds: [],
            campsiteTypes:[],
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        isModalOpen: function() {
            return this.isOpen;
        },
        closure_id: function() {
            return this.bulkpricing.id ? this.bulkpricing.id : '';
        },
        requireDetails: function() {
            return this.bulkpricing.reason == '1';
        },
    },
    watch: {
        selected_rate: function() {
            let vm = this;
            if (vm.selected_rate != ''){
                $.each(vm.rates, function(i, rate) {
                    if (rate.id== vm.selected_rate){
                        vm.bulkpricing.rate = rate.id;
                        vm.bulkpricing.adult = rate.adult;
                        vm.bulkpricing.concession = rate.concession;
                        vm.bulkpricing.child = rate.child;
                    }
                });
            }
            else{
                delete vm.bulkpricing.rate;
                vm.bulkpricing.adult = '';
                vm.bulkpricing.concession = '';
                vm.bulkpricing.child = '';
            }
        }
    },
    components: {
        alert,
        reason
    },
    methods: {
        close: function() {
            delete this.bulkpricing.original;
            this.errors = false;
            this.selected_rate = '';
            this.bulkpricing.period_start= '';
            this.bulkpricing.details= '';

            this.errorString = '';
            this.isOpen = false;
        },
        selectPark: function() {
            var vm = this;
            var park = vm.bulkpricing.park;
            vm.campgrounds = [];
            $.each(vm.parks, function(i, el) {
                if (el.url == park) {
                    $.each(el.campgrounds,function(k,c){
                        c.price_level == 0 ? vm.campgrounds.push(c):null;
                    })

                    setTimeout(function (e) {
                        $(vm.form.campground).select2({
                            "theme": "bootstrap"
                        }).
                        on("select2:select",function (e) {
                            var selected = $(e.currentTarget);
                            vm.bulkpricing.campgrounds = selected.val();
                        }).
                        on("select2:unselect",function (e) {
                            var selected = $(e.currentTarget);

                            vm.bulkpricing.campgrounds = selected.val();
                        });
                    },100);
                };
            });

        },
        selectCampsiteType:function () {
            var vm = this;

        },
        loadParks: function() {
            var vm = this;
            var url = api_endpoints.parks;
            $.ajax({
                url: url,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    $.each(data,function(i,el){
                        el.url = "//"+ el.url.split('://')[1];

                    });
                    vm.parks = data;
                    setTimeout(function (e) {

                        $(vm.form.park).select2({
                            "theme": "bootstrap"
                        }).
                        on("select2:select",function (e) {
                            console.log('here');
                            var selected = $(e.currentTarget);
                            vm.bulkpricing.park = selected.val();
                            vm.selectPark();
                        });
                    },100);

                }
            });

        },
        addHistory: function() {
            if ($(this.form).valid()){
                if (this.bulkpricing.id || this.bulkpricing.original){
                    this.$emit('updatePriceHistory');
                }else {
                    this.$emit('addPriceHistory');
                }
            }
        },
        fetchRates: function() {
            let vm = this;
            $.get(api_endpoints.rates,function(data){
                vm.rates = data;
            });
        },
        fetchCampsiteTypes: function() {
            let vm = this;
            $.get(api_endpoints.campsite_classes,function(data){
                vm.campsiteTypes = [];
                $.each(data,function(i,el){
                    el.can_add_rate ? vm.campsiteTypes.push(el): '';
                });

            });
        },
        goBack:function () {
            helpers.goBack(this);
        },
        addFormValidations: function() {
            let vm = this;
            $(vm.form).validate({
                rules: {
                    adult: "required",
                    concession: "required",
                    child: "required",
                    period_start: "required",
                    details: {
                        required: {
                            depends: function(el){
                                return vm.bulkpricing.reason=== '1';
                            }
                        }
                    }
                },
                messages: {
                    adult: "Enter an adult rate",
                    concession: "Enter a concession rate",
                    child: "Enter a child rate",
                    period_start: "Enter a start date",
                    details: "Details required if Other reason is selected"
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
    mounted: function() {
        var vm = this;
        $('[data-toggle="tooltip"]').tooltip()
        vm.loadParks();
        vm.setPrice = vm.priceOptions[1];
        vm.form = document.forms.bulkpricingForm;
        var picker = $(vm.form.period_start).closest('.date');
        var today = new Date();
        today.setDate(today.getDate()+1);
        var tomorrow = new Date(today);
        picker.datetimepicker({
            format: 'DD/MM/YYYY',
            useCurrent: false,
            minDate: tomorrow
        });
        picker.on('dp.change', function(e){
            vm.bulkpricing.period_start = picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.addFormValidations();
        vm.fetchRates();
        vm.fetchCampsiteTypes();
        //select2.defaults.set( "theme", "bootstrap" );
    }
};
</script>

<style lang="css" scoped>
    .editor{
        height: 200px;
    }
    .well:last-child{
        margin-bottom: 5px;
    }
    .helper {
        padding: 0px 12px;
        background-color: transparent;
        border: none;
    }
    .helper > i{
        padding: 6px;
        margin-left: -15px;
        margin-top: 4px;
    }
</style>
