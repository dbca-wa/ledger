<template lang="html">
  <div class="container">
    <div id="report-form">
        <form method="get" id="payments-form" action="/ledger/payments/api/report-allocated">
            <div class="well well-sm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="col-lg-12">
                            <h3 style="margin-bottom:20px;">Select Region</h3>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                      <label for="">Region</label>
                                      <select class="form-control" name="region" v-model="region">
                                          <option value="">Kensington</option>
                                          <option v-for="r in regions" :value="r.code">{{r.name}}</option>
                                      </select>
                                    </div>
                                </div>
                                <div class="col-md-6" v-show="region">
                                    <div class="form-group">
                                      <label for="">District</label>
                                      <select class="form-control" name="region" v-model="district">
                                          <option value="">All</option>
                                          <option v-for="d in selected_region.districts" :value="d.code">{{d.name}}</option>
                                      </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="well">
                <div class="row">
                    <div class="col-md-12">
                        <h3 style="margin-bottom:20px;">Payments Reports</h3>
                            <div class="row" v-show="!region">
                                <div class="col-md-6">
                                    <div class="form-group">
                                      <label for="">Start Date</label>
                                      <div class="input-group date"  id="accountsDateStartPicker">
                                          <input type="text" class="form-control" name="start" placeholder="DD/MM/YYYY" required >
                                          <span class="input-group-addon">
                                              <span class="glyphicon glyphicon-calendar"></span>
                                          </span>
                                      </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-group">
                                      <label for="">End Date</label>
                                      <div class="input-group date" id="accountsDateEndPicker">
                                          <input type="text" class="form-control" name="end"  placeholder="DD/MM/YYYY" required>
                                          <span class="input-group-addon">
                                              <span class="glyphicon glyphicon-calendar"></span>
                                          </span>
                                      </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row" style="margin-top:20px;">
                                <div class="col-md-6">
                                    <div class="form-group">
                                      <label for="">Bank Start Date</label>
                                      <div class="input-group date" id="flatDateStartPicker">
                                          <input type="text" class="form-control" name="banked_start"  placeholder="DD/MM/YYYY" required>
                                          <span class="input-group-addon">
                                              <span class="glyphicon glyphicon-calendar"></span>
                                          </span>
                                      </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-group">
                                      <label for="">Bank End Date</label>
                                      <div class="input-group date" id="flatDateEndPicker">
                                          <input type="text" class="form-control" name="banked_end"  placeholder="DD/MM/YYYY" required>
                                          <span class="input-group-addon">
                                              <span class="glyphicon glyphicon-calendar"></span>
                                          </span>
                                      </div>
                                    </div>
                                </div>

                            </div>
                            <div class="row">
                                <div class="col-sm-6">
                                    <button @click.prevent="generateByAccount()" class="btn btn-primary pull-left" >Generate Report By Accounts</button>
                                </div>
                                <div class="col-sm-6 clearfix">
                                  <button @click.prevent="generateFlatReport()" class="btn btn-primary pull-left" >Generate Report Flat</button>
                                </div>
                            </div>
                    </div>
                </div>
            </div>
        </form>
        <!--
        <form id="refund_form">
            <div class="well well-sm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="col-lg-12">
                            <h3 style="margin-bottom:20px;">Refunds Reports</h3>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                              <label for="">Start Date</label>
                              <div class="input-group date"  id="refundsStartPicker">
                                  <input type="text" class="form-control" name="refund_start_date" placeholder="DD/MM/YYYY">
                                  <span class="input-group-addon">
                                      <span class="glyphicon glyphicon-calendar"></span>
                                  </span>
                              </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                              <label for="">End Date</label>
                              <div class="input-group date" id="refundsEndPicker">
                                  <input type="text" class="form-control" name="refund_end_date"  placeholder="DD/MM/YYYY">
                                  <span class="input-group-addon">
                                      <span class="glyphicon glyphicon-calendar"></span>
                                  </span>
                              </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-lg-12">
                                <div class="col-sm-6">
                                    <button @click.prevent="generateRefundReport()" class="btn btn-primary pull-left" >Generate Refund Reports</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        -->
            <div class="well well-sm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="row">
                                    <div class="col-sm-6">
                                        <form ref="booking_settlements_form">
                                            <h3 style="margin-bottom:20px;">Settlement Report</h3>
                                            <div class="form-group">
                                              <label for="">Date</label>
                                              <div class="input-group date" ref="bookingSettlementsDatePicker">
                                                  <input type="text" class="form-control" name="booking_settlement_date"  placeholder="DD/MM/YYYY" required>
                                                  <span class="input-group-addon">
                                                      <span class="glyphicon glyphicon-calendar"></span>
                                                  </span>
                                              </div>
                                            </div>
                                            <div class="form-group">
                                                <button @click.prevent="getBookingSettlementsReport()" class="btn btn-primary pull-left" >Generate Settlement Report</button>
                                            </div>
                                        </form>
                                    </div>
                                    <!--
                                    <div class="col-sm-6">
                                        <form ref="bookings_form">
                                            <h3 style="margin-bottom:20px;">Bookings Report</h3>
                                            <div class="form-group">
                                              <label for="">Date</label>
                                              <div class="input-group date" ref="bookingsDatePicker">
                                                  <input type="text" class="form-control" name="bookings_date"  placeholder="DD/MM/YYYY" required>
                                                  <span class="input-group-addon">
                                                      <span class="glyphicon glyphicon-calendar"></span>
                                                  </span>
                                              </div>
                                            </div>
                                            <div class="form-group">
                                                <button @click.prevent="getBookingsReport()" class="btn btn-primary pull-left" >Generate Bookings Report</button>
                                            </div>
                                        </form>
                                    </div>
                                    -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        <form ref="oracle_form">
            <div class="well well-sm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="col-lg-12">
                            <h3 style="margin-bottom:20px;">Oracle Job</h3>
                        </div>
                        <div class="row">
                            <div class="col-lg-12">
                                <div class="col-sm-6">
                                    <div class="form-group">
                                      <label for="">Date</label>
                                      <div class="input-group date" ref="oracleDatePicker">
                                          <input type="text" class="form-control" name="oracle_date"  placeholder="DD/MM/YYYY" required>
                                          <span class="input-group-addon">
                                              <span class="glyphicon glyphicon-calendar"></span>
                                          </span>
                                      </div>
                                    </div>
                                    <div class="form-group">
                                        <button @click.prevent="runOracleJob()" class="btn btn-primary pull-left" >Run Job</button>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="checkbox">
                                      <label><input v-model="oracle_override" type="checkbox" value="">Override closed period check</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
  </div>
