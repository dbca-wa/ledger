<template lang="html">
    <div id="bookingperiod" class="panel-group" role="tablist" aria-multiselectable="true">
        <div class="row">
            <div class="panel panel-default" style="overflow:auto;">
                <div class="panel-heading" role="tab">
                    <h4 class="panel-title">
                        <h3 style="display:inline;">Booking Periods</h3>
                    </h4>
                </div>
                <div id="details-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="details-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <div class="col-md-2">
                                    <button type="button" class="btn btn-primary" style="width:100%;" @click.prevent="newOption()" style='display: none'>Add New Option</button>
                                </div>
                                <div class="col-md-8"/>
                                <div class="col-md-2">
                                    <a class="btn btn-primary" style="width:100%;" iiiclick.prevent="newPeriod()" href="/dashboard/bookingperiods/create" >Add New Group</a>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-2">
                                    <button type="button" class="btn btn-primary" style="width:100%;" @click.prevent="editOption()"  style='display: none'>Edit Option</button>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-2">
                                    <button type="button" class="btn btn-danger" style="width:100%;" @click.prevent="deleteOption()"  style='display: none'>Delete Option</button>
                                </div>
                            </div>
                            <div class="row">
                                <datatable ref="optionsTable" :dtHeaders="dt_headers" :dtOptions="dt_options" id="op_table"></datatable>
                            </div>
                        </div>
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
                        <div class="col-md-3">
                            <input type="text" style="width:100%;" maxlength="15" v-model="optionsName" v-on:blur="validateOptionsName()" class="form-control"/>
                        </div>
                        <div class="col-md-2">
                            <label>Description (Admin only)</label>
                        </div>
                        <div class="col-md-6">
                            <input type="text" style="width:100%;" v-model="optionsDescription" v-on:blur="validateOptionsDescription()" class="form-control"/>
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
                                <option v-for="res in booking_period_options" :value="res.id">{{res.option_description}}</option>
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
                                <option v-for="res in booking_period_options" :value="res.id">{{res.option_description}}</option>
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
            <div class="row">
                <div class="col-md-12" v-if="errorMsgDel">
                    <div class="errorMsgDiv" id="modalErrorDelete">{{ errorMsgDel }}</div>
                </div>
            </div>
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
            optionsDescription: '',
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
            errorMsgDel: '',
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
//                            var column = "<a href='#' class='editPeriod' data-rate=\"__RATE__\" >" + full.id + "</a>";
                            var column = "" + full.id + "";
