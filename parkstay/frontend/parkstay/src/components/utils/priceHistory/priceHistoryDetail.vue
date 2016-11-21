<template id="PriceHistoryDetail">
<bootstrapModal :title="title" :large=true @ok="addHistory()">

    <div class="modal-body">
        <form name="priceForm" class="form-horizontal">
			<alert :show.sync="showError" type="danger">{{errorString}}</alert>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Select Rate: </label>
                    </div>
                    <div class="col-md-4">
                        <select name="rate" v-model="selected_rate" class="form-control">
                            <option value=""></option>
                            <option v-for="r in rates":value="r.id">{{r.name}}</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Adult Price: </label>
                    </div>
                    <div class="col-md-4">
                        <input :readonly="selected_rate != ''" name="adult"  v-model="priceHistory.adult" type='text' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Concession Price: </label>
                    </div>
                    <div class="col-md-4">
                        <input :readonly="selected_rate != ''" name="concession"  v-model="priceHistory.concession" type='text' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Child Price: </label>
                    </div>
                    <div class="col-md-4">
                        <input :readonly="selected_rate != ''" name="child"  v-model="priceHistory.child" type='text' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Period start: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date'>
                            <input  name="period_start"  v-model="priceHistory.period_start" type='text' class="form-control" />
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
                        <label>Reason: </label>
                    </div>
                    <div class="col-md-4">
                        <select v-on:change="requireDetails()" name="reason" v-model="priceHistory.reason" class="form-control" id="close_cg_reason">
                            <option value="1">Closed due to natural disaster</option>
                            <option value="2">Closed for maintenance</option>
                            <option value="3">Other</option>
                        </select>
                    </div>
                </div>
            </div>
            <div v-show="showDetails" class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Details: </label>
                    </div>
                    <div class="col-md-5">
                        <textarea name="details" v-model="priceHistory.details" class="form-control"></textarea>
                    </div>
                </div>
            </div>
        </form>
    </div>

</bootstrapModal>
</template>

<script>
import bootstrapModal from '../bootstrap-modal.vue'
import { $, datetimepicker,api_endpoints, validate, helpers } from '../../../hooks'
import alert from '../alert.vue'
module.exports = {
    name: 'PriceHistoryDetail',
    props: {
        priceHistory: {
            type: Object,
            required: true
        },
        title: {
            type: String,
            required: true
        }
    },
    data: function() {
        let vm = this;
        return {
            id:'',
            selected_rate: '',
            rates: [],
            current_closure: '',
            closeStartPicker: '',
            showDetails: false,
            closeEndPicker: '',
            errors: false,
            errorString: '',
            form: '',
            isOpen: false,
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
        }
    },
    watch: {
        selected_rate: function() {
            let vm = this;
            if (vm.selected_rate != ''){
                $.each(vm.rates, function(i, rate) {
                    if (rate.url == vm.selected_rate){
                        vm.priceHistory.adult = rate.adult;
                        vm.priceHistory.concession = rate.concession;
                        vm.priceHistory.child = rate.child;
                    }
                });
            }
            else{
                vm.priceHistory.adult = '';
                vm.priceHistory.concession = '';
                vm.priceHistory.child = '';
            }
        }
    },
    components: {
        bootstrapModal,
        alert
    },
    methods: {
        requireDetails: function() {
            this.showDetails =  this.priceHistory.reason == 3;
        },
        close: function() {
            //this.priceHistory = {};
            this.errors = false;
            this.errorString = '';
            this.isOpen = false;
        },
        addHistory: function() {
            if ($(this.form).valid()){
                if (!this.priceHistory.id){
                    this.$emit('addPriceHistory');
                }else {
                    this.$emit('updatePriceHistory');
                }
            }
        },
        fetchRates: function() {
            let vm = this;
            $.get(api_endpoints.rates,function(data){
                vm.rates = data;    
            });
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
                                return vm.priceHistory.reason=== '3';
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
        vm.form = document.forms.priceForm;
        var picker = $(vm.form.period_start).closest('.date');
        picker.datetimepicker({
            format: 'DD/MM/YYYY',
            minDate: new Date()
        });
        picker.on('dp.change', function(e){
            vm.priceHistory.period_start = picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.addFormValidations();
        vm.fetchRates();
    }
};
</script>
