<template lang="html" id="booking-dashboard">
<div class="row">
  <div class="col-lg-12" v-show="!isLoading">
      <div class="well"     style="overflow: auto;">
          <div class="row">
              <div class="col-lg-12">
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
            <div class="col-md-4" v-if="filterCanceled == 'True'">
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
      </div>
      <changebooking ref="changebooking" :booking_id="selected_booking" :campgrounds="campgrounds"/>
      <bookingHistory ref="bookingHistory" :booking_id="selected_booking" />
  </div>
   <loader :isLoading="isLoading" >{{loading.join(' , ')}}</loader>
</div>
</template>

<script>
import {$,bus,datetimepicker,api_endpoints,helpers,Moment,swal,select2} from "../../hooks.js"
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
            dtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide:true,
                processing:true,
                searchDelay: 800,
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
                            d.campground = vm.filterCampground
                        }
                        if (vm.filterRegion != "All") {
                            d.region = vm.filterRegion
                        }
                        d.canceled = vm.filterCanceled;
                        d.refund_status = vm.filterRefundStatus;

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
                        data:"campground_name",
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"campground_region",
                        orderable:false,
                        searchable:false
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
                            var column = '<td ><div '+popover+' tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__">'+short_name+'</div></td>';
                            column.replace(/__SHNAME__/g, short_name);
                            return column.replace(/__NAME__/g, name);

                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"id",
                        orderable:false,
                        searchable:false,
                        mRender:function(data,type,full){
                            return full.status != 'Canceled' ? "<a href='/api/get_confirmation/"+full.id+"' target='_blank' class='text-primary'>PS"+data+"</a><br/>": "PS"+full.id;
                        }
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
                        data:"status",
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
                        data:"arrival",
                        orderable:false,
                        searchable:false,
                        mRender:function(data,type,full){
                            return Moment(data).format('DD/MM/YYYY');
                        }
                    },
                    {
                        data:"departure",
                        orderable:false,
                        searchable:false,
                        mRender:function(data,type,full){
                            return Moment(data).format('DD/MM/YYYY');
                        }
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
                                var payment = (full.paid || full.status == 'Canceled') ? "View" : "Record";
                                var record_payment = "<a href='"+invoice_string+"' target='_blank' class='text-primary' data-rec-payment='' > "+payment+" Payment</a><br/>";
                                column += record_payment;
                            }
                            if (full.editable){
                                var change_booking = "<a href='edit/"+full.id+"' class='text-primary' data-change = '"+booking+"' > Change</a><br/>";
                                var cancel_booking = "<a href='#' class='text-primary' data-cancel='"+booking+"' > Cancel</a><br/>";
                                column += cancel_booking;
                                column += change_booking;
                            }
                            full.has_history ? column += "<a href='edit/"+full.id+"' class='text-primary' data-history = '"+booking+"' > View History</a><br/>" : '';
                            $.each(full.active_invoices,(i,v) =>{
                                invoices += "<a href='/ledger/payments/invoice-pdf/"+v+"' target='_blank' class='text-primary'><i style='color:red;' class='fa fa-file-pdf-o'></i>&nbsp #"+v+"</a><br/>"; 
                            });
                            column += invoices;
                            column += "</td>";
                            return column.replace('__Status__', status);
                        },
                        orderable:false,
                        searchable:false
                    },
                ]
            },
            dtHeaders:["Mooring","Region","Person","Confirmation #","Status","From","To","Action"],
            dateFromPicker:null,
            dateToPicker:null,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            loading:[],
            selected_booking:-1,
            filterCampground:"All",
            filterRegion:"All",
            filterDateFrom:"",
            filterDateTo:"",
            filterCanceled: 'False',
            filterRefundStatus: 'All'
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
        ...mapGetters([
          'regions',
          'campgrounds'
        ]),
    },
    methods:{
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
                e.preventDefault();
                var selected_booking = JSON.parse($(this).attr('data-change'));
                vm.selected_booking = selected_booking.id;
                vm.$router.push({
                    'name':'edit-booking',
                    params: {
                        booking_id: selected_booking.id
                    }
                })
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
                'search[value]': vm.$refs.bookings_table.vmDataTable.search()
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
                fields = [...fields,"Adults","Concession","Children","Infants","Regos","Cancelled","Cancellation Reason","Cancelation Date","Cancelled By"]
                fields.splice(4,0,"Email");
                fields.splice(5,0,"Phone");
                fields.splice(9,0,'Amount Due')
                fields.splice(10,0,'Amount Paid')
                fields.splice(22,0,'Booking Type')
                var booking_types = {
                    0: 'Reception booking',
                    1: 'Internet booking',
                    2: 'Black booking',
                    3: 'Temporary reservation',
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
                                bk[field] = booking.campground_name;
                            break;
                            case 2:
                                bk[field] = booking.campground_region;
                            break;
                            case 3:
                                bk[field] = booking.firstname +" "+ booking.lastname;
                            break;
                            case 4:
                                bk[field] = booking.email;
                            break;
                            case 5:
                                bk[field] = booking.phone;
                            break;
                            case 6:
                                bk[field] = booking.id;
                            break;
                            case 7:
                                bk[field] = booking.campground_site_type;
                            break;
                            case 8:
                                bk[field] = booking.status;
                            break;
                            case 9:
                                bk[field] = booking.cost_total;
                            break;
                            case 10:
                                bk[field] = booking.amount_paid;
                            break;
                            case 11:
                                bk[field] = Moment(booking.arrival).format("DD/MM/YYYY");
                            break;
                            case 12:
                                bk[field] = Moment(booking.departure).format("DD/MM/YYYY");
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
                            case 17:
                                bk[field] =  booking.vehicle_payment_status.map(r =>{
                                    var val =Object.keys(r).map(k =>{
                                        if (k == 'Fee' || k == 'original_type'){ return 'avoid'; }
                                        if (k == 'Paid'){
                                            if (r[k] == 'Yes'){
                                                return "Status" +" : Entry Fee Paid";
                                            }
                                            else if( r[k] == 'No'){
                                                return "Status" +" : Unpaid";
                                            }
                                            else if(r[k] == 'pass_required'){
                                                return "Status" +" : Park Pass Required"
                                            }
                                        }
                                        else{
                                            return k +" : "+ r[k]
                                        }
                                    });
                                    return val.filter(i => i != 'avoid');
                                }).join(" | ");
                            break;
                            case 18:
                                bk[field] = booking.is_canceled;
                            break;
                            case 19:
                                bk[field] = booking.cancelation_reason;
                            break;
                            case 20:
                                bk[field] = booking.cancelation_time ? Moment(booking.cancelation_time).format("DD/MM/YYYY HH:mm:ss") : '';
                            break;
                            case 21:
                                bk[field] = booking.canceled_by;
                            break;
                            case 22:
                                if (typeof booking_types[booking.booking_type] !== 'undefined') {
                                    bk[field] = booking_types[booking.booking_type];
                                } else {
                                    bk[field] = booking.booking_type;
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
        }
    },
    mounted:function () {
        let vm = this;
        vm.dateFromPicker = $('#booking-date-from').datetimepicker(vm.datepickerOptions);
        vm.dateToPicker = $('#booking-date-to').datetimepicker(vm.datepickerOptions);
        vm.fetchCampgrounds();
        vm.fetchRegions();
        vm.addEventListeners();
        // Set the from date to todays date as default
        vm.filterDateFrom = Moment().format('DD/MM/YYYY')
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
