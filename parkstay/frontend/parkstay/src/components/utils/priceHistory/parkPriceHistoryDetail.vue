<template id="ParkPriceHistoryDetail">
<bootstrapModal title="Add Park Price History" :large=true @ok="addHistory()" @close="close()">

    <div class="modal-body">
        <form name="priceForm" class="form-horizontal">
			<alert :show.sync="showError" type="danger">{{errorString}}</alert>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Vehicle : </label>
                    </div>
                    <div class="col-md-4">
                        <input :readonly="selected_rate != ''" name="vehicle"  v-model="priceHistory.vehicle" type='text' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Concession : </label>
                    </div>
                    <div class="col-md-4">
                        <input :readonly="selected_rate != ''" name="concession"  v-model="priceHistory.concession" type='text' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Motorbike : </label>
                    </div>
                    <div class="col-md-4">
                        <input :readonly="selected_rate != ''" name="motorbike"  v-model="priceHistory.motorbike" type='text' class="form-control" />
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
            <reason type="price" v-model="priceHistory.reason" ></reason>
            <div v-show="requireDetails" class="row">
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
import reason from '../reasons.vue'
import { $, datetimepicker,api_endpoints, validate, helpers } from '../../../hooks'
import alert from '../alert.vue'
module.exports = {
    name: 'ParkPriceHistoryDetail',
    props: {
        priceHistory: {
            type: Object,
            required: true
        },
    },
    data: function() {
        let vm = this;
        return {
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
        },
        requireDetails: function() {
            return this.priceHistory.reason == '1';
        },
    },
    watch: {
        selected_rate: function() {
            let vm = this;
            if (vm.selected_rate != ''){
                $.each(vm.rates, function(i, rate) {
                    if (rate.id== vm.selected_rate){
                        vm.priceHistory.rate = rate.id;
                        vm.priceHistory.vehicle = rate.vehicle;
                        vm.priceHistory.concession = rate.concession;
                        vm.priceHistory.motorbike = rate.motorbike;
                        vm.priceHistory.infant = rate.infant;
                    }
                });
            }
            else{
                delete vm.priceHistory.rate;
                vm.priceHistory.vehicle = '';
                vm.priceHistory.concession = '';
                vm.priceHistory.motorbike = '';
                vm.priceHistory.infant = '';
            }
        }
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
            this.priceHistory.details= '';

            this.errorString = '';
            this.isOpen = false;
        },
        addHistory: function() {
            if ($(this.form).valid()){
                if (this.priceHistory.id || this.priceHistory.original){
                    this.$emit('updateParkPriceHistory');
                }else {
                    this.$emit('addParkPriceHistory');
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
                    vehicle: "required",
                    concession: "required",
                    motorbike: "required",
                    infant:"required",
                    period_start: "required",
                    details: {
                        required: {
                            depends: function(el){
                                return vm.priceHistory.reason=== '1';
                            }
                        }
                    }
                },
                messages: {
                    vehicle: "Enter an vehicle rate",
                    concession: "Enter a concession rate",
                    motorbike: "Enter a motorbike rate",
                    infant: "Enter a infant rate",
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
        vm.form = document.forms.priceForm;
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
            vm.priceHistory.period_start = picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.addFormValidations();
        vm.fetchRates();
    }
};
</script>
<style lang="css" scoped>
</style>
