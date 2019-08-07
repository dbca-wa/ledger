<template lang="html">
    <div id="proposalRequirementDetail">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Requirement" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="requirementForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <label class="radio-inline control-label"><input type="radio" name="requirementType" :value="true" v-model="requirement.standard">Standard Requirement</label>
                                <label class="radio-inline"><input type="radio" name="requirementType" :value="false" v-model="requirement.standard">Free Text Requirement</label>
                            </div>
                        </div>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="Name">Requirement</label>
                                    </div>
                                    <div class="col-sm-9" v-if="requirement.standard">
                                        <div style="width:70% !important">
                                            <select class="form-control" ref="standard_req" name="standard_requirement" v-model="requirement.standard_requirement">
                                                <option v-for="r in requirements" :value="r.id">{{r.code}} {{r.text}}</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-sm-9" v-else>
                                        <textarea style="width: 70%;"class="form-control" name="free_requirement" v-model="requirement.free_requirement"></textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-left"  for="Name">Due Date</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div class="input-group date" ref="due_date" style="width: 70%;">
                                            <input type="text" class="form-control" name="due_date" placeholder="DD/MM/YYYY" v-model="requirement.due_date">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <template v-if="validDate">
                                <div class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left"  for="Name">Recurrence</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <label class="checkbox-inline"><input type="checkbox" v-model="requirement.recurrence"></label>
                                        </div>
                                    </div>
                                </div>
                                <template v-if="requirement.recurrence">
                                    <div class="form-group">
                                        <div class="row">
                                            <div class="col-sm-3">
                                                <label class="control-label pull-left"  for="Name">Recurrence pattern</label>
                                            </div>
                                            <div class="col-sm-9">
                                                <label class="radio-inline control-label"><input type="radio" name="recurrenceSchedule" value="1" v-model="requirement.recurrence_pattern">Weekly</label>
                                                <label class="radio-inline control-label"><input type="radio" name="recurrenceSchedule" value="2" v-model="requirement.recurrence_pattern">Monthly</label>
                                                <label class="radio-inline control-label"><input type="radio" name="recurrenceSchedule" value="3" v-model="requirement.recurrence_pattern">Yearly</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="row">
                                            <div class="col-sm-12">
                                                <label class="control-label"  for="Name">
                                                    <strong class="pull-left">Recur every</strong> 
                                                    <input class="pull-left" style="width:10%; margin-left:10px;" type="number" name="schedule" v-model="requirement.recurrence_schedule"/> 
                                                    <strong v-if="requirement.recurrence_pattern == '1'" class="pull-left" style="margin-left:10px;">week(s)</strong>
                                                    <strong v-else-if="requirement.recurrence_pattern == '2'" class="pull-left" style="margin-left:10px;">month(s)</strong>
                                                    <strong v-else-if="requirement.recurrence_pattern == '3'" class="pull-left" style="margin-left:10px;">year(s)</strong>
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </template>
                            </template>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <template v-if="requirement.id">
                    <button type="button" v-if="updatingRequirement" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinnner fa-spin"></i> Updating</button>
                    <button type="button" v-else class="btn btn-default" @click="ok">Update</button>
                </template>
                <template v-else>
                    <button type="button" v-if="addingRequirement" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                    <button type="button" v-else class="btn btn-default" @click="ok">Add</button>
                </template>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {helpers,api_endpoints} from "@/utils/hooks.js"
