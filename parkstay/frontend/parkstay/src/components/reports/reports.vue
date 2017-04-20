<template lang="html">
    <div id="report-form">
        <div class="well">
            <div class="row">
                <div class="col-md-12">
                    <h3 style="margin-bottom:20px;">Payments Reports</h3>
                    <form method="get" id="payments-form" action="/ledger/payments/api/report">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                  <label for="">Region</label>
                                  <select class="form-control" name="region" v-model="region">
                                      <option v-for="r in regions" :value="r.code">{{r.name}}</option>
                                  </select>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                  <label for="">Start Date</label>
                                  <div class="input-group date"  id="accountsDateStartPicker">
                                      <input type="text" class="form-control" name="start" placeholder="YYYY-MM-DD" required >
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
                                      <input type="text" class="form-control" name="end"  placeholder="YYYY-MM-DD" required>
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
                                      <input type="text" class="form-control" name="banked_start"  placeholder="YYYY-MM-DD" required>
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
                                      <input type="text" class="form-control" name="banked_end"  placeholder="YYYY-MM-DD" required>
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
                    </form>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import {$,bus,datetimepicker,api_endpoints,helpers,Moment,formValidate} from "../../hooks.js"
export default {
    name:"reports",
    data:function () {
        let vm = this;
        return {
            accountsDateStartPicker:null,
            accountsDateEndPicker:null,
            flatDateStartPicker:null,
            flatDateEndPicker:null,
            datepickerOptions:{
                format: 'YYYY-MM-DD',
                showClear:true,
                useCurrent:false
            },
            regions:[],
            region:'swan'
        };
    },
    methods:{
        addEventListeners:function () {
            let vm = this;
            vm.accountsDateStartPicker = $('#accountsDateStartPicker').datetimepicker(vm.datepickerOptions);
            vm.accountsDateEndPicker = $('#accountsDateEndPicker').datetimepicker(vm.datepickerOptions);
            vm.flatDateStartPicker = $('#flatDateStartPicker').datetimepicker(vm.datepickerOptions);
            vm.flatDateEndPicker = $('#flatDateEndPicker').datetimepicker(vm.datepickerOptions);

            vm.flatDateStartPicker.on('dp.hide',function (e) {
                vm.flatDateEndPicker.data("DateTimePicker").date(null);
                vm.flatDateEndPicker.data("DateTimePicker").minDate(e.date);
            });
            vm.accountsDateStartPicker.on('dp.hide',function (e) {
                vm.accountsDateEndPicker.data("DateTimePicker").date(null);
                vm.accountsDateEndPicker.data("DateTimePicker").minDate(e.date);
            });
            vm.fetchRegions();
        },
        fetchRegions:function () {
            let vm = this;
            $.get('/ledger/payments/api/regions?format=json',function (data) {
                vm.regions = data;
            });
        },
        generateFlatReport:function () {
            let vm = this;
            var form = $('#payments-form');
            if (formValidate.validate(form).isValid) {
                var values = {
                    "system":"S019",
                    "start":vm.accountsDateStartPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "end":vm.accountsDateEndPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "banked_start":vm.flatDateStartPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "banked_end":vm.flatDateEndPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "flat":false,
                    "region":vm.region
                };
                vm.getReport(values);
            }
        },
        generateByAccount:function () {
            let vm = this;
            var form = $('#payments-form');
            if (formValidate.validate(form).isValid) {
                var values = {
                    "system":"S019",
                    "start":vm.accountsDateStartPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "end":vm.accountsDateEndPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "banked_start":vm.flatDateStartPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "banked_end":vm.flatDateEndPicker.data("DateTimePicker").date().set({hour:0,minute:0,second:0,millisecond:0}).format('YYYY-MM-DD H:mm:ss'),
                    "items":true,
                    "region":vm.region
                };
                vm.getReport(values);
            }
        },
        getReport:function (values) {
            let vm = this;
            var url = "/ledger/payments/api/report?"+$.param(values);
            window.location.assign(url);
        }
    },
    mounted:function () {
        let vm = this;
        vm.addEventListeners();
    }
}

</script>

<style lang="css">
</style>
