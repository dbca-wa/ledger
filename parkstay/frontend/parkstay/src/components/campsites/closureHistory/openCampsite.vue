<template id="pkCsOpen">
<bootstrapModal title="Open campsite" :large=true @ok="addOpen()">

    <div class="modal-body">
        <form id="openCGForm" class="form-horizontal">
            <div class="row">
			    <alert :show.sync="showError" type="danger"></alert>
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_current_closure">Current Closure: </label>
                    </div>
                    <div class="col-md-4">
                        <input id='open_cg_current_closure' v-model="current_closure" disabled type='text' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_range_end">Reopen on: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' id='open_cg_range_end'>
                            <input name="open_start" v-model="formdata.range_end" type='text' class="form-control" />
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <reason type="close" v-model="formdata.closure_reason"></reason>
            <div v-show="requireDetails" class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_details">Details: </label>
                    </div>
                    <div class="col-md-5">
                        <textarea name="open_details" v-model="formdata.details" class="form-control" id="open_cg_details"></textarea>
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
    name: 'pkCsOpen',
    data: function() {
        return {
            id:'',
            current_closure: '',
            formdata: {
                range_end: '',
                closure_reason:'',
                details: ''
            },
            picker: '',
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
            return (this.formdata.closure_reason === '1');
        }
    },
    components: {
        bootstrapModal,
        alert,
        reason
    },
    methods: {
        close: function() {
            this.isOpen = false;
            this.formdata.closure_reason = ''
        },
        addOpen: function() {
            if (this.form.valid()){
                this.$emit('openCampsite');
            }
        },
        addFormValidations: function() {
            let vm = this;
            this.form.validate({
                rules: {
                    open_start: "required",
                    open_reason: "required",
                    open_details: {
                        required: {
                            depends: function(el){
                                return vm.requireDetails;
                            }
                        }
                    }
                },
                messages: {
                    open_start: "Enter a reopening date",
                    open_reason: "Select an open reason from the options",
                    open_details: "Details required if Other reason is selected"
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
        vm.picker = $('#open_cg_range_end');
        vm.picker.datetimepicker({
            format: 'DD/MM/YYYY'
        });
        vm.picker.on('dp.change', function(e){
            vm.formdata.range_end = vm.picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.form = $('#openCGForm');
        vm.addFormValidations();
    }
};
</script>
