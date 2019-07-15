<template lang="html">
    <div id="bulk-period">
        <modal okText="Set Periods" @ok="setPeriods()" :force="true">
            <h4 slot="title">Bulk Booking Periods</h4>
            <div class="modal-body">
                <form name="periodForm" class="form-horizontal" style="overflow:visible;">
                    <div class="row" v-if="showErrorPeriods">
                        <div class="danger-message">&nbsp;{{errorStringPeriods}}</div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-2">
                                <label for="Moorings">Moorings</label>
                            </div>
                            <div class="col-md-10">
                                <select name="campgrounds" id="bp-campgrounds" v-model="selected_campgrounds" class="form-control" multiple>
                                    <option v-for="c in campgrounds" :value="c.id">{{ c.name }}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-2">
                                <label>Booking Period:</label>
                            </div>
                            <div class="col-md-10">
                                <select name="period" id="bp-periods" v-model="selected_period" class="form-control">
                                    <option v-for="per in booking_periods" :value="per.id"> {{ per.name }}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-2">
                                <label for="set_period_range_start">Period start: </label>
                            </div>
                            <div class="col-md-4">
                                <div class='input-group date' :id='set_period_range_start'>
                                    <input  name="period_start"  v-model="range_start" type='text' class="form-control" />
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-2">
                                <label for="set_period_range_end">Period End: </label>
                            </div>
                            <div class="col-md-4">
                                <div class='input-group date' :id='set_period_range_end'>
                                    <input name="period_end" v-model="range_end" type='text' class="form-control" />
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <reason type="price" v-model="reason" :wide="true" :wide="true"></reason>
                    <div vshow-dis="requireDetails" class="row">
                        <div class="form-group">
                            <div class="col-md-2">
                                <label>Details: </label>
                            </div>
                            <div class="col-md-10">
                                <textarea name="period_details" v-model="details" class="form-control" id="period_details"></textarea>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </modal>
    </div>
</template>

<script>
import alert from '../alert.vue'
import modal from '../bootstrap-modal.vue'
import reason from '../reasons.vue'
import { mapGetters } from 'vuex'
import { $, datetimepicker,api_endpoints, validate, helpers, bus } from '../../../hooks'