</template>

<script>
//import {$,swal,bus,datetimepicker,api_endpoints,helpers,Moment,validate} from "@/utils/hooks.js"
import {api_endpoints,helpers} from "@/utils/hooks.js"
export default {
    name:"reports",
    data:function () {
        let vm = this;
        return {
            form:null,
            refund_form:null,
            oracle_form: null,
            oracleDatePicker: null,
            booking_settlements_form: null,
            bookings_form: null,
            bookingSettlementsDatePicker: null,
            bookingsDatePicker: null,
            accountsDateStartPicker:null,
            accountsDateEndPicker:null,
            flatDateStartPicker:null,
            flatDateEndPicker:null,
            refundsStartPicker:null,
            refundsEndPicker:null,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false
            },
            regions:[],
            region:'',
            district:'',
            selected_region:{
                code:'',
                name:'',
                districts:[]
            },
            oracle_override: false,
        };
    },
    watch:{
        region: function () {
            let vm =this;
            vm.district = '';
            if (vm.region) {
                vm.selected_region = vm.regions.find(r => (r.code == vm.region));
            }else{
                vm.selected_region={
                    code:'',
                    name:'',
                    districts:[]
                }
            }
        }
    },
    methods:{
        addEventListeners:function () {
            let vm = this;
            vm.form = $('#payments-form');
            vm.refund_form = $('#refund_form');
            vm.oracle_form = $(vm.$refs.oracle_form);
            vm.booking_settlements_form = $(vm.$refs.booking_settlements_form);
            vm.bookings_form = $(vm.$refs.bookings_form);
            vm.accountsDateStartPicker = $('#accountsDateStartPicker').datetimepicker(vm.datepickerOptions);
            vm.accountsDateEndPicker = $('#accountsDateEndPicker').datetimepicker(vm.datepickerOptions);
            vm.flatDateStartPicker = $('#flatDateStartPicker').datetimepicker(vm.datepickerOptions);
            vm.flatDateEndPicker = $('#flatDateEndPicker').datetimepicker(vm.datepickerOptions);
            vm.refundsStartPicker = $('#refundsStartPicker').datetimepicker(vm.datepickerOptions);
            vm.refundsEndPicker = $('#refundsEndPicker').datetimepicker(vm.datepickerOptions);
            vm.oracleDatePicker = $(vm.$refs.oracleDatePicker).datetimepicker(vm.datepickerOptions);
            vm.bookingSettlementsDatePicker = $(vm.$refs.bookingSettlementsDatePicker).datetimepicker(vm.datepickerOptions);
            vm.bookingsDatePicker = $(vm.$refs.bookingsDatePicker).datetimepicker(vm.datepickerOptions);

            vm.flatDateStartPicker.on('dp.hide',function (e) {
                vm.flatDateEndPicker.data("DateTimePicker").date(null);
                vm.flatDateEndPicker.data("DateTimePicker").minDate(e.date);
            });
            vm.accountsDateStartPicker.on('dp.hide',function (e) {
                vm.accountsDateEndPicker.data("DateTimePicker").date(null);
                vm.accountsDateEndPicker.data("DateTimePicker").minDate(e.date);
            });
            vm.refundsStartPicker.on('dp.hide',function (e) {
                vm.refundsEndPicker.data("DateTimePicker").date(null);
                vm.refundsEndPicker.data("DateTimePicker").minDate(e.date);
            });
            vm.addFormValidations();
            vm.fetchRegions();
        },
        runOracleJob(){
            let vm = this;
            
            if (vm.oracle_form.valid()){
                let data = vm.oracleDatePicker.data("DateTimePicker").date().format('DD/MM/YYYY');
                let override = vm.oracle_override ? 'true': 'false';
                vm.$http.get('/api/oracle_job?date='+data+'&override='+override).then((response) => {
                    swal({
                        type: 'success',
                        title: 'Job Success', 
                        text: 'The oracle job was completed successfully', 
                    })
                },(error) => {
                    swal({
                        type: 'error',
                        title: 'Oracle Job Error', 
                        text: helpers.apiVueResourceError(error), 
                    })
                })
            }
        },
        getBookingSettlementsReport(){
            let vm = this;

            if (vm.booking_settlements_form.valid()){
                let data = vm.bookingSettlementsDatePicker.data("DateTimePicker").date().format('DD/MM/YYYY');
                var url = '/api/reports/booking_settlements?date='+data; 
                window.location.assign(url);
                /*vm.$http.get(url).then((response) => {
                },(error) => {
                    swal({
                        type: 'error',
                        title: 'BPOINT Settlement Report Error', 
                        text: helpers.apiVueResourceError(error), 
                    })
                })*/
            }
        },
        getBookingsReport(){
            let vm = this;

            if (vm.bookings_form.valid()){
                let data = vm.bookingsDatePicker.data("DateTimePicker").date().format('DD/MM/YYYY');
                var url = '/api/reports/bookings?date='+data; 
                window.location.assign(url);
                /*vm.$http.get(url).then((response) => {
                },(error) => {
                    swal({
                        type: 'error',
                        title: 'BPOINT Settlement Report Error', 
                        text: helpers.apiVueResourceError(error), 
                    })
                })*/
            }
        },
        fetchRegions:function () {
            let vm = this;
            $.get('/ledger/payments/api/regions?format=json',function (data) {
                vm.regions = data;
            });
        },
        fetchRegions:function () {
            let vm = this;
            $.get('/ledger/payments/api/regions?format=json',function (data) {
                vm.regions = data;
            });
        },
        generateFlatReport:function () {
            let vm = this;
            var values = vm.generateValues();
            if (values) {
                values.flat = false;
                vm.getReport(values);
            }
        },
        generateValues:function () {
            let vm = this;
            if(vm.form.valid()){
                var values = {
                    "system":"S516",
                    "start":(vm.region) ? vm.flatDateStartPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'):vm.accountsDateStartPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "end":(vm.region) ? vm.flatDateEndPicker.data("DateTimePicker").date().set({hour:23,minute:59,second:59,millisecond:0}).format('YYYY-MM-DD H:mm:ss'):vm.accountsDateEndPicker.data("DateTimePicker").date().set({hour:23,minute:59,second:59,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "banked_start":vm.flatDateStartPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "banked_end":vm.flatDateEndPicker.data("DateTimePicker").date().set({hour:23,minute:59,second:59,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                };
                if(vm.region){
                    values.region = vm.region;
                    if (vm.district) {
                        values.district = vm.district;
                    }
                }
                return values;
            }
            return false;
        },
        generateByAccount:function () {
            let vm = this;
            var values = vm.generateValues();
            if (values) {
                values.items = true;
                vm.getReport(values);
            }

        },
        generateRefundReport:function () {
            let vm =this;

            if (vm.refund_form.valid()) {
                var values = {
                    "start": vm.refundsStartPicker.data("DateTimePicker").date().format('DD/MM/YYYY'),
                    "end" :vm.refundsEndPicker.data("DateTimePicker").date().format('DD/MM/YYYY'),
                }
                var url = api_endpoints.booking_refunds +"?"+ $.param(values);
                window.location.assign(url);
            }else{
                console.log("invalid form");
            }

        },
        getReport:function (values) {
            let vm = this;
            var url = "/ledger/payments/api/report-allocated?"+$.param(values);
            window.location.assign(url);
        },
        addFormValidations: function() {
            let vm =this;
            vm.form.validate({
                rules: {
                    start: {
                        required:function(){
                            return vm.region.length == 0;
                        }
                    },
                    end: {
                        required:function(){
                            return vm.region.length == 0;
                        }
                    },
                    banked_start: "required",
                    banked_end: "required",
                },
                messages: {
                    start: "Field is required",
                    end: "Field is required",
                    banked_end: "Field is required",
                    banked_start: "Field is required",
                },
                showErrors:function(errorMap, errorList) {
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
            vm.refund_form.validate({
                rules: {
                    refund_start_date: {
                        required:function(){
                            return vm.region.length == 0;
                        }
                    },
                    refund_end_date: {
                        required:function(){
                            return vm.region.length == 0;
                        }
                    }
                },
                messages: {
                    refund_start_date: "Field is required",
                    refund_end_date: "Field is required",
                },
                showErrors:function(errorMap, errorList) {
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
            vm.oracle_form.validate({
                rules: {
                    oracle_date:'required', 
                },
                messages: {
                    oracle_date: "Field is required",
                },
                showErrors:function(errorMap, errorList) {
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
            vm.booking_settlements_form.validate({
                rules: {
                    booking_settlement_date:'required', 
                },
                messages: {
                    booking_settlement_date: "Field is required",
                },
                showErrors:function(errorMap, errorList) {
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
            vm.bookings_form.validate({
                rules: {
                    bookings_date:'required', 
                },
                messages: {
                    bookings_date: "Field is required",
                },
                showErrors:function(errorMap, errorList) {
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
    },
    mounted:function () {
        let vm = this;
        vm.addEventListeners();
    }
}

</script>

<style lang="css">
</style>
