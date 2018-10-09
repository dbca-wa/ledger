<template id="addMaxStayCS">
<bootstrapModal ref="modal" :title="getTitle" :large=true @ok="addMaxStay()" okText="Add">

    <div class="modal-body">
        <form id="addMaxStayForm" class="form-horizontal">
            <div class="row">
			    <alert :show.sync="showError" type="danger">{{errorString}}</alert>
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="stay_maximum">Maximum Stay: </label>
                    </div>
                    <div class="col-md-4">
                        <input placeholder="Default = 28" id='stay_maximum' v-model="stay.max_days" type='text' class="form-control" />
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="stay_start_picker">Period Start: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' id="stay_start_picker">
                            <input name="stay_start" v-model="stay.range_start" type='text' class="form-control" />
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
                        <label for="stay_end_picker">Period End: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' id='stay_end_picker'>
                            <input name="stay_end" v-model="stay.range_end" type='text' class="form-control" />
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <reason type="stay" v-model="stay.reason" ref="reason"></reason>
            <div v-show="requireDetails" class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="stay_details">Details: </label>
                    </div>
                    <div class="col-md-5">
                        <textarea name="stay_details" v-model="stay.details" class="form-control" id="stay_details"></textarea>
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
    name: 'addMaxStayCS',
    props: {
        mooringarea: {
            type: Object,
            required: true
        },
        stay: {
            type: Object
        }
    },
    data: function() {
        return {
            start_picker: '',
            end_picker: '',
            errors: false,
            errorString: '',
            form: '',
            isOpen: false,
            create: true
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
        getTitle: function() {
            return this.create ? 'Add New Maximum Stay Period' : 'Edit Maximum Stay Period';
        },
        requireDetails: function () {
            let vm = this;
            return (vm.stay.reason == 1)? true: false;
        }
    },
    components: {
        bootstrapModal,
        alert,
        reason
    },
    methods: {
        close: function() {
            this.stay.max_days= '';
            this.stay.range_start = '';
            this.stay.range_end = '';
            this.stay.reason = '';
            this.stay.details = '';

            this.isOpen = false;
            this.errors = false;
            this.errorString = '';
            this.status = '';
        },
        updateReason:function (id) {
            this.stay.reason = id;
        },
        addMaxStay: function() {
            if ($(this.form).valid()){
                if (!this.stay.id){
                    this.$emit('addCgStayHistory');
                }else {
                    this.$emit('updateStayHistory');
                }
            }
        },
        addFormValidations: function() {
            let vm = this;
            this.form.validate({
                rules: {
                    stay_start: "required",
                    stay_end: "required",
                    stay_reason: "required",
                    stay_details: {
                        required: {
                            depends: function(el){
                                return vm.stay.reason == 1;
                            }
                        }
                    }
                },
                messages: {
                    stay_start: "Enter a start date",
                    stay_reason: "Select an open reason from the options",
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
        if (!vm.create){
            vm.$refs.modal.title = 'Edit Maximum Stay Period';
        }
        vm.start_picker = $('#stay_start_picker');
        vm.end_picker = $('#stay_end_picker');
        vm.start_picker.datetimepicker({
            format: 'DD/MM/YYYY'
        });
        vm.end_picker.datetimepicker({
            format: 'DD/MM/YYYY'
        });
        vm.start_picker.on('dp.change', function(e){
            vm.stay.range_start = vm.start_picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.end_picker.on('dp.change', function(e){
            vm.stay.range_end = vm.end_picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.form = $('#addMaxStayForm');
        vm.addFormValidations();
    }
};
</script>