export default {
    name:"bulk-period",
    data:function () {
        let vm =this;
        return {
            isModalOpen:false,
            periodEndPicker:null,
            periodStartPicker:null,
            reason:'',
            reasons: [],
            priceHistory: "",
            range_start:'',
            range_end:'',
            errorStringPeriods: null,
            set_period_range_end:'set_period_range_end'+vm._uid,
            set_period_range_start:'set_period_range_start'+vm._uid,
            selected_campgrounds:[],
            selected_period: [],
            form: null
        }
    },
    computed:{
        showErrorPeriods: function() {
            var vm = this;
            return vm.errorStringPeriods != null;
        },
        requireDetails:function () {
            let vm = this;
            var check = this.reason
            for (var i = 0; i < vm.reasons.length; i++){
                if (vm.reasons[i].id == check){
                    return vm.reasons[i].detailRequired;
                }
            }
        },
        ...mapGetters([
          'campgrounds',
          'booking_periods'
        ]),
    },
    components:{
        modal,
        alert,
        reason
    },
    methods:{
        close:function () {
            this.isModalOpen = this.$parent.showBulkBookingPeriod  = false;
            this.$parent.$refs.dtGrounds.vmDataTable.ajax.reload();
            this.range_start = "";
            this.range_start_time = "";
            this.range_end = "";
            this.range_end_time = "";
            this.campgrounds = "";
            this.booking_periods = "";
            this.reason = "";
            this.errorStringPeriods = null;
			this.periodStartPicker.data('DateTimePicker').date(new Date());
			this.periodEndPicker.data('DateTimePicker').clear();
        },
        events:function () {
            let vm = this;
            vm.periodEndPicker = $('#'+vm.set_period_range_end);
            vm.periodStartPicker = $('#'+vm.set_period_range_start).datetimepicker({
                format: 'DD/MM/YYYY',
                minDate: new Date()
            });
            vm.periodEndPicker.datetimepicker({
                format: 'DD/MM/YYYY',
                useCurrent: false
            });
            vm.periodStartPicker.on('dp.change', function(e){
                vm.range_start = vm.periodStartPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
                vm.periodEndPicker.data("DateTimePicker").minDate(e.date);
            });
            vm.periodEndPicker.on('dp.change', function(e){
                var date = vm.periodEndPicker.data('DateTimePicker').date();
                vm.range_end = (date) ? date.format('DD/MM/YYYY') : null;
            });
            vm.addFormValidations();
            vm.fetchCampgrounds();
            vm.fetchPeriods();
            vm.initSelectTwo();
        },
        fetchCampgrounds: function() {
            let vm = this;
            if (vm.campgrounds.length == 0) {
                vm.$store.dispatch("fetchCampgrounds");
            }
        },
        fetchPeriods: function() {
            let vm = this;
            if (vm.booking_periods.length == 0){
                vm.$store.dispatch("fetchBookingPeriods");
            }
        },
        initSelectTwo:function () {
            let vm = this;
            setTimeout(function () {
                $('#bp-campgrounds').select2({
                    theme: 'bootstrap',
                    allowClear: true,
                    placeholder: "Select Moorings",
                    tags:false,
                }).
                on("select2:select",function (e) {
                    vm.selected_campgrounds = $(e.currentTarget).val();
                }).
                on("select2:unselect",function (e) {
                    vm.selected_campgrounds = $(e.currentTarget).val();
                });
                $('#bp-periods').select2({
                    theme: 'bootstrap',
                    allowClear: true,
                    placeholder: "Select Booking Periods",
                    tags: false,
                }).
                on("select2:select", function (e){
                    vm.selected_period = $(e.currentTarget).val();
                }).
                on("select2:unselect", function (e) {
                    vm.selected_period = "";
                });
            },100);
        },
        setPeriods:function () {
            let vm =this;
            if (vm.requireDetails && (vm.details == "" || vm.details == " " || !vm.details)){
                $('#period_details')
                    .tooltip({
                        trigger: "focus"
                    })
                    .attr("data-original-title", "Detail required for this reason.")
                    .parents('.form-group').addClass('has-error');
            } else {
                if (vm.form.valid() && vm.selected_campgrounds.length>0 && vm.selected_period.length > 0){
                    let data = {
                        period_start: vm.range_start,
                        period_end: vm.range_end,
                        moorings: vm.selected_campgrounds,
                        booking_period: vm.selected_period,
                        reason: vm.reason,
                        details: vm.details
                    }
                    $.ajax({
                        url:api_endpoints.bulk_period,
                        method: 'POST',
                        xhrFields: { withCredentials:true },
                        data: data,
                        headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                        dataType: 'json',
                        success: function(data, stat, xhr) {
                            vm.$store.dispatch("updateAlert",{
                                visible:true,
                                type:"success",
                                message: data
                        });
                        vm.close();
                        },
                        error:function (resp){
                            if (resp.responseText.includes("Dates overlap existing periods")){
                                var split = resp.responseText.split('\n');
                                vm.errorStringPeriods = split[1];
                            } else {
                                vm.$store.dispatch("updateAlert",{
                                    visible:true,
                                    type:"danger",
                                    message: helpers.apiError(resp)
                                });
                                vm.close();  
                            }
                        }
                    });
                }
            }
        },
        addFormValidations: function() {
            let vm = this;
            vm.form.validate({
                rules: {
                    campgrounds: "required",
                    period: "required",
                    period_start: "required",
                    period_end: "required",
                    open_reason: "required",
                    period_details:{
                        required: {
                            depends: function(el){
                                var check = this.reason;
                                for (var i = 0; i < vm.reasons.length; i++){
                                    if (vm.reasons[i].id == check){
                                        return vm.reasons[i].detailRequired;
                                    }
                                }
                            }
                        }
                    }
                },
                messages: {
                    campgrounds: "Select at least 1 mooring",
                    period: "Select a period",
                    period_start: "Enter a start date",
                    period_end: "Enter an end date",
                    open_reason: "Select a reason",
                    period_details: "This reason requires more details"
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
        let vm = this;
        vm.form = $(document.forms.periodForm);
        vm.events();
        bus.$once('priceReasons',setReasons => {
            vm.reasons = setReasons;
        });
    }
}

</script>

<style lang="css">
.body{
    padding:0 20px;
}
.danger-message{
    z-index: 999999;
    background-color: #F2DEDE;
    color: #A94442;
    border-style: solid;
    border-width: 1px;
    border-color: #A94442;
    border-radius: 5px;
    padding: 8px;
    margin-bottom: 10px;
}
</style>
