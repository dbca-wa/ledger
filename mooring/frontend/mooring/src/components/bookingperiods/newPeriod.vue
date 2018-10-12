<template lang="html">
    <div id="bookingperiod">
        <div class="container">
            <div class="well" style="overflow:auto;">
                <div style="text-align:center">
                    <h1>Booking Periods</h1>
                </div>
                <div class="col-lg-12">
                    <div class="row">
                        <div class="col-md-3">
                            <button type="button" class="btn btn-primary" @click.prevent="newOption()">Add New Option</button>
                        </div>
                        <div class="col-md-6"/>
                        <div class="col-md-3">
                            <button type="button" class="btn btn-primary" @click.prevent="newPeriod()">Add New Period</button>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <button type="button" class="btn btn-primary" @click.prevent="editOption()">Edit Option</button>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <button type="button" class="btn btn-danger" @click.prevent="deleteOption()">Delete Option</button>
                        </div>
                    </div>
                    <div class="row">
                        <datatable ref="optionsTable" :dtHeaders="dt_headers" :dtOptions="dt_options" id="op_table"></datatable>
                    </div>
                </div>
            </div>
        </div>
        <modal :large="true"  @cancel="closeEditOptionModal()" class="modal fade" data-backdrop="true" :force="true" id="editOptionModal">
            <h4 slot="title">Add New Period Option</h4>
            <div class="row" height="500px">
                <div class="col-lg-12">
                    <div class="row">
                        <div class="col-md-12" v-if="errorMsg">
                            <div class="errorMsgDiv" id="modalError">{{ errorMsg }}</div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-1">
                            <label>Name</label>
                        </div>
                        <div class="col-md-5">
                            <input type="text" style="width:100%;" v-model="optionsName" v-on:blur="validateOptionsName()" class="form-control"/>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-1">
                            <label>Small Price</label>
                        </div>
                        <div class="col-md-3">
                            <div class="input-group">
                                <span class="input-group-addon">$</span>
                                <input type="number" v-model="optionsSmallPrice" v-on:blur="validateOptionsPrices()" min="0.00" step="0.01" placeholder="9.99" class="form-control currency"/>
                            </div>
                        </div>
                        <div class="col-md-1">
                            <label>Medium Price</label>
                        </div>
                        <div class="col-md-3">
                            <div class="input-group">
                                <span class="input-group-addon">$</span>
                                <input type="number" v-model="optionsMediumPrice" v-on:blur="validateOptionsPrices()" min="0.00" step="0.01" placeholder="19.99" class="form-control currency"/>
                            </div>
                        </div>
                        <div class="col-md-1">
                            <label>Large Price</label>
                        </div>
                        <div class="col-md-3">
                            <div class="input-group">
                                <span class="input-group-addon">$</span>
                                <input type="number" v-model="optionsLargePrice" v-on:blur="validateOptionsPrices()" min="0.00" step="0.01" placeholder="29.99" class="form-control currency"/>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-1">
                            <label>Start Time</label>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <div class="input-group date" id="startTime">
                                    <input type='text' class="form-control" placeholder="10:00" @blur="validateOptionsTimes()" v-model="optionsStartTime"/>
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-time"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-1">
                            <label>End Time</label>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <div class="input-group date" id="endTime">
                                    <input type='text' class="form-control" placeholder="18:00" @blur="validateOptionsTimes()" v-model="optionsFinishTime"/>
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-time"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-on:click="closeEditOptionModal()" class="btn btn-default" style="width:180px;font-weight:bold;">Close</button>
                <button type="button" v-on:click="saveOption()" class="btn btn-success" style="width:180px;font-weight:bold;">Save</button>
            </div>
        </modal>
        <modal :large="true"  @cancel="closeSelectorModal()" class="modal fade" data-backdrop="true" :force="true" id="selectorModal">
            <h4 slot="title">Select One Period Option To Edit</h4>
            <div class="row" height="500px">
                <div class="col-lg-12">
                    <div class="row">
                        <div class="col-md-3"/>
                        <div class="col-md-6" style="overflow:visible;">
                            <label>Period Option</label>
                            <select name="periodOptionsModal" id="periodOptionsModal" ref="periodOptionsModal" style="width:100%;">
                                <option v-for="res in booking_period_options" :value="res.id">{{res.period_name}}</option>
                            </select>
                        </div>
                        <div class="col-md-3"/>
                    </div>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-on:click="closeSelectorModal()" class="btn btn-default" style="width:180px;font-weight:bold;">Close</button>
                <button type="button" v-on:click="editOption()" class="btn btn-success" style="width:180px;font-weight:bold;">Edit</button>
            </div>
        </modal>
        <modal :large="true"  @cancel="closeDeleteModal()" class="modal fade" data-backdrop="true" :force="true" id="deleteModal">
            <h4 slot="title">Select Period Option To Delete</h4>
            <div class="row" height="500px">
                <div class="col-lg-12">
                    <div class="row">
                        <div class="col-md-12" v-if="errorMsgDelete">
                            <div class="errorMsgDiv" id="modalErrorDelete">{{ errorMsgDelete }}</div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3"/>
                        <div class="col-md-6" style="overflow:visible;">
                            <label>Period</label>
                            <select name="periodOptionsDelete" id="periodOptionsDelete" ref="periodOptionsDelete" style="width:100%;">
                                <option v-for="res in booking_period_options" :value="res.id">{{res.period_name}}</option>
                            </select>
                        </div>
                        <div class="col-md-3"/>
                    </div>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-on:click="closeDeleteModal()" class="btn btn-default" style="width:180px;font-weight:bold;">Close</button>
                <button type="button" v-on:click="deleteOption()" class="btn btn-danger" style="width:180px;font-weight:bold;">Delete</button>
            </div>
        </modal>
        <modal :large="true"  @cancel="closeEditPeriodModal()" class="modal fade" data-backdrop="true" :force="true" id="editPeriodModal">
            <h4 slot="title">Editing {{ loadName }}</h4>
            <div class="row" height="500px">
                <div class="col-lg-12">
                    <div class="row">
                        <div class="col-md-3"/>
                        <div class="col-md-6">
                            <label>Name</label>
                            <input type="text" v-model="loadName" class="form-control" style="width:100%"/>
                        </div>
                        <div class="col-md-3"/>
                    </div>
                    <div class="row">
                        <div class="col-md-3"/>
                        <div class="col-md-6" style="overflow:visible;">
                            <label>Period</label>
                            <select name="periodOptions" id="periodOptions" ref="periodOptions" style="width:100%;" multiple>
                                <option v-for="res in booking_period_options" :value="res.id">{{res.period_name}}</option>
                            </select>
                        </div>
                        <div class="col-md-3"/>
                    </div>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-on:click="closeEditPeriodModal()" class="btn btn-default" style="width:180px;font-weight:bold;">Close</button>
                <button type="button" v-on:click="savePeriod()" class="btn btn-success" style="width:180px;font-weight:bold;">Save</button>
            </div>
        </modal>
        <modal :large="true" @cancel="closeDelConfirmModal()" class="modal fade" data-backdrop="true" :force="true" id="deleteConfirmModal">
            <h4 slot="title">Delete {{ delName }}</h4>
            <div class="row" style="text-align:center;">
                <p>Are you sure you would like to delete {{delName}}?
            </div>
            <div slot="footer">
                <button type="button" v-on:click="closeDelConfirmModal()" class="btn btn-default" style="width:180px;font-weight:bold;">Close</button>
                <button type="button" v-on:click="deletePeriod()" class="btn btn-danger" style="width:180px;font-weight:bold;">Delete</button>
            </div>
        </modal>
    </div>
