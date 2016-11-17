<template id="addMaxStayCS">
<bootstrapModal title="Add New Maximum Stay Period" :large=true @ok="addMaxStay()" okText="Add">

    <div class="modal-body">
        <form id="addMaxStayForm" class="form-horizontal">
            <div class="row">
			    <alert :show.sync="showError" type="danger"></alert>
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="stay_maximum">Maximum Stay: </label>
                    </div>
                    <div class="col-md-4">
                        <input placeholder="Default = 28" id='stay_maximum' v-model="formdata.max_days" type='text' class="form-control" />
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
                            <input name="stay_start" v-model="formdata.range_start" type='text' class="form-control" />
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
                            <input name="stay_end" v-model="formdata.range_end" type='text' class="form-control" />
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
                        <label for="stay_reason">Reason: </label>
                    </div>
                    <div class="col-md-4">
                        <select name="stay_reason" v-model="formdata.reason" class="form-control" id="stay_reason">
                            <option value="1">Reason 1</option>
                            <option value="2">Reason 2</option>
                            <option value="3">Reason 3</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
            </div>
            <div v-show="requireDetails" class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="stay_details">Details: </label>
                    </div>
                    <div class="col-md-5">
                        <textarea name="stay_details" v-model="formdata.details" class="form-control" id="stay_details"></textarea>
                    </div>
                </div>
            </div>
        </form>
    </div>

</bootstrapModal>
</template>

<script>
import bootstrapModal from '../utils/bootstrap-modal.vue'
import {bus} from '../utils/eventBus.js'
import { $, datetimepicker,api_endpoints, validate, helpers } from '../../hooks'
import alert from '../utils/alert.vue'
module.exports = {
    name: 'addMaxStayCS',
    props: {
        campsite: {
            type: Object,
            required: true
        }
    },
    data: function() {
        return {
            formdata: {
                max_days: '',
                range_start: '',
                range_end: '',
                reason:'',
                details: ''
            },
            start_picker: '',
            end_picker: '',
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
            return (this.formdata.reason === 'other')? true: false;
        }
    },
    components: {
        bootstrapModal,
        alert
    },
    methods: {
        close: function() {
            this.isOpen = false;
            this.status = '';
        },
        addMaxStay: function() {
            if (this.form.valid()){
                this.sendData();
            }
        },
        sendData: function() {
            let vm = this;
            var data = this.formdata;
            data.campsite = vm.campsite.id;
            $.ajax({
                url: api_endpoints.campsites_stay_history,
                method: 'POST',
                xhrFields: { withCredentials:true },
                data: data,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.close();
                    vm.$parent.refreshMaxStayTable();
                },
                error:function (resp){
                    vm.errors = true;
                    vm.errorString = helpers.apiError(resp);
                }
            });

        },
        addFormValidations: function() {
            let vm = this;
            this.form.validate({
                rules: {
                    stay_start: "required",
                    stay_reason: "required",
                    stay_details: {
                        required: {
                            depends: function(el){
                                return vm.formdata.reason === 'other';
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
        vm.start_picker = $('#stay_start_picker');
        vm.end_picker = $('#stay_end_picker');
        vm.start_picker.datetimepicker({
            format: 'DD/MM/YYYY'
        });
        vm.end_picker.datetimepicker({
            format: 'DD/MM/YYYY'
        });
        vm.start_picker.on('dp.change', function(e){
            vm.formdata.range_start = vm.start_picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.end_picker.on('dp.change', function(e){
            vm.formdata.range_end = vm.end_picker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.form = $('#addMaxStayForm');
        vm.addFormValidations();
    }
};
</script>
