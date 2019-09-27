<template lang="html" id="booking-dashboard">
<div class="panel-group" id="bookings-accordion" role="tablist" aria-multiselectable="true">
    <div class="row" v-show="!isLoading">
        <div class="panel panel-default" style="overflow:visible;">
            <div class="panel-heading" role="tab" id="bookings-heading">
                <h4 class="panel-title">
                    <a role="button" data-toggle="collapse" href="#bookings-collapse"
                    aria-expanded="false" aria-controls="bookings-collapse" style="outline:none;">
                        <div>
                            <h3 style="display:inline;">Bookings</h3>
                            <span id="collapse_bookings_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                        </div>
                    </a>
                </h4>
            </div>
            <div id="bookings-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="bookings-heading">
                <div class="panel-body">
                    <div class="row">
                        <div class="col-md-12">
                            <button v-if="!exportingCSV" type="button" class="btn btn-default pull-right" id="print-btn" @click="print()">
                                <i class="fa fa-file-excel-o" aria-hidden="true"></i> Export to CSV
                            </button>
                            <button v-else type="button" class="btn btn-default pull-right" disabled>
                                <i class="fa fa-circle-o-notch fa-spin" aria-hidden="true"></i> Exporting to CSV
                            </button>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-group">
                            <label for="">Mooring</label>
                            <select v-show="isLoading" class="form-control" >
                                <option value="">Loading...</option>
                            </select>
                            <select ref="campgroundSelector" v-if="!isLoading" class="form-control" v-model="filterCampground" id="filterCampground">
                                <option value="All">All</option>
                                <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                            </select>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                            <label for="">Region</label>
                            <select v-show="isLoading" class="form-control" name="">
                                    <option value="">Loading...</option>
                            </select>
                            <select ref="regionSelector" v-if="!isLoading" class="form-control" v-model="filterRegion" id="filterRegion">
                                    <option value="All">All</option>
                                    <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                            </select>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                            <label for="">Cancelled</label>
                                <select class="form-control" v-model="filterCanceled" id="filterCanceled">
                                    <option value="True">Yes</option>
                                    <option value="False">No</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row" style="margin-bottom:10px;">
                        <div class="col-md-4">
                            <label for="">Date From</label>
                            <div class="input-group date" id="booking-date-from">
                            <input type="text" class="form-control"  placeholder="DD/MM/YYYY" v-model="filterDateFrom">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <label for="">Date To</label>
                            <div class="input-group date" id="booking-date-to">
                            <input type="text" class="form-control"  placeholder="DD/MM/YYYY" v-model="filterDateTo">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <label for="">Keyword</label>
                            <div class="form-group" id="booking-keyword">
                            <input type="text" class="form-control"  placeholder="" v-model="filterBookingKeyword" name='BookingKeyword' id="BookingKeyword">
                            </div>
                        </div>


                        <div style='display: none' class="col-md-4" iv-if="filterCanceled == 'True'">
                            <div class="form-group">
                            <label for="">Refund Status</label>
                            <select class="form-control" v-model="filterRefundStatus" id="filterRefundStatus">
                                    <option value="All">All</option>
                                    <option value="Refunded">Refunded</option>
                                    <option value="Partially Refunded">Partially Refunded</option>
                                    <option value="Not Refunded">Not Refunded</option>
                            </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="bookings_table" id="bookings-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders"></datatable>
                        </div>
                    </div>
                    <changebooking ref="changebooking" :booking_id="selected_booking" :campgrounds="campgrounds"/>
                    <bookingHistory ref="bookingHistory" :booking_id="selected_booking" />
                </div>
            </div>
        <loader :isLoading="isLoading" >{{loading.join(' , ')}}</loader>
        </div>
    </div>

    <div class="row" v-show="!isLoading2">
        <div class="panel panel-default" style="overflow:visible;margin-top:20px;">
            <div class="panel-heading" role="tab" id="admissions-heading">
                <h4 class="panel-title">
                    <a role="button" data-toggle="collapse" href="#admissions-collapse"
                    aria-expanded="false" aria-controls="admissions-collapse" style="outline:none;">
                        <div>
                            <h3 style="display:inline;">Admission Fee Payments</h3>
                            <span id="collapse_admissions_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                        </div>
                    </a>
                </h4>
            </div>
            <div id="admissions-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="admissions-heading">
                <div class="panel-body">
                    <div class="row">
                        <div class="col-md-12">
                            <button v-if="!exportingCSV2" type="button" class="btn btn-default pull-right" id="print-btn" @click="print2()">
                                <i class="fa fa-file-excel-o" aria-hidden="true"></i> Export to CSV
                            </button>
                            <button v-else type="button" class="btn btn-default pull-right" disabled>
                                <i class="fa fa-circle-o-notch fa-spin" aria-hidden="true"></i> Exporting to CSV
                            </button>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Date From</label>
                            <div class="input-group date" id="admission-date-from">
                            <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateFrom2">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Date To</label>
                            <div class="input-group date" id="admission-date-to">
                            <input type="text" class="form-control"  placeholder="DD/MM/YYYY" v-model="filterDateTo2">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                            <label for="">Cancelled</label>
                            <select class="form-control" v-model="filterCanceled2" id="filterCanceled2">
                                    <option value="True">Yes</option>
                                    <option value="False">No</option>
                            </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Keyword</label>
                            <div class="form-group" id="booking-keyword">
                            <input type="text" class="form-control"  placeholder="" v-model="filterAdmissionKeyword" name='AdmissionKeyword' id="AdmissionKeyword">
                            </div>
                        </div>


                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="admissions_bookings_table" id="admissions-bookings-table" :dtOptions="dtOptions2" :dtHeaders="dtHeaders2"></datatable>
                        </div>
                    </div>
                </div>
            </div>
            <loader :isLoading2="isLoading2" >{{loading2.join(' , ')}}</loader>
        </div>
    </div>
