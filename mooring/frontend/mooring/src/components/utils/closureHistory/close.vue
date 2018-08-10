<template id="Close">
<bootstrapModal :title="title" :large=true @ok="addClosure()">

    <div class="modal-body">
        <form name="closeForm" class="form-horizontal">
            <div class="row">
			    <alert :show.sync="showError" type="danger">{{errorString}}</alert>
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_range_start">Closure start: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' :id='close_cg_range_start'>
                            <input  name="closure_start"  v-model="statusHistory.range_start" type='text' class="form-control" />
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
                        <div class='input-group date' :id='close_cg_range_end'>
                            <input name="closure_end" v-model="statusHistory.range_end" type='text' class="form-control" />
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <reason type="close" v-model="statusHistory.closure_reason" ></reason>
            <div v-show="requireDetails" class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label>Details: </label>
                    </div>
                    <div class="col-md-4">
                        <textarea name="closure_details" v-model="statusHistory.details" class="form-control" id="close_cg_details"></textarea>
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
import reason from '../reasons.vue'
module.exports = {
    name: 'Close',
    props: {
        statusHistory: {
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
            current_closure: '',
            closeStartPicker: '',
            showDetails:false,
            closeEndPicker: '',
            errors: false,
            errorString: '',
            form: '',
            isOpen: false,
            close_cg_range_start: 'close_cg_range_start'+vm._uid,
            close_cg_range_end: 'close_cg_range_end'+vm._uid,
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
            return this.statusHistory.id ? this.statusHistory.id : '';
        },
        requireDetails: function() {
            return this.statusHistory.closure_reason == '1';
        },
    },
    components: {
        bootstrapModal,
        alert,
        reason
    },
    methods: {
        close: function() {
            this.errors = false;
            this.errorString = '';
            this.isOpen = false;
            this.statusHistory.id = '';
            this.statusHistory.range_start= '';
            this.statusHistory.range_end= '';
            this.statusHistory.status= '1';
            this.statusHistory.details= '';
            this.statusHistory.reason = '';
            this.statusHistory.closure_reason = '';
            var today = new Date();
            this.closeEndPicker.data('DateTimePicker').clear();
            this.closeStartPicker.data('DateTimePicker').clear();
        },
        addClosure: function() {
            if (this.form.valid()){
                if (!this.closure_id){
                    this.$emit('closeRange');
                }else {
                    this.$emit('updateRange');
                }
            }
        },
        addFormValidations: function() {
            let vm = this;
            vm.form.validate({
                rules: {
                    closure_start: "required",
                    closure_status: "required",
                    closure_details: {
                        required: {
                            depends: function(el){
                                return vm.statusHistory.reason=== '1';
                            }
                        }
                    }
                },
                messages: {
                    closure_start: "Enter a start date",
                    closure_status: "Select a closure reason from the options",
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
        vm.statusHistory.status=1;
        vm.statusHistory.reason='';
        vm.closeEndPicker = $('#'+vm.close_cg_range_end);
        vm.closeStartPicker = $('#'+vm.close_cg_range_start).datetimepicker({
            format: 'DD/MM/YYYY',
            minDate: new Date()
        });
        vm.closeEndPicker.datetimepicker({
            format: 'DD/MM/YYYY',
            useCurrent: false
        });
        vm.closeStartPicker.on('dp.change', function(e){
            vm.statusHistory.range_start = vm.closeStartPicker.data('DateTimePicker').date() != null ? vm.closeStartPicker.data('DateTimePicker').date().format('DD/MM/YYYY') : '';
            e.date != null ? vm.closeEndPicker.data("DateTimePicker").minDate(e.date): '';
        });
        vm.closeEndPicker.on('dp.change', function(e){
            vm.statusHistory.range_end = vm.closeEndPicker.data('DateTimePicker').date() != null  ? vm.closeEndPicker.data('DateTimePicker').date().format('DD/MM/YYYY') : '';
        });
        vm.form = $(document.forms.closeForm);
        vm.addFormValidations();
    },
};
</script>