//                            column = column.replace(/__RATE__/g, full.id);
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
                            var names = "<td>";
                            for(var i = 0; i < full.booking_period.length; i++){
                                names += full.booking_period[i].period_name + " (" + full.booking_period[i].option_description + ")<br/>";
                            }
                            names += "</td>";
                            return names;
                        }
                        return '';
                    }
                }, {
                    mRender: function(data, type, full) {
                        var id = full.id;
//                        var column = "<td ><a href='#' class='editPeriod' data-rate=\"__RATE__\" >Edit</a><br/>"
                        var column = "<td ><a href='/dashboard/bookingperiods/"+id+"/edit' >Edit</a><br/>";
                        column += "<a href='/dashboard/bookingperiods/"+id+"/view' >View Periods</a><br/>";
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
    watch: {
        booking_period_options: function(val){
            let vm = this;
            setTimeout( function(){
                //Because this is using the custom adapter (see addEventListeners for more info)
                //the text value must be assigned in order for the name to display in the dropdown.
                for(var i = 0; i < vm.booking_period_options.length; i++){
                    vm.booking_period_options[i].text = vm.booking_period_options[i].option_description;
                }
                //Then trigger the change of data on all 3 dropdowns.
                $(vm.$refs.periodOptions).data('select2').dataAdapter.updateOptions(vm.booking_period_options);
                $(vm.$refs.periodOptionsDelete).data('select2').dataAdapter.updateOptions(vm.booking_period_options);
                $(vm.$refs.periodOptionsModal).data('select2').dataAdapter.updateOptions(vm.booking_period_options);
            }, 200);
        }
    },
    methods: {
        fetchBookingPeriodOptions: function(){
            let vm = this;
            vm.$store.dispatch("fetchBookingPeriodOptions");
        },
        setPeriodEditorFields: function(){
            let vm = this;
            var url = api_endpoints.booking_period_edit(vm.loadId);
            //Loading and populating the fields for the period user is editing.
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                method: "GET",
                url: url,
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
            vm.optionsDescription = res.option_description;
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
            vm.optionsDescription = '';
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
            vm.errorMsgDel = null;
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
        validateOptionsDescription: function(){
            //Name field must be filled in. Essentially required but offers use of
            //the bootstrap alert error message.
            let vm = this;
            var errorString = "Please enter a description for admin use.";
            if(!vm.optionsDescription || vm.optionsDescription == ""){
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
            var url = api_endpoints.booking_period_options_edit(vm.deletingId);
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                method: "DELETE",
                url: url,
                xhrFields: { withCredentials:true },
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                success: function(msg){
                    vm.fetchBookingPeriodOptions();
                    vm.closeDeleteModal();
                    vm.deletingId = "";
                },
                error: function(resp){
                    if(resp.status == 500 && resp.responseJSON == "Error in use."){
                        //Need to display error message.
                        vm.errorMsgDelete = "This option is currently used in a period. Please remove before deleting."
                    } else {
                        vm.errorMsgDelete = "There was an error, please try again later or speak with a super user."
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
                    'option_description': vm.optionsDescription,
                    'small_price': vm.optionsSmallPrice,
                    'medium_price': vm.optionsMediumPrice,
                    'large_price': vm.optionsLargePrice,
                    'start_time': vm.optionsStartTime,
                    'finish_time': vm.optionsFinishTime
                }
                
                if(vm.editing){
                    var url = api_endpoints.booking_period_options_edit(vm.editingId);
                    var method = "PUT";
                } else {
                    var url = api_endpoints.booking_period_options;
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
                        //On success; refresh the table, get the new options, close the modal
                        //and clear any data in it.
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
            var url = api_endpoints.booking_period_edit(vm.delId);
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                method: "DELETE",
                url: url,
                xhrFields: { withCredentials:true },
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                success: function(msg){
                    //On success; refresh the table, get the new options and close the modal.
                    vm.fetchBookingPeriodOptions();
                    vm.$refs.optionsTable.vmDataTable.ajax.reload();
                    vm.closeDelConfirmModal();
                    vm.delId = "";
                },
                error: function(resp){
                    //Need to display error message.
                    if(resp.status == 500 && resp.responseText.slice(0,14) == "ProtectedError"){
                        vm.errorMsgDel = "This period is currently used for a mooring site rate. Please remove before deleting."
                    } else {
                        vm.errorMsgDel = "There was an error, please try again later or speak with a super user."
                    }
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
            
            if(vm.editing){
                var url = api_endpoints.booking_period_edit(vm.loadId);
                var method = "PUT";
            } else {
                var url = api_endpoints.booking_period;
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
            //This is a custom adapter that allows for dynamic refreshing of data.
            //Select 4.0.3 does not currently have a way of updating data properly.
            //Without using this we can add a new option and that would appear,
            //however if we change the name of a period option it would still have
            //the old text in the option in the dropdown in the edit selector (for options)
            //or the delete selector (for options). The multi-select seems to work, 
            //populating the correct word and the options are correct. However all
            //3 need to be updated.
            $.fn.select2.amd.define('select2/data/customAdapter',
                ['select2/data/array', 'select2/utils'],
                function(ArrayAdapter, Utils){
                    function CustomDataAdapter($element, options){
                        CustomDataAdapter.__super__.constructor.call(this, $element, options);
                    }
                    Utils.Extend(CustomDataAdapter, ArrayAdapter);
                    CustomDataAdapter.prototype.updateOptions = function (data) {
                        this.$element.find('option').remove(); //remove all options
                        this.addOptions(this.convertToOptions(data));
                    }
                    return CustomDataAdapter;
                }
            );
            var customAdapter = $.fn.select2.amd.require('select2/data/customAdapter'); //For use in select2 initialisation.

            //Launches the edit period modal from the datatable. This can be from clicking
            //the ID or the edit under actions.
            vm.$refs.optionsTable.vmDataTable.on('click','.editPeriod', function(e) {
                e.preventDefault();
                vm.loadId = e.currentTarget.dataset.rate;
                if(vm.loadId){
                    vm.setPeriodEditorFields();
                    vm.editing = true;
                    $('#editPeriodModal').modal('show');
                }
            });
            //Launches the delete confirm modal from the datatable.
            vm.$refs.optionsTable.vmDataTable.on('click','.deletePeriod', function(e) {
                e.preventDefault();
                vm.delId = e.currentTarget.dataset.rate;
                if(vm.delId){
                    var url = api_endpoints.booking_period_edit(vm.delId);
                    $.ajax({
                        beforeSend: function(xhrObj) {
                            xhrObj.setRequestHeader("Content-Type", "application/json");
                            xhrObj.setRequestHeader("Accept", "application/json");
                        },
                        method: "GET",
                        url: url,
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

            // Period options on the edit or new period modal.
            $(vm.$refs.periodOptions).select2({
                "theme": "bootstrap",
                dataAdapter: customAdapter,
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
                dataAdapter: customAdapter,
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
                dataAdapter: customAdapter,
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
    display: block;
    overflow: auto;
    border-style:solid;
    border-width:2px;
    border-radius: 10px;
    padding:10px;
    font-size:12pt;
    margin-bottom:20px;
}
</style>