</div>
</template>


<script>
// Variabled ending with a 2 (except select2) are reused for the admissions fee payment table.
import {$,
        bus,
        datetimepicker,
        api_endpoints,
        helpers,
        Moment,
        swal,
//        select2
        } from "../../hooks.js"
import loader from "../utils/loader.vue"
import datatable from '../utils/datatable.vue'
import changebooking from "./changebooking.vue"
import bookingHistory from "./history.vue"
import modal from '../utils/bootstrap-modal.vue'
import { mapGetters } from 'vuex'
export default {
    name:'booking-dashboard',
    components:{
        datatable,
        loader,
        changebooking,
        modal,
        bookingHistory
    },
    data:function () {
        let vm =this;
        return {
            exportingCSV: false,
            exportingCSV2: false,
            payment_officer: false,
            dtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                fnDrawCallback: function(oSettings, json){
                    if(vm.payment_officer){
                        vm.$refs.bookings_table.vmDataTable.rows().every(function(){
                            var rowdata = this.data();
                            rowdata['payment_visible'] = true;
                            this.data(rowdata);
                        });
                    }
                },
                serverSide:true,
                processing:true,
                searchDelay: 800,
                searching: false,
                ajax: {
                    "url": api_endpoints.bookings,
                    "dataSrc": 'results',
                    data :function (d) {
                        if (vm.filterDateFrom) {
                            d.arrival = vm.filterDateFrom;
                        }
                        if (vm.filterDateTo) {
                            d.departure = vm.filterDateTo;
                        }
                        if (vm.filterCampground != "All") {
                            d.campground = vm.filterCampground;
                        }
                        if (vm.filterRegion != "All") {
                            d.region = vm.filterRegion;
                        }
                        d.canceled = vm.filterCanceled;
                        d.refund_status = vm.filterRefundStatus;
                        if (vm.filterBookingKeyword.length > 0) {
			     d.search_keyword = vm.filterBookingKeyword;
			}
                        return d;
                    }
                },
                columnDefs: [
                    {
                        responsivePriority: 1,
                        targets: 0
                    },
                    {
                        responsivePriority: 2,
                        targets: 2
                    },
                    {
                        responsivePriority: 3,
                        targets: 7
                    }
                ],
                columns:[
                    {
                        data:"id",
                        orderable:false,
                        searchable:false,
                        mRender:function(data,type,full) {
                            return full.status != 'Canceled' ? "<a href='/api/get_confirmation/"+full.id+"' target='_blank' class='text-primary'>PS"+data+"</a><br/>": "PS"+full.id;
                        }
                    },
                    {
                        mRender: function(data, type, full) {
                            //var name = full.firstname +" "+full.lastname;
                            var first_name = full.firstname ? full.firstname : '';
                            var last_name = full.lastname ? full.lastname : '';
                            var name = first_name +" "+ last_name;
                            var max_length = 25;
                            var short_name = (name.length > max_length) ? name.substring(0,max_length-1)+'...' : name;
                            var popover =  (name.length > max_length) ? "class=\"name_popover\"":"";
                            var column = '<td ><div '+popover+' tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__">'+short_name+'</div>';

                            column += '<BR>'+ full.booking_phone_number;
                            column += '</td>';
                            column.replace(/__SHNAME__/g, short_name);
                            return column.replace(/__NAME__/g, name);

                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        mRender: function(data, type, full){
                            if (full.regos.length > 0){
                                var rego = full.regos[0].vessel;
                            } else {
                                var rego = "-"
                            }
                            return rego;
                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        mRender: function(data, type, full){
                            var line = "<td>";
                            for (var msb in full.mooringsite_bookings){
                                line += '<tr>' + full.mooringsite_bookings[msb][0] + '<br/></tr>';
                            }
                            line += '</td>';
                            return line;
                        },
                        orderable: false,
                        searchable: false
                    },
                    {
                        mRender: function(data, type, full){
                            var line = '<td>';
                            for (var msb in full.mooringsite_bookings){
                                line += '<tr>' + full.mooringsite_bookings[msb][1] + '<br/></tr>';
                            }
                            line += '</td>';
                            return line;
                        },
                        orderable:false,
                        searchable:false
                    },
//                    {
//                        data:"campground_site_type",
//                        mRender:function (data,type,full) {
//                            if (data){
//                                var max_length = 15;
//                                var name = (data.length > max_length) ? data.substring(0,max_length-1)+'...' : data;
//                                var column = '<td> <div class="name_popover" tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >'+ name +'</div></td>';
//                                return column.replace('__NAME__', data);
//                            }
//                            return '';
//                        },
//                        orderable:false,
//                        searchable:false
//                   },
                    {
                        orderable:false,
                        searchable:false,
                        mRender:function(data,type,full){
                            var line = '<td>';
                            for (var msb in full.mooringsite_bookings){
                                var date = Moment(full.mooringsite_bookings[msb][2]).format('DD/MM/YYYY HH:mm');
                                line += '<tr>' + date + '<br/></tr>';
                            }
                            line += '</td>';
                            return line;
                        }
                    },
                    {
                        orderable:false,
                        searchable:false,
                        mRender:function(data,type,full){
                            var line = '<td>';
                            for (var msb in full.mooringsite_bookings){
                                var date = Moment(full.mooringsite_bookings[msb][3]).format('DD/MM/YYYY HH:mm');
                                line += '<tr>' + date + '<br/></tr>';
                            }
                            line += '</td>';
                            return line;
                        }
                    },
                    {
                        data:"invoice_status",
                        orderable:false,
                        searchable:false,
                        mRender: function(data,type,full){
                            if (data === 'Canceled' && full.cancellation_reason != null){
                                let val = helpers.dtPopover(full.cancellation_reason);
                                return `<span>${data}</span><br/><br/>${val}`;
                            }
                            return data;
                        },
                        'createdCell': helpers.dtPopoverCellFn
                    },
                    {
                        mRender: function(data, type, full) {
                            var status = (data == true) ? "Open" : "Temporarily Closed";
                            var booking = JSON.stringify(full);
                            var invoices = "";
                            var invoice = "/ledger/payments/invoice/"+full.invoice_reference;
                            var invoice_link= (full.invoice_reference)?"<a href='"+invoice+"' target='_blank' class='text-primary'>Invoice</a><br/>":"";
                            var column = "<td >";
                            if (full.invoices.length > 0) {
                                var invoice_string = '/ledger/payments/invoice/payment?';
                                $.each(full.invoices,function(i,n){
                                    invoice_string += 'invoice='+n+'&';
                                });
                                invoice_string = invoice_string.slice(0,-1);
                                var location_port = window.location.port ? ':'+window.location.port : '';
                                var location_url = `${window.location.protocol}//${window.location.hostname}${location_port}`;
                                invoice_string += full.payment_callback_url ? '&callback_url='+location_url+full.payment_callback_url : '';
//                                if (full.invoice_status == 'unpaid') { 
                               if(full.payment_visible){
                                     var payment = (full.invoice_status == 'paid') ? "View" : "Record";
                                
                                     var record_payment = "<a href='"+invoice_string+"' target='_blank' class='text-primary' data-rec-payment='' > "+payment+" Payment</a><br/>";
                                     column += record_payment; 
                                }                                
                            }
                            if (full.editable){
                                if (full.booking_type == 0 || full.booking_type == 1 || full.booking_type == 2) { 
                                var change_booking = "<a href='/view-booking/"+full.id+"' class='text-primary' > Change</a><br/>";
                                var cancel_booking = "<a href='/cancel-booking/"+full.id+"' class='text-primary' idata-cancel='"+booking+"' > Cancel</a><br/>";
                                column += cancel_booking;
                                column += change_booking;
				}
                            }

                            full.has_history ? column += "<a href='/view-booking/"+full.id+"' class='text-primary' data-history = '"+booking+"' > View History</a><br/>" : '';
                            $.each(full.invoices,(i,v) =>{
                                invoices += "<a href='/mooring/payments/invoice-pdf/"+v+"' target='_blank' class='text-primary'><i style='color:red;' class='fa fa-file-pdf-o'></i>&nbsp #"+v+"</a><br/>"; 
                            });
                            invoices += " <a class='text-primary' href='/booking-history/"+full.id+"'>View History</a>";
                            column += invoices;
                            column += "</td>";
                            return column.replace('__Status__', status);
                        },
                        orderable:false,
                        searchable:false
                    },
                ]
            },
            dtOptions2:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                fnDrawCallback: function(oSettings, json){
                    if(vm.payment_officer){
                        vm.$refs.admissions_bookings_table.vmDataTable.rows().every(function(){
                            var rowdata = this.data();
                            rowdata['payment_visible'] = true;
                            this.data(rowdata);
                        });
                    }
                },
                serverSide:true,
                processing:true,
                searchDelay: 800,
                searching:false,
                ajax: {
                    "url": api_endpoints.admissionsbookings,
                    "dataSrc": 'results',
                    data :function (d) {
                        if (vm.filterDateFrom2) {
                            d.arrival = vm.filterDateFrom2;
                        }
                        if (vm.filterDateTo2) {
                            d.departure = vm.filterDateTo2;
                        }
                        if (vm.filterAdmissionKeyword.length > 0) {
                             d.search_keyword = vm.filterAdmissionKeyword;
			}
                        d.canceled = vm.filterCanceled2;
                    }
                },
                columns:[
                    {
                        data: "id",
                        mRender:function(data,type,full){
                            return "<a href='/api/get_admissions_confirmation/"+data+"' target='_blank' class='text-primary'>AD"+data+"</a><br/>";
                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        mRender: function(data, type, full){
                            if (full.booking){
                                return "<a href='/api/get_confirmation/"+full.booking+"' target='_blank' class='text-primary'>PS"+full.booking+"</a><br/>"
                            } else {
                                return "-"
                            }
                        },
                        orderable: false,
                        searchable: false,
                    },
                    {
                        data: "customerName",
                        orderable:false,
                        searchable:false
                    },
                    {
                        mRender: function(data,type,full){
                            if(full.vesselRegNo){
                                return full.vesselRegNo;
                            } else {
                                return "-";
                            }
                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        mRender:function(data,type,full){
                            return full.noOfAdults + full.noOfChildren + full.noOfInfants;
                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"arrivalDate",
                        orderable:false,
                        searchable:false,
                        mRender:function(data,type,full){
                            var dates = ""
                            for (var no in full.lines){
                                dates += Moment(full.lines[no].date).format("DD/MM/YYYY") + "<br/>";
                            }
                            return dates;
                        }
                    },
                    {
                         mRender: function(data,type,full){
                            if(full.warningReferenceNo){
                                return full.warningReferenceNo;
                            } else {
                                return "-";
                            }
                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        mRender: function(data, type, full) {
                            var search = "";
                            var invoices = "";
                            var column = ""
                            $.each(full.invoice_ref,(i,v) =>{
                                if (i != 0){
                                    search += "&";
                                }
                                search += "invoice=" + v
                                invoices += "<a href='/mooring/payments/invoice-pdf/"+v+"' target='_blank' class='text-primary'><i style='color:red;' class='fa fa-file-pdf-o'></i>&nbsp #"+v+"</a><br/>"; 
                            });
                            var invoice = "/ledger/payments/invoice/payment?" + search;
                            if (full.payment_visible) {
                                var invoice_link= (full.invoice_ref)?"<a href='"+invoice+"' target='_blank' class='text-primary'>View Payment</a><br/>":"";
                                column += invoice_link;
                            }
                            console.log(full.part_booking);
                            if (full.in_future && !full.part_booking) {
                                if (full.booking_type == 0 || full.booking_type == 1 || full.booking_type == 2) { 
                                    var cancel_booking = "<a href='/cancel-admissions-booking/"+full.id+"' class='text-primary'> Cancel</a><br/>";
                                    column += cancel_booking;
			        }
                            }
                            // invoices += " <a href='/booking-history/{{ full.id }}'>View History</a>";
                            column += invoices;
                            return column;
                        },
                        orderable:false,
                        searchable:false
                    },
                ]
            },
            dtHeaders:["Confirmation #", "Person", "Vessel Reg #", "Mooring", "Region", "From", "To", "Status", "Action"],
            dtHeaders2:["Confirmation #", "Booking #", "Person", "Vessel Reg #", "Total Attendees", "Admission Date", "Warning Ref #", "Action"],
            dateFromPicker:null,
            dateToPicker:null,
            dateFromPicker2:null,
            dateToPicker2:null,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            loading:[],
            loading2:[],
            selected_booking:-1,
            filterCampground:"All",
            filterRegion:"All",
            filterDateFrom:"",
            filterDateTo:"",
            filterCanceled: 'False',
            filterRefundStatus: 'All',
            filterDateFrom2:"",
            filterDateTo2:"",
            filterCanceled2: 'False',
            filterBookingKeyword: '',
            filterAdmissionKeyword: ''
        }
    },
    watch:{
        filterCampground: function() {
            let vm = this;
            vm.$refs.bookings_table.vmDataTable.ajax.reload();
        },
        filterRegion: function() {
            let vm = this;
            vm.$refs.bookings_table.vmDataTable.ajax.reload();
        },
        filterCanceled: function() {
            let vm = this;
            vm.$refs.bookings_table.vmDataTable.ajax.reload();
        },
        filterRefundStatus: function() {
            let vm = this;
            vm.$refs.bookings_table.vmDataTable.ajax.reload();
        },
    },
    computed:{
        isLoading:function () {
            return this.loading.length > 0;
        },
        isLoading2: function (){
            return this.loading2.length > 0;
        },
        ...mapGetters([
          'regions',
          'campgrounds'
        ]),
    },
    methods:{
        showhidebookings: function() {
            var content = $('#content_booking');
            var span = $('#collapse_bookings_span');
            if (content.css("display") !== "none"){
                content.css("display", "none");
                span.removeClass("glyphicon glyphicon-menu-up");
                span.addClass("glyphicon glyphicon-menu-down");
            } else {
                content.css("display", "block");
                span.removeClass("glyphicon glyphicon-menu-down");
                span.addClass("glyphicon glyphicon-menu-up");
            }
        },
        showhideadmissions: function(){
            var content = $('#content_admissions')
            var span = $('#collapse_admissions_span');
            if (content.css("display") !== "none"){
                content.css("display", "none");
                span.removeClass("glyphicon glyphicon-menu-up");
                span.addClass("glyphicon glyphicon-menu-down");
            } else {
                content.css("display", "block");
                span.removeClass("glyphicon glyphicon-menu-down");
                span.addClass("glyphicon glyphicon-menu-up");
            }
        },
        fetchCampgrounds:function () {
            let vm =this;
            vm.loading.push('fetching campgrounds');
            if (vm.campgrounds.length == 0) {
                vm.$store.dispatch("fetchCampgrounds");
            }
            vm.loading.splice('fetching campgrounds',1);
        },
        fetchRegions:function () {
            let vm =this;
            if (vm.regions.length == 0) {
                vm.$store.dispatch("fetchRegions");
            }
        },
        cancelBooking:function (booking) {
            let vm =this;
            vm.$http.delete(api_endpoints.booking(booking.id),{
                emulateJSON:true,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}
            }).then((response)=>{
                vm.$refs.bookings_table.vmDataTable.ajax.reload();
            },(error) =>{
                console.log(error);
            });
        },
        addEventListeners:function () {
            let vm =this;

            /* View History */
            vm.$refs.bookings_table.vmDataTable.on('click','a[data-history]',function (e) {
                e.preventDefault();
                var selected_booking = JSON.parse($(this).attr('data-history'));
                vm.selected_booking = selected_booking.id;
                vm.$refs.bookingHistory.booking = selected_booking;
                vm.$refs.bookingHistory.isModalOpen = true;

                //vm.$refs.changebooking.fetchBooking(vm.selected_booking);
            });

            /* Campground Selector*/
            $(vm.$refs.campgroundSelector).select2({
                "theme": "bootstrap",
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.filterCampground = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.filterCampground = "All";
            }); 
            /* End Campground Selector*/

            /* Region Selector*/
            $(vm.$refs.regionSelector).select2({
                "theme": "bootstrap",
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.filterRegion = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.filterRegion = "All";
            }); 
            /* End Region Selector*/
            
            vm.$refs.bookings_table.vmDataTable.on('click','a[data-change]',function (e) {
                //e.preventDefault();
                //var selected_booking = JSON.parse($(this).attr('data-change'));
                //vm.selected_booking = selected_booking.id;
               // vm.$router.push({
               //     'name':'edit-booking',
                //    params: {
                //        booking_id: selected_booking.id
                //    }
               // })
                //vm.$refs.changebooking.fetchBooking(vm.selected_booking);
            });

            vm.$refs.bookings_table.vmDataTable.on('click','a[data-cancel]',function (e) {
                vm.selected_booking = JSON.parse($(this).attr('data-cancel'));
                swal({
                  title: 'Cancel Booking',
                  text: "Provide a cancellation reason",
                  type: 'warning',
                  input: 'textarea',
                  showCancelButton: true,
                  confirmButtonText: 'Submit',
                  showLoaderOnConfirm: true,
                  preConfirm: function (reason) {
                    return new Promise(function (resolve, reject) {
                        vm.$http.delete(api_endpoints.booking(vm.selected_booking.id)+'?reason='+reason,{
                            emulateJSON:true,
                            headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}
                        }).then((response)=>{
                            resolve()
                        },(error) =>{
                            reject(helpers.apiVueResourceError(error));
                        });
                    })
                  },
                  allowOutsideClick: false
                }).then(function (reason) {
                    vm.$refs.bookings_table.vmDataTable.ajax.reload();
                    swal({
                        type: 'success',
                        title: 'Booking Cancelled',
                        html: 'Booking PS' + vm.selected_booking.id + ' has been cancelled'
                    })
                })
                //bus.$emit('showAlert', 'cancelBooking');
            });
            vm.dateToPicker.on('dp.change', function(e){
                if (vm.dateToPicker.data('DateTimePicker').date()) {
                    vm.filterDateTo =  e.date.format('DD/MM/YYYY');
                    vm.$refs.bookings_table.vmDataTable.ajax.reload();
                }
                else if (vm.dateToPicker.data('date') === "") {
                    vm.filterDateTo = "";
                    vm.$refs.bookings_table.vmDataTable.ajax.reload();
                }

             });

            vm.dateFromPicker.on('dp.change',function (e) {
                if (vm.dateFromPicker.data('DateTimePicker').date()) {
                    vm.filterDateFrom = e.date.format('DD/MM/YYYY');
                    vm.dateToPicker.data("DateTimePicker").minDate(e.date);
                    vm.$refs.bookings_table.vmDataTable.ajax.reload();
                }
                else if (vm.dateFromPicker.data('date') === "") {
                    vm.filterDateFrom = "";
                    vm.$refs.bookings_table.vmDataTable.ajax.reload();
                }

            });

            vm.dateToPicker2.on('dp.change', function(e){
                if (vm.dateToPicker2.data('DateTimePicker').date()) {
                    vm.filterDateTo2 =  e.date.format('DD/MM/YYYY');
                    vm.$refs.admissions_bookings_table.vmDataTable.ajax.reload();
                }
                else if (vm.dateToPicker2.data('date') === "") {
                    vm.filterDateTo2 = "";
                    vm.$refs.admissions_bookings_table.vmDataTable.ajax.reload();
                }

             });

            vm.dateFromPicker2.on('dp.change',function (e) {
                if (vm.dateFromPicker2.data('DateTimePicker').date()) {
                    vm.filterDateFrom2 = e.date.format('DD/MM/YYYY');
                    vm.dateToPicker2.data("DateTimePicker").minDate(e.date);
                    vm.$refs.admissions_bookings_table.vmDataTable.ajax.reload();
                }
                else if (vm.dateFromPicker2.data('date') === "") {
                    vm.filterDateFrom2 = "";
                    vm.$refs.admissions_bookings_table.vmDataTable.ajax.reload();
                }

            });
            $('#filterCanceled2').on('change',function (e) {
                   vm.$refs.admissions_bookings_table.vmDataTable.ajax.reload();
	    });
            helpers.namePopover($,vm.$refs.bookings_table.vmDataTable);
            $(document).on('keydown', function(e) {
                if(e.ctrlKey && (e.key == "p" || e.charCode == 16 || e.charCode == 112 || e.keyCode == 80) ){
                    e.preventDefault();
                    bus.$emit('showAlert', 'printBooking');
                    e.stopImmediatePropagation();
                }
            });
        },
        printParams() {
            let vm = this;
            var str = [];
            let obj = {
                arrival : vm.filterDateFrom != null ? vm.filterDateFrom: '',
                departure : vm.filterDateTo != null ? vm.filterDateTo:'' ,
                campground : vm.filterCampground != 'All' ? vm.filterCampground : '',
                region : vm.filterRegion != 'All' ? vm.filterRegion : '',
                canceled: vm.filterCanceled,
            }
             // 'search[value]': vm.$refs.bookings_table.vmDataTable.search()

            for(var p in obj)
                if (obj.hasOwnProperty(p)) {
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
                }
            return str.join("&");
        },
        printParams2() {
            let vm = this;
            var str = [];
            let obj = {
                arrival : vm.filterDateFrom2 != null ? vm.filterDateFrom2: '',
                departure : vm.filterDateTo2 != null ? vm.filterDateTo2:'' ,
                'search[value]': vm.$refs.admissions_bookings_table.vmDataTable.search(),
                canceled: vm.filterCanceled2,
            }

            for(var p in obj)
                if (obj.hasOwnProperty(p)) {
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
                }
            return str.join("&");
        },
        print:function () {
            let vm =this;
            vm.exportingCSV = true;
            vm.$http.get(api_endpoints.bookings+'?'+vm.printParams()).then(res => {
                var data = res.body.results;

                var json2csv = require('json2csv');
                var fields = ['Created']
                //var fields = [...vm.dtHeaders];
                var fields = [...fields,...vm.dtHeaders];
                fields.splice(vm.dtHeaders.length-1,1);
                fields = ['Created', 'Confirmation No', 'Person', 'Email', 'Phone', 'Vessel Rego', 'Amount Due', 'Amount Paid',"Status", "Mooring", "Region", "Arrival", "Departure", "Adults","Concession","Children","Infants",'Booking Type','Invoices','Admission Ref#', 'Admission Amount','Vessel Size','Vessel Draft','Vessel Beam','Vessel Weight']
                //fields = ['Created', 'Confirmation No', 'Person', 'Email', 'Phone', 'Vessel Rego', 'Amount Due', 'Amount Paid',"Status", "Mooring", "Region", "Arrival", "Departure", "Adults","Concession","Children","Infants","Cancelled","Cancellation Reason","Cancelation Date","Cancelled By", 'Booking Type','Invoices']
                // fields = [...fields,"Adults","Concession","Children","Infants","Regos","Cancelled","Cancellation Reason","Cancelation Date","Cancelled By"]
                // fields.splice(4,0,"Email");
                // fields.splice(5,0,"Phone");
                // fields.splice(9,0,'Amount Due')
                // fields.splice(10,0,'Amount Paid')
                // fields.splice(22,0,'Booking Type')
                var booking_types = {
                    0: 'Reception booking',
                    1: 'Internet booking',
                    2: 'Black booking',
                    3: 'Temporary reservation',
                    4: 'Cancelled Booking',
                    5: 'Changed Booking',
                };

                //var data = vm.$refs.bookings_table.vmDataTable.ajax.json().results;
                var bookings = [];
                $.each(data,function (i,booking) {
                    var bk = {};
                    $.each(fields,function (j,field) {
                        switch (j) {
                            case 0:
                                bk[field] = Moment(booking.created).format("DD/MM/YYYY HH:mm:ss");
                            break;
                            case 1:
                                // bk[field] = booking.campground_name;
                                bk[field] = "PS" + booking.id;
                            break;
                            case 2:
                                // bk[field] = booking.campground_region;
                                bk[field] = booking.firstname +" "+ booking.lastname;
                            break;
                            case 3:
                                // bk[field] = booking.firstname +" "+ booking.lastname;
                                bk[field] = booking.email;
                            break;
                            case 4:
                                // bk[field] = booking.email;
                                bk[field] = booking.phone;
                            break;
                            case 5:
                                // bk[field] = booking.phone;
                                bk[field] = booking.regos[0].vessel;
                            break;
                            case 6:
                                bk[field] = booking.cost_total;
                            break;
                            case 7:
                                // bk[field] = booking.campground_site_type;
                                bk[field] = booking.amount_paid;
                            break;
                            case 8:
                                bk[field] = booking.invoice_status;
                            break;
                            case 9:
                                var name_list = []
                                console.log(booking.mooringsite_bookings)
                                for (var i = 0; i < booking.mooringsite_bookings.length; i++){
                                    console.log(booking.mooringsite_bookings[i]);
                                    console.log(booking.mooringsite_bookings[i][0]);
                                    console.log(booking.mooringsite_bookings[i][1]);
                                    console.log(booking.mooringsite_bookings[i][2]);
                                    console.log(booking.mooringsite_bookings[i][3]);
                                    name_list.push(booking.mooringsite_bookings[i][0]);
                                }
                                bk[field] = name_list;
                            break;
                            case 10:
                                var name_list = []
                                for (var i = 0; i < booking.mooringsite_bookings.length; i++){
                                    name_list.push(booking.mooringsite_bookings[i][1]);
                                }
                                bk[field] = name_list;
                            break;
                            case 11:
                                var name_list = []
                                for (var i = 0; i < booking.mooringsite_bookings.length; i++){
                                    name_list.push(Moment(booking.mooringsite_bookings[i][2]).format('DD/MM/YYYY HH:mm'));
                                }
                                bk[field] = name_list;
                            break;
                            case 12:
                                var name_list = []
                                for (var i = 0; i < booking.mooringsite_bookings.length; i++){
                                    name_list.push(Moment(booking.mooringsite_bookings[i][3]).format('DD/MM/YYYY HH:mm'));
                                }
                                bk[field] = name_list;
                            break;
                            case 13:
                                bk[field] = booking.guests.adults;
                            break;
                            case 14:
                                bk[field] =  booking.guests.concession;
                            break;
                            case 15:
                                bk[field] =  booking.guests.children;
                            break;
                            case 16:
                                bk[field] =  booking.guests.infants;
                            break;
//                            case 17:
//                                bk[field] = booking.is_canceled;
//                            break;
//                            case 18:
//                                bk[field] = booking.cancelation_reason;
//                            break;
//                            case 19:
//                                bk[field] = booking.cancelation_time ? Moment(booking.cancelation_time).format("DD/MM/YYYY HH:mm:ss") : '';
//                            break;
//                            case 20:
//                                bk[field] = booking.canceled_by;
//                            break;
                            case 17:
                                if (typeof booking_types[booking.booking_type] !== 'undefined') {
                                    bk[field] = booking_types[booking.booking_type];
                                } else {
                                    bk[field] = booking.booking_type;
                                }
                            break;                   
                            case 18:
                                bk[field] = booking.invoices;
                            break;
                            case 19:
                                if (booking.admissions) { 
                                	bk[field] = 'AD'+booking.admissions.id;
                                } else {
					bk[field] = '';
				}
                            break;
                            case 20:
                                if (booking.admissions) {
                                    	bk[field] = booking.admissions.amount;
                                } else {
					bk[field] = '';
				}
                            break;
                            case 21:
                                if (booking.vessel_details) {
                                        bk[field] = booking.vessel_details.vessel_size;
                                } else {
                                        bk[field] = '';
                                }
                            break;
                            case 22:
                                if (booking.vessel_details) {
                                        bk[field] = booking.vessel_details.vessel_draft;
                                } else {
                                        bk[field] = '';
                                }
                            break;
                            case 23:
                                if (booking.vessel_details) {
                                        bk[field] = booking.vessel_details.vessel_beam;
                                } else {
                                        bk[field] = '';
                                }
                            break;
                            case 24:
                                if (booking.vessel_details) {
                                        bk[field] = booking.vessel_details.vessel_weight;
                                } else {
                                        bk[field] = '';
                                }
                            break;

                        }
                    });
                    bookings.push(bk);
                });
                var csv = json2csv({ data:bookings, fields: fields });
                var a = document.createElement("a"),
                file = new Blob([csv], {type: 'text/csv'});
                var filterCampground = (vm.filterCampground == 'All') ? "All Moorings " : $('#filterCampground')[0].selectedOptions[0].text;
                var filterRegion = (vm.filterCampground == 'All') ? (vm.filterRegion == 'All')? "All Regions" : $('#filterRegion')[0].selectedOptions[0].text : "";
                var filterDates = (vm.filterDateFrom) ? (vm.filterDateTo) ? "From "+vm.filterDateFrom + " To "+vm.filterDateTo: "From "+vm.filterDateFrom : (vm.filterDateTo) ? " To "+vm.filterDateTo : "" ;
                var filename =  filterCampground +  "_" + filterRegion + "_" +filterDates+ ".csv";
                if (window.navigator.msSaveOrOpenBlob) // IE10+
                    window.navigator.msSaveOrOpenBlob(file, filename);
                else { // Others
                    var url = URL.createObjectURL(file);
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(function() {
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                    }, 0);
                }
                vm.exportingCSV = false;
            },
            (error) => {
                vm.exportingCSV = false;
                swal({
                    type: 'error',
                    title: 'Export Error', 
                    text: helpers.apiVueResourceError(error), 
                })
            });
        },
        print2:function () {
            let vm =this;
            vm.exportingCSV2 = true;
            
            vm.$http.get(api_endpoints.admissionsbookings+'?'+vm.printParams2()).then(res => {
                var data = res.body.results;

                var json2csv = require('json2csv');
                var fields = ["Confirmation No", "Customer", "Email", "Overnight Stay", "Arrival Date", "Total Attendees", "Adults","Children","Infants", "Vessel Reg No", "Warning Reference", "Invoice Reference",'Vessel Size','Vessel Draft','Vessel Beam','Vessel Weight']
                
                var bookings = [];
                $.each(data,function (i,booking) {
                    var bk = {};
                    $.each(fields,function (j,field) {
                        switch (j) {
                            case 0:
                                bk[field] = "AD" + booking.id;
                                
                            break;
                            case 1:
                                bk[field] = booking.customerName;
                            break;
                            case 2:
                                bk[field] = booking.email;
                            break;
                            case 3:
                                var answer = "";
                                if(booking.lines){
                                    for (var line in booking.lines){
                                        if (line > 0){
                                            answer += ", ";
                                        }
                                        if (booking.lines[line].overnight){
                                            answer += "Yes";
                                        } else {
                                            answer += "No"
                                        }
                                        
                                    }
                                }
                                bk[field] = answer;
                            break;
                            case 4:
                                var dates = ""
                                if (booking.lines){
                                    for (var line in booking.lines){
                                        if (line > 0){
                                            dates += ", ";
                                        }
                                        dates += Moment(booking.lines[line].date).format("DD/MM/YYYY");
                                    }
                                }
                                bk[field] = dates
                            break;
                            case 5:
                                bk[field] = booking.noOfAdults + booking.noOfChildren + booking.noOfInfants;
                            break;
                            case 6:
                                bk[field] = booking.noOfAdults;
                            break;
                            case 7:
                                bk[field] = booking.noOfChildren;
                            break;
                            case 8:
                                bk[field] = booking.noOfInfants;
                            break;
                            case 9:
                                bk[field] = booking.vesselRegNo;
                            break;
                            case 10:
                                bk[field] = booking.warningReferenceNo;
                            break;
                            case 11:
                                bk[field] = booking.invoice_ref;
                            break;
                        }
                    });
                    bookings.push(bk);
                });
                var csv = json2csv({ data:bookings, fields: fields });
                var a = document.createElement("a"),
                file = new Blob([csv], {type: 'text/csv'});
                var filterDates = (vm.filterDateFrom2) ? (vm.filterDateTo2) ? "From "+vm.filterDateFrom2 + " To "+vm.filterDateTo2: "From "+vm.filterDateFrom2 : (vm.filterDateTo2) ? " To "+vm.filterDateTo2 : "" ;
                var filename =  filterDates + "_admissions" + ".csv";
                filename.replace(" ", "_");
                if (window.navigator.msSaveOrOpenBlob) // IE10+
                    window.navigator.msSaveOrOpenBlob(file, filename);
                else { // Others
                    var url = URL.createObjectURL(file);
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(function() {
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                    }, 0);
                }
                vm.exportingCSV2 = false;
            },
            (error) => {
                vm.exportingCSV2 = false;
                swal({
                    type: 'error',
                    title: 'Export Error', 
                    text: helpers.apiVueResourceError(error), 
                })
            });
        },
    },
    created: function(){
        let vm = this;
        $.ajax({
            url: api_endpoints.profile,
            method: 'GET',
            dataType: 'json',
            success: function(data, stat, xhr){
                if(data.is_payment_officer){
                    vm.payment_officer = true;
                }
            }
        });
    },
    mounted:function () {
        let vm = this;
        vm.dateFromPicker = $('#booking-date-from').datetimepicker(vm.datepickerOptions);
        vm.dateToPicker = $('#booking-date-to').datetimepicker(vm.datepickerOptions);
        vm.dateFromPicker2 = $('#admission-date-from').datetimepicker(vm.datepickerOptions);
        vm.dateToPicker2 = $('#admission-date-to').datetimepicker(vm.datepickerOptions);
        vm.fetchCampgrounds();
        vm.fetchRegions();
        vm.addEventListeners();
        //Bookings
        $('#bookings-collapse').on('shown.bs.collapse', function(){
            $('#collapse_bookings_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_bookings_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#bookings-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_bookings_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_bookings_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Admissions
        $('#admissions-collapse').on('shown.bs.collapse', function(){
            $('#collapse_admissions_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_admissions_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#admissions-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_admissions_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_admissions_span').addClass("glyphicon glyphicon-menu-down");
        });

        $('#BookingKeyword').on('change', function() {
               vm.$refs.bookings_table.vmDataTable.ajax.reload();
        });


        $('#AdmissionKeyword').on('change', function() { 
               vm.$refs.admissions_bookings_table.vmDataTable.ajax.reload(); 
        }); 

    }

}
</script>

<style lang="css">
    .text-warning{
        color:#f0ad4e;
    }
    @media print {
        .col-md-3 {
            width: 25%;
            float:left;
        }

        a[href]:after {
           content: none !important;
        }

        #print-btn {
            display: none !important;
        }
    }
</style>
