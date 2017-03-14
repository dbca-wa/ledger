<template lang="html" id="booking-dashboard">
<div class="row">
  <div class="col-lg-12" v-show="!isLoading">
      <div class="well">
          <div class="row">
              <div class="col-lg-12">
                  <button type="button" class="btn btn-default pull-right" id="print-btn" @click="print()">
                      <i class="fa fa-print" aria-hidden="true"></i> Print
                  </button>
              </div>
          </div>
          <div class="row">
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Campground</label>
                  <select v-show="isLoading" class="form-control" >
                      <option value="">Loading...</option>
                  </select>
                  <select v-if="!isLoading" class="form-control" v-model="filterCampground" id="filterCampground">
                      <option value="All">All</option>
                      <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                  </select>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Region</label>
                  <select v-show="isLoading" class="form-control" name="">
                        <option value="">Loading...</option>
                  </select>
                  <select v-if="!isLoading" class="form-control" v-model="filterRegion" id="filterRegion">
                        <option value="All">All</option>
                        <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                  </select>
                </div>
            </div>
            <div class="col-md-3">
                <label for="">Date From</label>
                <div class="input-group date" id="booking-date-from">
                  <input type="text" class="form-control"  placeholder="DD/MM/YYYY">
                  <span class="input-group-addon">
                      <span class="glyphicon glyphicon-calendar"></span>
                  </span>
                </div>
            </div>
            <div class="col-md-3">
                <label for="">Date To</label>
                <div class="input-group date" id="booking-date-to">
                  <input type="text" class="form-control"  placeholder="DD/MM/YYYY">
                  <span class="input-group-addon">
                      <span class="glyphicon glyphicon-calendar"></span>
                  </span>
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
  </div>
   <loader :isLoading="isLoading" >{{loading.join(' , ')}}</loader>
   <confirmbox id="cancelBooking" :options="cancelBookingOptions"></confirmbox>
   <confirmbox id="printBooking" :options="printBookingOptions"></confirmbox>
</div>
</template>