</template>

<script>
import datatable from '../utils/datatable.vue'
import {
    $,
    api_endpoints,
    select2,
    datetimepicker,
    helpers
    } from '../../hooks.js'
import modal from '../utils/bootstrap-modal.vue'
import { mapGetters } from 'vuex'

export default {
    name: "bookingperiod",
    components:{
        datatable,
        modal,
    },
    data: function() {
        return {
            periodOptions: '',
            periodOptionsModal: '',
            periodOptionsDelete: '',
            optionsName: '',
            optionsSmallPrice: '',
            optionsMediumPrice: '',
            optionsLargePrice: '',
            optionsStartTime: '',
            optionsFinishTime: '',
            editingId: '',
            deletingId: '',
            editing: false,
            errorMsg: "",
            errorMsgDelete: '',
            loadId: '',
            loadName: '',
            delId: '',
            delName: '',
            selectedOptions: '',
            dt_headers: ['ID', 'Period Name', 'Options', 'Action'],
            dt_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                order: [],
                ajax: {
                    url: api_endpoints.booking_period,
                    dataSrc: ''
                },
                columns: [{
                    data: 'id',
                    mRender: function(data, type, full){
                        if(data){
                            var column = "<a href='#' class='editPeriod' data-rate=\"__RATE__\" >" + full.id + "</a>";
                            column = column.replace(/__RATE__/g, full.id);
                            return column;
                        } else {
                            return '';
                        }
                    }
                }, {
                    data: 'name',

                }, {
                    data: 'booking_period',
                    mRender: function(data, type, full) {
                        if (data){
                            var names = "";
                            for(var i = 0; i < full.booking_period.length; i++){
                                names += full.booking_period[i].period_name + ", ";
                            }
                            return names;
                        }
                        return '';
                    }
                }, {
                    mRender: function(data, type, full) {
                        var id = full.id;
                        var column = "<td ><a href='#' class='editPeriod' data-rate=\"__RATE__\" >Edit</a><br/>"
                        column += "<a href='#' class='deletePeriod' data-rate=\"__RATE__\" >Delete</a></td>";
                        column = column.replace(/__RATE__/g, id);
                        return column;
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            }
        }
    },
    computed: {
        ...mapGetters([
          'booking_period_options'
        ]),
    },
    methods: {
        fetchBookingPeriodOptions: function(){
            let vm = this;
            vm.$store.dispatch("fetchBookingPeriodOptions");
        },
        setPeriodEditorFields: function(){
            let vm = this;
            var url = api_endpoints.booking_period;
            var urlGet = url.slice(0, -5);
            urlGet += "/" + vm.loadId + "/";
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                method: "GET",
                url: urlGet,
                xhrFields: { withCredentials:true },
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                success: function(data){
                    vm.loadName = data.name;
                    vm.selectedOptions = [];
                    var selectOptions = $('#periodOptions');
                    for (var i = 0; i < data.booking_period.length; i++){
                        vm.selectedOptions.push(data.booking_period[i].id);
                    }
                    selectOptions.val(vm.selectedOptions).trigger('change');
                    vm.periodOptions = vm.selectedOptions;
                },
                error: function(resp){
                }
            });
        },
        setOptionsEditorFields: function(pid){
            //First find the corresponding period option from the list we got from
            //mapgetters. array.find() doesn't seem to work here, may need to look
            //at a more efficient method.
            //Once found set the variables then display the editor modal.
            let vm = this;
            for(var i = 0; i < vm.booking_period_options.length; i++){
                if(vm.booking_period_options[i].id == pid){
                    var res = vm.booking_period_options[i];
                }
            }
            vm.optionsName = res.period_name;
            vm.optionsSmallPrice = res.small_price;
            vm.optionsMediumPrice = res.medium_price;
            vm.optionsLargePrice = res.large_price;
            vm.optionsStartTime = res.start_time.substr(0,5);
            vm.optionsFinishTime = res.finish_time.substr(0,5);
            vm.editing = true;
            vm.editingId = pid;
            $('#editOptionModal').modal('show');
        },
        clearEdit: function(){
            //Destroys any data in the edit period option modal, used after save.
            let vm = this;
            vm.optionsName = '';
            vm.optionsSmallPrice = '';
            vm.optionsMediumPrice = '';
            vm.optionsLargePrice = '';
            vm.optionsStartTime = '';
            vm.optionsFinishTime = '';
            vm.editing = false;
            vm.editingId = '';
        },
        newPeriod: function(){
            let vm = this;
            vm.editing = false;
            $('#editPeriodModal').modal('show');
        },
        newOption: function(){
            //New period option modal, no pre-fetch to populate.
            let vm = this;
            vm.clearEdit();
            vm.editing = false;
            $('#editOptionModal').modal('show');
        },
        editOption: function(){
            let vm = this;
            if(vm.periodOptionsModal) {
                //Can launch the edit modal, close the selector but
                //keep the periods drop down in the main screen disabled.
                var pid = vm.periodOptionsModal;
                vm.setOptionsEditorFields(pid);
                vm.closeSelectorModal();
            } else {
                //Launch into a selector modal.
                $('#periodOptionsModal').val('').trigger('change');
                $('#selectorModal').modal('show');
            }
        },
        deleteOption: function(){
            let vm = this;
            if(vm.periodOptionsDelete!=""){
                vm.deletingId = vm.periodOptionsDelete;
                vm.deleteOptionData();
            } else {
                $('#periodOptionsDelete').val('').trigger('change');
                $('#deleteModal').modal('show');
            }
        },
        closeDelConfirmModal: function(){
            //Confirm delete period modal.
            let vm = this;
            $('#deleteConfirmModal').modal('hide');
            vm.delName = null;
            vm.delId = null;
        },
        closeEditPeriodModal: function(){
            let vm = this;
            $('#editPeriodModal').modal('hide');
            $('#periodOptions').val('').trigger('change');
            vm.loadName = null;
            vm.loadId = null;
            vm.periodOptions = null;
            vm.selectedOptions = null;
        },
        closeEditOptionModal: function(){
            let vm = this;
            $('#editOptionModal').modal('hide');
        },
        closeSelectorModal: function(){
            //When closing the selector modal, the periodoptionsmodal variable must be destroyed.
            //That way if editing a second, the selector is reset to default appearence.
            let vm = this;
            vm.periodOptionsModal = null;
            $('#periodOptionsModal').val('').trigger('change');
            $('#selectorModal').modal('hide');
        },
        closeDeleteModal: function(){
            let vm = this;
            $('#deleteModal').modal('hide');
            vm.periodOptionsDelete = '';
            $('#periodOptionsDelete').val('').trigger('change');
        },
        validateOptionsName: function(){
            //Name field must be filled in. Essentially required but offers use of
            //the bootstrap alert error message.
            let vm = this;
            var errorString = "Please enter a name.";
            if(!vm.optionsName || vm.optionsName == ""){
                vm.errorMsg = errorString;
                return true;
            } else {
                if(vm.errorMsg == errorString){
                    vm.errorMsg = null;
                }
                return false;
            }
        },
        validateOptionsPrices: function(){
            //Prices must be filled in. Essentially required but offers use of the
            //bootstrap alert error message.
            let vm = this;
            var errorString = "Please enter a price for all 3 options. If you do not want a price, please specify 0.";
            if(!vm.optionsSmallPrice || !vm.optionsMediumPrice || !vm.optionsLargePrice || vm.optionsSmallPrice == "" || vm.optionsMediumPrice == "" || vm.optionsLargePrice == ""){
                vm.errorMsg = errorString;
                return true;
            } else {
                if(vm.errorMsg == errorString){
                    vm.errorMsg = null;
                }
                return false;
            }
        },
        validateOptionsTimes: function(){
            //Times must be filled out, and must be in format HH:MM.
            let vm = this;
            var errorString = "Both time fields must be in format HH:MM.";
            if(!vm.optionsStartTime || !vm.optionsFinishTime || vm.optionsStartTime == "" || vm.optionsFinishTime == ""){
                vm.errorMsg = errorString;
                return true;
            } else {
                if(vm.optionsStartTime.substr(2,1) !== ":" || vm.optionsFinishTime.substr(2,1) !== ":"){
                    if(int(vm.optionsStartTime) < 24){
                        vm.optionsStartTime += ":00";
                    }
                    if(int(vm.optionsFinishTime) < 24){
                        vm.optionsFinishTime += ":00";
                    }
                }
                if(!vm.optionsStartTime.match(/^\d\d:\d\d/) || !vm.optionsFinishTime.match(/^\d\d:\d\d/)){
                    vm.errorMsg = errorString;
                    return true;
                } else if(vm.errorMsg == errorString){
                    vm.errorMsg = null;
                }
                return false;
            }
        },
        deleteOptionData: function(){
            let vm = this;
            var url = api_endpoints.booking_period_options;
            var urlDelete = url.slice(0, -5);
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                method: "DELETE",
                url: urlDelete + "/" + vm.deletingId + "/",
                xhrFields: { withCredentials:true },
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                success: function(msg){
                    vm.fetchBookingPeriodOptions();
                    vm.closeDeleteModal();
                    vm.deletingId = "";
                },
                error: function(resp){
                    if(resp.status == 405){
                        //Need to display error message.
                        vm.errorMsgDelete = "This option is currently used in a period. Please remove before deleting."
                    }
                }
            });
        },
        saveOption: function(){
            let vm = this;
            //Begin with validation
            var iserror = false;
            iserror = vm.validateOptionsName();
            iserror = vm.validateOptionsPrices();
            iserror = vm.validateOptionsTimes();

            if(!iserror){
                //If valid, get the data from the model fields into a dictionary.
                var data = {
                    'period_name': vm.optionsName,
                    'small_price': vm.optionsSmallPrice,
                    'medium_price': vm.optionsMediumPrice,
                    'large_price': vm.optionsLargePrice,
                    'start_time': vm.optionsStartTime,
                    'finish_time': vm.optionsFinishTime
                }
                var url = api_endpoints.booking_period_options;
                if(vm.editing){
                    url = url.slice(0, -5) + "/" + vm.editingId + "/";
                    var method = "PUT";
                } else {
                    var method = "POST";
                }
                $.ajax({
                    beforeSend: function(xhrObj) {
                        xhrObj.setRequestHeader("Content-Type", "application/json");
                        xhrObj.setRequestHeader("Accept", "application/json");
                    },
                    method: method,
                    url: url,
                    xhrFields: { withCredentials:true },
                    data: JSON.stringify(data),
                    headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                    success: function(msg){
                        vm.$refs.optionsTable.vmDataTable.ajax.reload();
                        vm.fetchBookingPeriodOptions();
                        vm.closeEditOptionModal();
                        vm.clearEdit();
                    },
                    error: function(resp){
                    }
                });
            }
        },
        deletePeriod: function(){
            let vm = this;
            var url = api_endpoints.booking_period;
            var urlDelete = url.slice(0, -5);
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                method: "DELETE",
                url: urlDelete + "/" + vm.delId + "/",
                xhrFields: { withCredentials:true },
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                success: function(msg){
                    vm.fetchBookingPeriodOptions();
                    vm.$refs.optionsTable.vmDataTable.ajax.reload();
                    vm.closeDelConfirmModal();
                    vm.delId = "";
                },
                error: function(resp){
                    
                }
            });
        },
        savePeriod: function(){
            //Save new or update existing booking period.
            let vm = this;
            var data = {
                'name': vm.loadName,
                'booking_period': vm.periodOptions
            }
            var url = api_endpoints.booking_period;
            if(vm.editing){
                url = url.slice(0, -5) + "/" + vm.loadId + "/";
                var method = "PUT";
            } else {
                var method = "POST"
            }   
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                url: url,
                method: method,
                xhrFields: { withCredentials:true },
                data: JSON.stringify(data),
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                success: function(msg){
                    vm.closeEditPeriodModal();
                    vm.$refs.optionsTable.vmDataTable.ajax.reload();
                },
                error: function(resp){
                }
            });
        },
        addEventListeners: function(){
            let vm = this;
            vm.$refs.optionsTable.vmDataTable.on('click','.editPeriod', function(e) {
                e.preventDefault();
                vm.loadId = e.currentTarget.dataset.rate;
                if(vm.loadId){
                    vm.setPeriodEditorFields();
                    vm.editing = true;
                    $('#editPeriodModal').modal('show');
                }
            });
            vm.$refs.optionsTable.vmDataTable.on('click','.deletePeriod', function(e) {
                e.preventDefault();
                vm.delId = e.currentTarget.dataset.rate;
                if(vm.delId){
                    var url = api_endpoints.booking_period;
                    var urlGet = url.slice(0, -5);
                    urlGet += "/" + vm.delId + "/";
                    $.ajax({
                        beforeSend: function(xhrObj) {
                            xhrObj.setRequestHeader("Content-Type", "application/json");
                            xhrObj.setRequestHeader("Accept", "application/json");
                        },
                        method: "GET",
                        url: urlGet,
                        xhrFields: { withCredentials:true },
                        headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                        success: function(data){
                            vm.delName = data.name;
                            $('#deleteConfirmModal').modal('show');
                        },
                        error: function(resp){
                        }
                    });
                }
            });

            /* Period options Selector*/
            $(vm.$refs.periodOptions).select2({
                "theme": "bootstrap"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.periodOptions = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                if(selected.val().length > 0){

                    vm.periodOptions = selected.val();
                } else {
                    vm.periodOptions = "";
                }
            });

            //============Modal items==============
            //Start time datepicker set to format for time only.
            var startpicker = $('#startTime').datetimepicker({
                format: 'HH:mm',
            });
            startpicker.on('dp.change', function(e){
                vm.optionsStartTime = startpicker.data('DateTimePicker').date().format('HH:mm');
            });
            //End time datepicker, same as above.
            var endpicker = $('#endTime').datetimepicker({
                format: 'HH:mm',
            });
            endpicker.on('dp.change', function(e){
                vm.optionsFinishTime = endpicker.data('DateTimePicker').date().format('HH:mm');
            });

            //Period options in the selector modal for editing.
            $(vm.$refs.periodOptionsModal).select2({
                "theme": "bootstrap",
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.periodOptionsModal = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.periodOptionsModal = selected.val();
            });
            //Period options for the delete modal.
            $(vm.$refs.periodOptionsDelete).select2({
                "theme": "bootstrap",
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.periodOptionsDelete = selected.val();
                vm.errorMsgDelete = "";
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.periodOptionsDelete = selected.val();
            });
        },
    },
    created: function(){
        let vm = this;
    },
    mounted: function(){
        let vm = this;
        vm.fetchBookingPeriodOptions();
        vm.addEventListeners();
        vm.$refs.optionsTable.vmDataTable.order(0, "asc");
        
    }
}

</script>
<style>
.errorMsgDiv{
    background-color: #F2DEDE;
    color: #C78382;
    border-color: #EBCCD1;
    height:50px;
    border-style:solid;
    border-width:2px;
    border-radius: 10px;
    padding:10px;
    font-size:12pt;
    margin-bottom:20px;
}
/* .select2-container{
    
    z-index: 0;
} */
.select2-container--open{
    /* Very important for asthetics, without this the periods selector in the 
    main screen will be usable when not disabled behind the selector modal
    dropdown. When is it disabled this setting stops the not-allowed cursor
    appearing. */
    z-index: 9999999;
}
</style>