export default {
    name:'Requirement-Detail',
    components:{
        modal,
        alert
    },
    props:{
            proposal_id:{
                type:Number,
                required: true
            },
            requirements: {
                type: Array,
                required: true
            }
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            requirement: {
                due_date: '',
                standard: true,
                recurrence: false,
                recurrence_pattern: '1',
                proposal: vm.proposal_id
            },
            addingRequirement: false,
            updatingRequirement: false,
            validation_form: null,
            type: '1',
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            validDate: false
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        due_date: {
            cache: false,
            get(){
                if (this.requirement.due_date == undefined  || this.requirement.due_date == '' || this.requirement.due_date ==  null){
                    return '';
                }
                else{
                    return this.requirement.due_date;
                }
            }
        }
    },
    watch: {
        due_date: function(){
            this.validDate = moment(this.requirement.due_date,'DD/MM/YYYY').isValid();
        },
    },
    methods:{
        initialiseRequirement: function(){
            this.requirement = {
                due_date: '',
                standard: true,
                recurrence: false,
                recurrence_pattern: '1',
                proposal: vm.proposal_id
            }
        },
        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }
        },
        cancel:function () {
            this.close()
        },
        close:function () {
            this.isModalOpen = false;
            $(this.$refs.standard_req).val(null).trigger('change');
            this.requirement = {
                standard: true,
                recurrence: false,
                due_date: '',
                recurrence_pattern: '1',
                proposal: this.proposal_id
            };
            this.errors = false;
            $('.has-error').removeClass('has-error');
            $(this.$refs.due_date).data('DateTimePicker').clear();
            //$(this.$refs.due_date).clear();
            this.validation_form.resetForm();
        },
        fetchContact: function(id){
            let vm = this;
            vm.$http.get(api_endpoints.contact(id)).then((response) => {
                vm.contact = response.body; vm.isModalOpen = true;
            },(error) => {
                console.log(error);
            } );
        },
        sendData:function(){
            let vm = this;
            vm.errors = false;
            let requirement = JSON.parse(JSON.stringify(vm.requirement));
            if (requirement.standard){
                requirement.free_requirement = '';
            }
            else{
                requirement.standard_requirement = '';
                $(this.$refs.standard_req).val(null).trigger('change');
            }
            if (!requirement.due_date){
                requirement.due_date = null;
                requirement.recurrence = false;
                delete requirement.recurrence_pattern;
                requirement.recurrence_schedule ? delete requirement.recurrence_schedule : '';
            }
            if (vm.requirement.id){
                vm.updatingRequirement = true;
                vm.$http.put(helpers.add_endpoint_json(api_endpoints.proposal_requirements,requirement.id),JSON.stringify(requirement),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.updatingRequirement = false;
                        vm.$parent.updatedRequirements();
                        vm.close();
                    },(error)=>{
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                        vm.updatingRequirement = false;
                    });
            } else {
                vm.addingRequirement = true;
                vm.$http.post(api_endpoints.proposal_requirements,JSON.stringify(requirement),{
                        emulateJSON:true,
                    }).then((response)=>{
                        vm.addingRequirement = false;
                        vm.close();
                        vm.$parent.updatedRequirements();
                    },(error)=>{
                        vm.errors = true;
                        vm.addingRequirement = false;
                        vm.errorString = helpers.apiVueResourceError(error);
                    });
                
            }
        },
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    standard_requirement:{
                        required: {
                            depends: function(el){
                                return vm.requirement.standard;
                            }
                        }
                    },
                    free_requirement:{
                        required: {
                            depends: function(el){
                                return !vm.requirement.standard;
                            }
                        }
                    },
                    schedule:{
                        required: {
                            depends: function(el){
                                return vm.requirement.recurrence;
                            }
                        }
                    }
                },
                messages: {
                    arrival:"field is required",
                    departure:"field is required",
                    campground:"field is required",
                    campsite:"field is required"
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
       },
       eventListeners:function () {
            let vm = this;
            // Initialise Date Picker
            $(vm.$refs.due_date).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.due_date).on('dp.change', function(e){
                if ($(vm.$refs.due_date).data('DateTimePicker').date()) {
                    vm.requirement.due_date =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.due_date).data('date') === "") {
                    vm.requirement.due_date = "";
                }
             });

            // Intialise select2
            $(vm.$refs.standard_req).select2({
                "theme": "bootstrap",
                allowClear: true,
                minimumInputLength: 2,
                placeholder:"Select Requirement"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.requirement.standard_requirement = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.requirement.standard_requirement = selected.val();
            });
       }
   },
   mounted:function () {
        let vm =this;
        vm.form = document.forms.requirementForm;
        vm.addFormValidations();
        this.$nextTick(()=>{
            vm.eventListeners();
        });
   }
}
</script>

<style lang="css">
</style>
