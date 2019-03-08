<template id="ParkPriceHistoryDetail">
<bootstrapModal title="Add Price History" :large=true @ok="addHistory()" @cancel="close()" @close="close()">

    <div class="modal-body" style="overflow:visible;">
        <form name="priceForm" class="form-horizontal" style="overflow:visible;">
			<alert :show.sync="showError" type="danger">{{errorString}}</alert>
            <div class="row" style="overflow:visible;">
                <div class="form-group" style="overflow:visible;">
                    <div class="col-md-2">
                        <label>Period start: </label>
                    </div>
                    <div class="col-md-4" style="overflow:visible;">
                        <div class="input-group date" >
                            <input type="text" id="period_start" class="form-control"  placeholder="DD/MM/YYYY" v-model="priceHistory.period_start">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                    <div class="col-md-2" style="display:none;">
                        <label>Period end: </label>
                    </div>
                    <div class="col-md-4" style="overflow:visible;display:none;">
                        <div class='input-group date'>
                            <input name="period_end" v-model="priceHistory.period_end" type='text' id="period_end" class="form-control" />
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
                        <label>Adult Cost Day: </label>
                    </div>
                    <div class="col-md-4">
                        <input name="adult_cost"  v-model="priceHistory.adult_cost" type='number' class="form-control" />
                    </div>
                    <div class="col-md-2">
                        <label>Adult Cost Overnight: </label>
                    </div>
                    <div class="col-md-4">
                        <input name="adult_overnight_cost"  v-model="priceHistory.adult_overnight_cost" type='number' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Child Cost Day: </label>
                    </div>
                    <div class="col-md-4">
                        <input name="child_cost"  v-model="priceHistory.children_cost" type='number' class="form-control" />
                    </div>
                    <div class="col-md-2">
                        <label>Child Cost Overnight: </label>
                    </div>
                    <div class="col-md-4">
                        <input name="child_overnight_cost"  v-model="priceHistory.children_overnight_cost" type='number' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Infant Cost Day: </label>
                    </div>
                    <div class="col-md-4">
                        <input name="infant_cost"  v-model="priceHistory.infant_cost" type='number' class="form-control" />
                    </div>
                    <div class="col-md-2">
                        <label>Infant Cost Overnight: </label>
                    </div>
                    <div class="col-md-4">
                        <input name="infant_overnight_cost"  v-model="priceHistory.infant_overnight_cost" type='number' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Family Cost Day: </label>
                    </div>
                    <div class="col-md-4">
                        <input name="family_cost"  v-model="priceHistory.family_cost" type='number' class="form-control" />
                    </div>
                    <div class="col-md-2">
                        <label>Family Cost Overnight: </label>
                    </div>
                    <div class="col-md-4">
                        <input name="family_overnight_cost"  v-model="priceHistory.family_overnight_cost" type='number' class="form-control" />
                    </div>
                </div>
            </div>

            <div class="row" id="div_mooring_groups">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Mooring Group: </label>
                    </div>
                    <div  class="col-md-4">
                        <select class="form-control" name="mooring_group" v-model="priceHistory.mooring_group">
                            <option value=""></option>
                            <option v-for="mg in mooring_groups" :value="mg.id">{{mg.name}}</option>
                        </select>
                    </div>
                </div>
            </div>

            <reason type="price" @blur="validateReason()" v-model="priceHistory.reason" ></reason>
            <div v-show="requireDetails" class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Comment: </label>
                    </div>
                    <div class="col-md-5">
                        <textarea name="comments" @blur="validateReason()" v-model="priceHistory.comments" class="form-control"></textarea>
                    </div>
                </div>
            </div>


        </form>
    </div>

</bootstrapModal>
</template>