<script>
import {$,bus,datetimepicker,api_endpoints,helpers,Moment} from "../../hooks.js"
import loader from "../utils/loader.vue"
import datatable from '../utils/datatable.vue'
import confirmbox from '../utils/confirmbox.vue'
import changebooking from "./changebooking.vue"
import modal from '../utils/bootstrap-modal.vue'
export default {
    name:'booking-dashboard',
    components:{
        datatable,
        loader,
        changebooking,
        confirmbox,
        modal
    },
    data:function () {
        let vm =this;
        return {
            cancelBookingOptions: {
                icon: "<i class='fa fa-exclamation-triangle fa-2x text-warning' aria-hidden='true'></i>",
                message: "Are you sure you want to cancel this booking ?",
                buttons: [{
                    text: "Cancel",
                    event: "cbevent",
                    bsColor: "btn-warning",
                    handler: function() {
                        vm.cancelBooking(vm.selected_booking);
                        vm.selected_booking = -1;
                    },
                    autoclose: true
                }],
                id: 'cancelBooking'
            },
            printBookingOptions: {
                icon: "<i class='fa fa-exclamation-circle fa-2x text-primary' aria-hidden='true'></i>",
                message: "Please use the CSV button below for a better formarted document, otherwise use the print button to print the current page.",
                buttons: [
                    {
                    text: "<i class=\"fa fa-file-excel-o\" aria-hidden=\"true\"></i> CSV",
                    event: "dcsvevent",
                    bsColor: "btn-default",
                    handler: function() {
                        vm.printCsv();
                    },
                    autoclose: true
                    },
                    {
                        text: "<i class=\"fa fa-print\" aria-hidden=\"true\"></i> Print",
                        event: "printevent",
                        bsColor: "btn-default",
                        handler: function() {
                            window.print();
                        },
                        autoclose: true
                    }
                ],
                id: 'printBooking'
            },
            dtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide:true,
                processing:true,
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

                        return d;
                    }
                },
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
                            var name = full.firstname +" "+full.lastname;
                            var max_length = 15;
                            var short_name = (name.length > max_length) ? name.substring(0,max_length-1)+'...' : name;
                            var column = '<td ><div class="name_popover" tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__">'+short_name+'</div></td>';
                            column.replace(/__SHNAME__/g, short_name);
                            return column.replace(/__NAME__/g, name);

                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"id",
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"campground_site_type",
                        mRender:function (data,type,full) {
                            if (data){
                                var max_length = 10;
                                var name = (data.length > max_length) ? data.substring(0,max_length-1)+'...' : data;
                                var column = '<td> <div class="name_popover" tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >'+ name +'</div></td>';
                                return column.replace('__NAME__', data);
                            }
                            return '';
                        },
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"status",
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"arrival",
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"departure",
                        orderable:false,
                        searchable:false
                    },
                    {
                        mRender: function(data, type, full) {
                            var status = (data == true) ? "Open" : "Temporarily Closed";
                            var booking = JSON.stringify(full);
                            var invoice = "/ledger/payments/invoice/"+full.invoice_reference;
                            var invoice_link= (full.invoice_reference)?"<a href='"+invoice+"' target='_blank' class='text-primary'>Invoice</a><br/>":"";
                            var column = "<td >";
                            var invoice_string = '/ledger/payments/invoice/payment?';
                            $.each(full.invoices,function(i,n){
                                invoice_string += 'invoice='+n+'&';
                            });
                            invoice_string.trim('&');
                            if (!full.paid){
                                var record_payment = "<a href='"+invoice_string+"' target='_blank' class='text-primary' data-rec-payment='' > Record Payment</a><br/>";
                                column += record_payment;
                            }
                            if (full.editable){
                                var change_booking = "<a href='#' class='text-primary' data-change = '"+booking+"' > Change</a><br/>";
                                var cancel_booking = "<a href='#' class='text-primary' data-cancel='"+booking+"' > Cancel</a><br/>";
                                column += cancel_booking;
                                column += change_booking;
                            }
                            column += "</td>";
                            return column.replace('__Status__', status);
                        },
                        orderable:false,
                        searchable:false
                    },
                ]
            },
            dtHeaders:["Campground","Region","Person","Confirmation #"," Campsite(Type)","Status","From","To","Action"],
            dateFromPicker:null,
            dateToPicker:null,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false
            },
            loading:[],
            regions:[],
            campgrounds:[],
            selected_booking:-1,
            filterCampground:"All",
            filterRegion:"All",
            filterDateFrom:"",
            filterDateTo:""
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
        filterDateFrom: function() {
            let vm = this;
            vm.$refs.bookings_table.vmDataTable.ajax.reload();
        },
        filterDateTo: function() {
            let vm = this;
            vm.$refs.bookings_table.vmDataTable.ajax.reload();
        }
    },
    computed:{
        isLoading:function () {
            return this.loading.length > 0;
        }
    },
    methods:{
        fetchCampgrounds:function () {
            let vm =this;
            vm.loading.push('fetching campgrounds');
            vm.$http.get(api_endpoints.campgrounds).then((response) => {
                vm.campgrounds = response.body;
                vm.loading.splice('fetching campgrounds',1);
            }, (response) => {
              vm.loading.splice('fetching campgrounds',1);
            });
        },
        fetchRegions:function () {
            let vm =this;
            vm.loading.push('fetching regions');
            vm.$http.get(api_endpoints.regions).then((response) => {
                vm.regions = response.body;
                vm.loading.splice('fetching regions',1);
            }, (error) => {
              vm.loading.splice('fetching regions',1);
              console.log(error);
            });
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
            vm.$refs.bookings_table.vmDataTable.on('click','a[data-change]',function (e) {
                var selected_booking = JSON.parse($(this).attr('data-change'));
                vm.selected_booking = selected_booking.id;
                vm.$refs.changebooking.fetchBooking(vm.selected_booking);
            });

            vm.$refs.bookings_table.vmDataTable.on('click','a[data-cancel]',function (e) {
                vm.selected_booking = JSON.parse($(this).attr('data-cancel'));
                bus.$emit('showAlert', 'cancelBooking');
            });
            vm.dateToPicker.on('dp.hide', function(e){
                vm.filterDateTo =  e.date.format('YYYY-MM-DD');
                if (vm.dateToPicker.data('date') === "") {
                    vm.filterDateTo = ""
                }else {
                    vm.filterDateTo =  e.date.format('YYYY-MM-DD');
                }
             });

            vm.dateFromPicker.on('dp.hide',function (e) {
                if (vm.dateFromPicker.data('date') === "") {
                    vm.filterDateFrom = ""
                }else {
                    vm.filterDateFrom = e.date.format('YYYY-MM-DD');
                    vm.dateToPicker.data("DateTimePicker").minDate(e.date);
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
        print:function () {
            bus.$emit('showAlert', 'printBooking')
        },
        printCsv:function () {
            let vm =this;
            var json2csv = require('json2csv');
            var fields = JSON.parse(JSON.stringify(vm.dtHeaders));
            fields.splice(fields.length-1,1);
            var data = vm.$refs.bookings_table.vmDataTable.ajax.json().results;
            var bookings = [];
            $.each(data,function (i,booking) {
                var bk = {};
                $.each(fields,function (j,field) {
                    switch (j) {
                        case 0:
                        bk[field] = booking.campground_name;
                        break;
                        case 1:
                            bk[field] = booking.campground_region;
                        break;
                        case 2:
                            bk[field] = booking.firstname + booking.lastname;
                        break;
                        case 3:
                            bk[field] = booking.id;
                        break;
                        case 4:
                            bk[field] = booking.campground_site_type;
                        break;
                        case 5:
                            bk[field] = (booking.editable)? "Paid":"Unpaid";
                        break;
                        case 6:
                            bk[field] = Moment(booking.arrival).format("dddd, MMMM Do YYYY");
                        break;
                        case 7:
                            bk[field] = Moment(booking.departure).format("dddd, MMMM Do YYYY");
                        break;

                    }
                });
                bookings.push(bk);
            });
            var csv = json2csv({ data:bookings, fields: fields });
            var a = document.createElement("a"),
            file = new Blob([csv], {type: 'text/csv'});
            var filterCampground = (vm.filterCampground == 'All') ? "All Campgrounds " : $('#filterCampground')[0].selectedOptions[0].text;
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
        }
    },
    mounted:function () {
        let vm = this;
        vm.dateFromPicker = $('#booking-date-from').datetimepicker(vm.datepickerOptions);
        vm.dateToPicker = $('#booking-date-to').datetimepicker(vm.datepickerOptions);
        vm.fetchCampgrounds();
        vm.fetchRegions();
        vm.addEventListeners();
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
