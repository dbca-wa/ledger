<template lang="html" >
    <div id="bulkpricing">
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
                  <loader :isLoading="isLoading" >{{loading.join(' , ')}}</loader>
                <div class="panel-body" v-show="!isLoading">
                          <alert :show="showError" :duration="7000" type="danger">{{errorString}}</alert>
                          <alert :show="showSuccess" :duration="7000" type="success"><strong>Bulk pricing was successfull </strong></alert>
                          <div class="well well-sm">
                              <div class="row">
                                  <div class="col-lg-12">
                                      <div class="col-md-3">
                                          <div class="radio">
                                            <label for="">Set price per : </label>
                                          </div>
                                      </div>
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
                                    <h3>Add New Pricing Period For {{setPrice}}</h3><br/>
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
                                                  <option v-for="park in parks" :value="park.id">{{ park.name }}</option>
                                              </select>
                                          </div>
                                          <div class="col-md-4" v-show="setPrice == priceOptions[2]">
                                              <select name="tmpCampsiteType" v-show="!campsiteTypes.length > 0" class="form-control" >
                                                  <option >Loading...</option>
                                              </select>
                                              <select name="campsiteType" v-if="campsiteTypes.length > 0" @change="selectCampsiteType" class="form-control" v-model="bulkpricing.campsiteType">
                                                  <option v-for="ct  in campsiteTypes" :value="ct.id">{{ ct.name }}</option>
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
                                              <label><i class="fa fa-question-circle" data-toggle="tooltip" data-placement="bottom" title="Select a rate to prefill the price fields otherwise use the manual entry">&nbsp;</i>Select Rate: </label>

                                          </div>
                                          <div class="col-sm-4">
                                              <select name="rate" v-model="selected_rate" class="form-control" title="testing">
                                                  <option value="">Manual Entry</option>
                                                  <option v-for="r in rates":value="r.id">{{r.name}}</option>
                                              </select>
                                          </div>
                                      </div>
                                      <div class="form-group">
                                          <div class="col-md-2">
                                              <label>Adult Price: </label>
                                          </div>
                                          <div class="col-md-4">
                                              <input :readonly="selected_rate != ''" name="adult"  v-model="bulkpricing.adult" type='text' class="form-control" required="true" />
                                          </div>
                                      </div>
                                      <div class="form-group">
                                          <div class="col-md-2">
                                              <label>Concession Price: </label>
                                          </div>
                                          <div class="col-md-4">
                                              <input :readonly="selected_rate != ''" name="concession"  v-model="bulkpricing.concession" type='text' class="form-control" required="true" />
                                          </div>
                                      </div>
                                      <div class="form-group">
                                          <div class="col-md-2">
                                              <label>Child Price: </label>
                                          </div>
                                          <div class="col-md-4">
                                              <input :readonly="selected_rate != ''" name="child"  v-model="bulkpricing.child" type='text' class="form-control" required="true"/>
                                          </div>
                                      </div>
                                      <div class="form-group">
                                          <div class="col-md-2">
                                              <label>Period start: </label>
                                          </div>
                                          <div class="col-md-4">
                                              <div class='input-group date'>
                                                  <input  name="period_start"  v-model="bulkpricing.period_start" type='text' class="form-control" required="true" />
                                                  <span class="input-group-addon">
                                                      <span class="glyphicon glyphicon-calendar"></span>
                                                  </span>
                                              </div>
                                          </div>
                                      </div>
                                      <reason type="price" v-model="bulkpricing.reason" style="margin:0px 0px;" required="true"></reason>
                                      <div v-show="requireDetails">
                                          <div class="form-group">
                                              <div class="col-md-2">
                                                  <label>Details: </label>
                                              </div>
                                              <div class="col-md-5">
                                                  <textarea name="details" v-model="bulkpricing.details" class="form-control" :required="requireDetails"></textarea>
                                              </div>
                                          </div>
                                      </div>
                                      <div class="btn-group btn-group-sm">
                                          <button type="button" class="btn btn-primary" style="margin-right:10px;" @click.prevent="sendData()">Save</button>
                                          <button type="button" class="btn btn-default" @click="goBack()" >Cancel</button>
                                      </div>
                                    </form>
                                </div>
                              </div>
                          </div>
                </div>
            </div>
        </div>
        <div class="panel panel-default">
            <div class="panel-heading" role="tab" id="parkentry-heading">
                <h4 class="panel-title">
                    <a role="button" data-toggle="collapse" href="#parkentry-collapse"
                       aria-expanded="false" aria-controls="parkentry-collapse">
                        <h3>Park Entry</h3>
                    </a>
                </h4>
            </div>
            <div id="parkentry-collapse" class="panel-collapse collapse in" role="tabpanel"
                 aria-labelledby="parkentry-heading">
              <div class="panel-body" >
                  <div class="col-lg-12">
                      <price-history  :addParkPrice="true" :dt_options="priceHistoryDt" :dt_headers="priceHistoryDtHeaders" :object_id="34" level='park' ></price-history>
                  </div>
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
    select2,
    Moment
}
from '../../hooks.js'
import alert from '../utils/alert.vue'
import reason from '../utils/reasons.vue'
import loader from '../utils/loader.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
import { mapGetters } from 'vuex'
export default {
    name:"bulkpricing",
    data: function() {
        let vm = this;
        return {
            priceOptions:['Price Tariff','Park','Campsite Type'],
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
            loading: [],
            form: '',
            bulkpricing: {
                reason: '',
                campgrounds:[]
            },
            campgrounds:[],
            selectedPark: {},
            campsiteTypes:[],
            showSuccess:false,
            priceHistoryDt:{
                responsive: true,
                processing: true,
                ordering:false,
                deferRender: true,
                ajax: {
                    url: api_endpoints.park_price_history(),
                    dataSrc: ''
                },
                columns: [{
                    data: 'period_start',
                    mRender: function(data, type, full) {
                        return Moment(data).format('DD/MM/YYYY');
                    }

                }, {
                    data: 'period_end',
                    mRender: function(data, type, full) {
                        if (data) {
                            return Moment(data).format('DD/MM/YYYY');
                        }
                        else {
                            return '';
                        }
                    }

                }, {
                    data: 'vehicle'
                }, {
                    data: 'concession'
                }, {
                    data: 'motorbike'
                }, {
                    data: 'reason',
                    mRender: function(data, type, full) {
                        if (data.id == 1){
                            return data.text +":"+ full.details;
                        }else{
                            return data.text
                        }
                    }
                }, {
                    data: 'editable',
                    mRender: function(data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editPrice' data-rate=\"__RATE__\" >Edit</a><br/>"
                            column += "<a href='#' class='deletePrice' data-rate=\"__RATE__\" >Delete</a></td>";
                            column = column.replace(/__RATE__/g, id);
                            return column;
                        }
                        else {
                            return "";
                        }
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            priceHistoryDtHeaders:[
                "Period Start","Period End", "Vehicle","Concession","Motorbike","Comment","Action"
            ]

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
        isLoading: function(){
            let vm = this;
            if ( vm.loading.length > 0){
                return true;
            }
            else{
                setTimeout(function (e) {
                    $(vm.form.park).select2({
                        "theme": "bootstrap",
                        allowClear: true,
                        placeholder:"Select Park"
                    }).
                    on("select2:select",function (e) {
                        var selected = $(e.currentTarget);
                        vm.bulkpricing.park = selected.val();
                        vm.selectPark();
                    }).
                    on("select2:unselect",function (e) {
                        var selected = $(e.currentTarget);
                        vm.bulkpricing.park = "";
                    });
                },100);
            }
        },
        ...mapGetters([
          'parks',
          'campsite_classes'
        ]),
    },
    watch: {
        setPrice: function(){
            let vm = this;
            if (vm.setPrice == vm.priceOptions[2]){
                setTimeout(function(){
                    $(vm.form.campsiteType).select2({
                        theme: 'bootstrap',
                        allowClear: true,
                        placeholder: "Select Campsite Type",
                    }).
                    on("select2:select",function (e) {
                        var selected = $(e.currentTarget);
                        vm.bulkpricing.campsiteType = selected.val();
                    }).
                    on("select2:unselect",function (e) {
                        var selected = $(e.currentTarget);

                        vm.bulkpricing.campsiteType = selected.val();
                    });
                },100);
            }
        },
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
        },
        campsite_classes:function () {
            let vm =this;
            vm.availableCampsiteClasses();
        }
    },
    components: {
        alert,
        reason,
        loader,
        'price-history':priceHistory
    },
    methods: {
        availableCampsiteClasses:function () {
            let vm =this;
            vm.loading.push('Loading CampsiteTypes');
            vm.campsiteTypes = [];
            $.each(vm.campsite_classes,function(i,el){
                el.can_add_rate ? vm.campsiteTypes.push(el): '';
            });
            if (vm.campsiteTypes.length == 0) {
                vm.campsiteTypes.push({
                    id:"",
                    name:""
                });
            }
            vm.loading.splice('Loading CampsiteTypes',1);
        },
        sendData: function(){
            let vm = this;
            if($(vm.form).valid()){
                vm.loading.push('Updating prices...');
                var data = JSON.parse(JSON.stringify(vm.bulkpricing));
                var url = api_endpoints.bulkPricing();
                data.type = vm.setPrice;
                $.ajax({
                     beforeSend: function(xhrObj) {
                        xhrObj.setRequestHeader("Content-Type", "application/json");
                        xhrObj.setRequestHeader("Accept", "application/json");
                    },
                    method: "POST",
                    url: url,
                    xhrFields: { withCredentials:true },
                    data: JSON.stringify(data),
                    headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                    success: function(msg){
                        setTimeout(function () {
                            vm.loading.splice('Updating prices...',1);
                            vm.bulkpricing = {
                                reason: '',
                                campgrounds:[]
                            };
                            vm.showSuccess = true;
                        },500);
                    },
                    error: function(resp){
                        vm.loading.splice('Updating prices...',1);
                        vm.errors = true;
                        vm.errorString = resp;
                    }
                });
            }else{
                vm.errors = true;
                vm.errorString = "Please fill all details";
            }
        },
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
                if (el.id == park) {
                    $.each(el.campgrounds,function(k,c){
                        c.price_level == 0 ? vm.campgrounds.push(c):null;
                    })

                    setTimeout(function (e) {
                        $(vm.form.campground).select2({
                            "theme": "bootstrap",
                            allowClear: true,
                            placeholder: {
                              text:"Select Campground",
                              selected:'selected'
                            }
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
            vm.loading.push('Loading Parks');
            if (vm.parks.length == 0) {
                vm.$store.dispatch("fetchParks");
            }
            vm.loading.splice('Loading Parks',1);

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
            vm.loading.push('Loading Rates');
            $.get(api_endpoints.rates,function(data){
                vm.rates = data;
                vm.loading.splice('Loading Rates',1);
            });
        },
        fetchCampsiteTypes: function() {
            let vm = this;
            if (vm.campsite_classes.length == 0) {
                vm.$store.dispatch("fetchCampsiteClasses");
            }else{
                vm.availableCampsiteClasses();
            }
        },
        goBack:function () {
            helpers.goBack(this);
        },
        addFormValidations: function() {
            let vm = this;
            $(vm.form).validate({
                rules: {
                    park:{
                        required: {
                            depends: function(el){
                                return vm.setPrice == vm.priceOptions[1];
                            }
                        }
                    },
                    campground:{
                        required: {
                            depends: function(el){
                                return vm.setPrice == vm.priceOptions[1];
                            }
                        }
                    },
                    campsiteType:{
                        required: {
                            depends: function(el){
                                return vm.setPrice == vm.priceOptions[2];
                            }
                        }
                    },
                    adult: "required",
                    concession: "required",
                    child: "required",
                    period_start: "required",
                    open_reason: "required",
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
        $("i.fa").tooltip();
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
</style>
