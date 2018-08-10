<template id="pkCgClose">
<bootstrapModal title="(Temporarily) close campground" :large=true @ok="addClosure()">

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
                        <label for="open_cg_range_start">Reopen: </label>
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
            <reason type="close" v-model="formdata.closure_reason" ref="reason"></reason>
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
import bootstrapModal from '../utils/bootstrap-modal.vue'
import {bus} from '../utils/eventBus.js'
import { $, datetimepicker,api_endpoints, validate, helpers } from '../../hooks'
import alert from '../utils/alert.vue'
import reason from '../utils/reasons.vue'
module.exports = {
    name: 'pkCgClose',
    data: function() {
        return {
            status: '',
            id:'',
            formdata: {
                range_start: '',
                range_end: '',
                closure_reason:'',
                status:'1',
                details: ''
            },
            closeStartPicker: '',
            closeEndPicker: '',
            errors: false,
            errorString: '',
            form: ''
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        isModalOpen: function() {
            return this.$parent.isOpenCloseCG;
        },
        requireDetails: function () {
            let vm =this;
            return (vm.formdata.closure_reason == 1)? true: false;
        },
    },
    components: {
        bootstrapModal,
        alert,
        reason
    },
    methods: {
        close: function() {
            this.$parent.isOpenCloseCG = false;
            this.formdata = {
                range_start: '',
                range_end: '',
                closure_reason:'',
                status:'1',
                details: ''
            };
            this.$refs.reason.selected = "";
        },
        addClosure: function() {
            if (this.form.valid()){
                this.sendData();
            }
        },
        sendData: function() {
            let vm = this;
            var data = this.formdata;
            $.ajax({
                url: api_endpoints.opencloseCG(vm.id),
                method: 'POST',
                xhrFields: { withCredentials:true },
                data: data,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.close();
                    bus.$emit('refreshCGTable');
                },
                error:function (data){
                    vm.errors = true;
                    vm.errorString = helpers.apiError(data);
                }
            });
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
                                return vm.formdata.closure_reason === '1';
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
        bus.$on('openclose', function(data){
            vm.status = data.status;
            vm.id = data.id;
        });
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
