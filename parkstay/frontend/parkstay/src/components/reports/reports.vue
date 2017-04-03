<template lang="html">
    <div id="report-form">
        <div class="well">
            <div class="row">
                <div class="col-md-12">
                    <h3 style="margin-bottom:20px;">Payments Reports</h3>
                    <form method="get" id="payments-form" action="/ledger/payments/api/report">
                        <input type="hidden" name="system" value="S019">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                  <label for="">Start Date</label>
                                  <div class="input-group date"  id="accountsDateStartPicker">
                                      <input type="text" class="form-control" name="start" placeholder="YYYY-MM-DD H:m:s" required >
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
                                      <input type="text" class="form-control" name="end"  placeholder="YYYY-MM-DD H:m:s" required>
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
                                      <input type="text" class="form-control" name="banked_start"  placeholder="YYYY-MM-DD H:m:s" required>
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
                                      <input type="text" class="form-control" name="banked_end"  placeholder="YYYY-MM-DD H:m:s" required>
                                      <span class="input-group-addon">
                                          <span class="glyphicon glyphicon-calendar"></span>
                                      </span>
                                  </div>
                                </div>
                            </div>

                        </div>
                        <div class="row">
                            <div class="col-sm-6">
                                <button type=submit class="btn btn-primary pull-left" name="items" value="true">Generate Report By Accounts</button>
                            </div>
                            <div class="col-sm-6 clearfix">
                              <button type=submit class="btn btn-primary pull-left" name="flat" value="false">Generate Report Flat</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import {$,bus,datetimepicker,api_endpoints,helpers,Moment} from "../../hooks.js"
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
                format: 'YYYY-MM-DD H:mm:ss',
                showClear:true,
                useCurrent:false
            }
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
