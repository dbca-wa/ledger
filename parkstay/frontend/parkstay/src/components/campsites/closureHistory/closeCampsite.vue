<template id="pkCsClose">
<bootstrapModal title="(Temporarily) close campsite" :large=true @ok="addClosure()">

    <div class="modal-body">
        <form id="closeCGForm" class="form-horizontal">
            <div class="row">
			    <alert :show.sync="showError" type="danger">{{errorString}}</alert>
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_range_start">Closure start: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' id='close_cg_range_start'>
                            <input  name="closure_start" v-model="formdata.range_start" type='text' class="form-control" />
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
                        <label for="open_cg_range_start">Reopen on: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' id='close_cg_range_end'>
                            <input name="closure_end" v-model="formdata.range_end" type='text' class="form-control" />
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <reason type="close" ref="reason" v-model="reason"></reason>
            <div v-show="requireDetails" class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_details">Details: </label>
                    </div>
                    <div class="col-md-5">
                        <textarea name="closure_details" v-model="formdata.details" class="form-control" id="close_cg_details"></textarea>
                    </div>
                </div>
            </div>
        </form>
    </div>

</bootstrapModal>
</template>

<script>
import bootstrapModal from '../../utils/bootstrap-modal.vue'
import reason from '../../utils/reasons.vue'
import {bus} from '../../utils/eventBus.js'
import { $, datetimepicker,api_endpoints, validate, helpers } from '../../../hooks'
import alert from '../../utils/alert.vue'
module.exports = {
    name: 'pkCsClose',
    data: function() {
        return {
            reason:'',
            formdata: {
                campsite: '',
                status: 1,
                range_start: '',
                range_end: '',
                closure_reason:'',
                details: ''
            },
            closeStartPicker: '',
            closeEndPicker: '',
            errors: false,
            errorString: '',
            form: '',
            isOpen: false
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
        requireDetails: function () {
            let vm =this;
            return (vm.formdata.closure_reason === '1');
        },
    },
    components: {
        bootstrapModal,
        alert,
        reason
    },
    watch:{
        reason:function () {
            this.formdata.closure_reason = this.reason;

        }
    },
    methods: {
        close: function() {
            this.isOpen = false;
            this.formdata = {
                status:1,
                range_start: '',
                range_end: '',
                closure_reason:'',
                details: ''
            };
            this.$refs.reason.selected = "";
        },
        addClosure: function() {
            if (this.form.valid()){
                this.$emit('closeCampsite');
            }
        },
        addFormValidations: function() {
            let vm = this;
            this.form.validate({
                rules: {
                    closure_start: "required",
                    closure_reason: "required",
                    closure_details: {
                        required: {
                            depends: function(el){
                                return vm.requireDetails;
                            }
                        }
                    }
                },
                messages: {
                    closure_start: "Enter a start date",
                    closure_reason: "Select a closure reason from the options",
                    closure_details: "Details required if Other reason is selected"
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
        vm.closeStartPicker = $('#close_cg_range_start');
        vm.closeEndPicker = $('#close_cg_range_end');
        vm.closeStartPicker.datetimepicker({
            format: 'DD/MM/YYYY',
            minDate: new Date()
        });
        vm.closeEndPicker.datetimepicker({
            format: 'DD/MM/YYYY',
            useCurrent: false
        });
        vm.closeStartPicker.on('dp.change', function(e){
            vm.formdata.range_start = vm.closeStartPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
            vm.closeEndPicker.data("DateTimePicker").minDate(e.date);
        });
        vm.closeEndPicker.on('dp.change', function(e){
            vm.formdata.range_end = vm.closeEndPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.form = $('#closeCGForm');
        vm.addFormValidations();
    }
};
</script>
