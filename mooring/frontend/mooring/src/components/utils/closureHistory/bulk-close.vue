<template lang="html">
    <div id="bulk-close">
        <modal okText="Close Moorings" @ok="closeCampgrounds()" :force="true">
            <h4 slot="title">Bulk Close Moorings</h4>
            <div class="body">
                <alert :show="false" type="danger">{{errorString}}</alert>
                <form name="closeForm" class="form-horizontal">
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-4">
                                <label for="Moorings">Moorings</label>
                            </div>
                            <div class="col-md-8">
                                <select  class="form-control" id="bc-campgrounds" name="campgrounds" placeholder="" multiple v-model="selected_campgrounds">
                                    <option v-for="c in campgrounds" :value="c.id">{{ c.name }}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-4">
                                <label for="open_cg_range_start">Closure start: </label>
                            </div>
                            <div class="col-md-8">
                                <div class='input-group date' :id='close_cg_range_start'>
                                    <input  name="closure_start"  v-model="range_start" type='text' class="form-control" />
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <div class="col-md-4">
                                <label for="open_cg_range_start">Reopen: </label>
                            </div>
                            <div class="col-md-8">
                                <div class='input-group date' :id='close_cg_range_end'>
                                    <input name="closure_end" v-model="range_end" type='text' class="form-control" />
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <reason type="close" v-model="reason" :large="true" ></reason>
                    <div v-show="requireDetails" class="row">
                        <div class="form-group">
                            <div class="col-md-4">
                                <label>Details: </label>
                            </div>
                            <div class="col-md-8">
                                <textarea name="closure_details" v-model="details" class="form-control" id="close_cg_details"></textarea>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </modal>
    </div>
</template>

<script>
import modal from '../bootstrap-modal.vue'
import reason from '../reasons.vue'
import alert from '../alert.vue'
import { mapGetters } from 'vuex'
import { $, datetimepicker,api_endpoints, validate, helpers } from '../../../hooks'

export default {
    name:"bulk-close",
    data:function () {
        let vm =this;
        return {
            isModalOpen:false,
            closeEndPicker:null,
            closeStartPicker:null,
            reason:'',
            range_start:'',
            range_end:'',
            close_cg_range_end:'close_cg_range_end'+vm._uid,
            close_cg_range_start:'close_cg_range_start'+vm._uid,
            selected_campgrounds:[],
            form: null
        }
    },
    computed:{
        requireDetails:function () {
            return (this.reason == '1')
        },
        ...mapGetters([
          'campgrounds'
        ]),
    },
    components:{
        modal,
        reason,
        alert
    },
    methods:{
        close:function () {
            this.isModalOpen = this.$parent.showBulkClose  = false;
            this.$parent.$refs.dtGrounds.vmDataTable.ajax.reload();
            this.range_start = "";
            this.range_end = "";
            this.campgrounds = "";
            this.reason = "";
			this.closeStartPicker.data('DateTimePicker').date(new Date());
			this.closeEndPicker.data('DateTimePicker').clear();
        },
        events:function () {
            let vm = this;
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
                vm.range_start = vm.closeStartPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
                vm.closeEndPicker.data("DateTimePicker").minDate(e.date);
            });
            vm.closeEndPicker.on('dp.change', function(e){
                var date = vm.closeEndPicker.data('DateTimePicker').date();
                vm.range_end = (date) ? date.format('DD/MM/YYYY') : null;
            });
            vm.addFormValidations();
            vm.fetchCampgrounds();
            vm.initSelectTwo();
        },
        fetchCampgrounds: function() {
            let vm = this;
            if (vm.campgrounds.length == 0) {
                vm.$store.dispatch("fetchCampgrounds");
            }
        },
        initSelectTwo:function () {
            let vm = this;
            setTimeout(function () {
                $('#bc-campgrounds').select2({
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
            },100)
        },
        closeCampgrounds:function () {
            let vm =this;

            if (vm.form.valid() && vm.selected_campgrounds.length>0){
                let vm = this;
                let data = {
                    range_start: vm.range_start,
                    range_end: vm.range_end,
                    campgrounds: vm.selected_campgrounds,
                    reason: vm.reason,
                    status:'1'
                }
                if (vm.reason == '1') {
                    data.details = vm.details
                }
                $.ajax({
                    url:api_endpoints.bulk_close,
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
                        vm.$store.dispatch("updateAlert",{
        					visible:true,
        					type:"danger",
        					message: helpers.apiError(resp)
                        });
                        vm.close();
                    }
                });
            }

        },
        addFormValidations: function() {
            let vm = this;
            vm.form.validate({
                rules: {
                    closure_start: "required",
                    closure_status: "required",
                    open_reason: "required",
                    closure_details: {
                        required: {
                            depends: function(el){
                                return vm.reason === '1';
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
    mounted:function () {
        let vm = this;
        vm.form = $(document.forms.closeForm);
        vm.events();
    }
}

</script>

<style lang="css">
.body{
    padding:0 20px;
}
</style>