<script>
import 'foundation-sites';
import 'foundation-datepicker/js/foundation-datepicker';
import moment from 'moment'
import JQuery from 'jquery'
import bootstrapModal from '../utils/bootstrap-modal.vue'
import reason from '../utils/reasons.vue'
import { api_endpoints, validate, helpers, bus } from '../hooks'
import alert from '../utils/alert.vue'
module.exports = {
    name: 'ParkPriceHistoryDetail',
    props: {
        priceHistory: {
            type: Object,
            required: true,
        },
    },
    data: function() {
        let vm = this;
        return {
            id:'',
            title: '',
            current_closure: '',
            closeStartPicker: '',
            arrivalData: '',
            showDetails: false,
            closeEndPicker: '',
            errors: false,
            errorString: '',
            form: '',
            reasons: [],
            isOpen: false,
            mooring_groups: [],
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
            return this.priceHistory.id ? this.priceHistory.id : '';
        },
        requireDetails: function() {
            let vm = this;
            var check = this.priceHistory.reason
            for (var i = 0; i < vm.reasons.length; i++){
                if (vm.reasons[i].id == check){
                    return vm.reasons[i].detailRequired;
                }
            }
        },
    },
    watch: {
    },
    components: {
        bootstrapModal,
        alert,
        reason
    },
    methods: {
        close: function() {
            delete this.priceHistory.original;
            this.errors = false;
            this.selected_rate = '';
            this.priceHistory.period_start= '';
            this.priceHistory.comments= '';
            this.priceHistory.period_end='';
            this.priceHistory.adult_cost='';
            this.priceHistory.adult_overnight_cost='';
            this.priceHistory.children_cost='';
            this.priceHistory.children_overnight_cost='';
            this.priceHistory.infant_cost='';
            this.priceHistory.infant_overnight_cost='';
            this.priceHistory.family_cost='';
            this.priceHistory.family_overnight_cost='';
            this.priceHistory.reason={id:1};

            this.errorString = '';
            this.isOpen = false;
            // this.$emit("cancel");
        },
        addHistory: function() {
            if(this.validateForm()){
                if ($(this.form).valid()){
                    if (this.priceHistory.id){
                        this.$emit('updateParkPriceHistory');
                    }else {
                        this.$emit('addParkPriceHistory');
                    } 
                }
                
            }
        },
        validateForm: function(){
            var isValid = true;
            isValid = this.validatePeriodStart();
            if(isValid){
                isValid = this.validateReason();
            }
            return isValid;
        },
        validateReason: function(){
            if(!Number.isInteger(parseInt(this.priceHistory.reason))){
                this.errorString = "Please select a reason.";
                this.errors = true;
                return false;
            } else if(this.requireDetails){
                if(!this.priceHistory.comments || this.priceHistory.comments == ""){
                    this.errorString = "Please enter further details to explain the reason.";
                    this.errors = true;
                    return false;
                } else {
                    this.errorString = "";
                    this.errors = false;
                    return true;
                }
            } else {
                this.errorString = "";
                this.errors = false;
                return true;
            }  
        },
        validatePeriodStart: function(){
            if(!this.priceHistory.period_start || this.priceHistory.period_start == "" || this.priceHistory.period_start == undefined){
                this.errorString = "Please select a Period Start date.";
                this.errors = true;
                return false;
            } else {
                this.errorString = "";
                this.errors = false;
                return true;
            }
        },
        addFormValidations: function() {
            let vm = this;
            $(vm.form).validate({
                rules: {
                    period_start: "required",
                    comments: {
                        required: {
                            depends: function(el){
                                var check = vm.priceHistory.reason;
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
                    period_start: "Enter a start date",
                    comments: "Details required if certain reasons are selected"
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
        vm.form = document.forms.priceForm;

        var today = new Date();
        today.setDate(today.getDate()+1);
        var tomorrow = new Date(today);

        // var datepickerOptions = {
        //     format: 'DD/MM/YYYY',
        //     showClear:true,
        //     useCurrent:false,
        //     keepInvalid:true,
        //     allowInputToggle:true
        // }

        // var picker = $('#period_start').datetimepicker(datepickerOptions);
        // var picker2 = $('#period_end').datetimepicker(datepickerOptions);

        // picker.on('dp.change',function (e) {
        //     if (picker.data('DateTimePicker').date()) {
        //         vm.priceHistory.period_start = e.date.format('DD/MM/YYYY');
        //     }
        //     else if (vm.dateFromPicker.data('date') === "") {
        //         vm.priceHistory.period_start = "";
        //     }

        // });

        // picker2.on('dp.change',function (e) {
        //     if (picker2.data('DateTimePicker').date()) {
        //         vm.priceHistory.period_end = e.date.format('DD/MM/YYYY');
        //     }
        //     else if (vm.dateFromPicker.data('date') === "") {
        //         vm.priceHistory.period_end = "";
        //     }

        // });

        var mg = $('#mooring_groups').val();
        vm.mooring_groups = JSON.parse( mg );

        $(document).foundation();
        var arrivalEl = $('#period_start');
        var arrivalDate = null;

        this.arrivalData = arrivalEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                return;
            }
        }).on('changeDate', function (ev) {
            ev.target.dispatchEvent(new CustomEvent('change'));
        }).on('change', function (ev) {
            vm.arrivalData.hide();
            // console.log(vm.arrivalData.date);
            // vm.priceHistory.period_start = moment(vm.arrivalData.date, "DD/MM/YYYY");
            console.log(ev.target.value);
            vm.priceHistory.period_start = ev.target.value;

            // console.log(vm.priceHistory.period_start);
        }).on('keydown', function (ev) {
            if (ev.keyCode == 13) {
                ev.target.dispatchEvent(new CustomEvent('change'));
            }
        }).data('datepicker');

        if (arrivalDate != null){
            this.arrivalData.date = arrivalDate.toDate();
            this.arrivalData.setValue();
            this.arrivalData.fill();
        }


        // var picker = $(vm.form.period_start).closest('.date');
        // picker.datetimepicker({
        //     format: 'DD/MM/YYYY',
        //     useCurrent: false,
        //     minDate: tomorrow
        // });
        // picker.on('dp.change', function(e){
        //     vm.priceHistory.period_start = picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        // });
        // var picker2 = $(vm.form.period_end).closest('.date');
        // picker2.datetimepicker({
        //     format: 'DD/MM/YYYY',
        //     useCurrent: false,
        //     minDate: tomorrow
        // })
        // picker2.on('dp.change', function(e){
        //     vm.priceHistory.period_end = picker2.data('DateTimePicker').date().format('DD/MM/YYYY');
        // });



        vm.addFormValidations();
        bus.$once('reasons',setReasons => {
            vm.reasons = setReasons;
        });
    }
};
</script>
<style lang="css" scoped>
</style>
