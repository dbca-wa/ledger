<template lang="html" id="booking-dashboard">
<div class="row">
  <div class="col-lg-12" v-show="!isLoading">
      <div class="well">
          <div class="row">
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Campground</label>
                  <select v-show="isLoading" class="form-control" >
                      <option value="">Loading...</option>
                  </select>
                  <select v-if="!isLoading" class="form-control" v-model="filterCampground">
                      <option value="All">All</option>
                      <option v-for="campground in campgrounds" value="campground.id">{{campground.name}}</option>
                  </select>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Region</label>
                  <select v-show="isLoading" class="form-control" name="">
                        <option value="">Loading...</option>
                  </select>
                  <select v-if="!isLoading" class="form-control" v-model="filterRegion">
                        <option value="All">All</option>
                        <option v-for="park in parks" value="park.id">{{park.name}}</option>
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
      <changebooking ref="changebooking" :booking="selected_booking" :campgrounds="campgrounds"/>
  </div>
   <loader :isLoading="isLoading" >{{loading.join(' , ')}}</loader>
   <confirmbox id="cancelBooking" :options="cancelBookingOptions"></confirmbox>
</div>
</template>

<script>
import {$,bus,datetimepicker,api_endpoints} from "../../hooks.js"
import loader from "../utils/loader.vue"
import datatable from '../utils/datatable.vue'
import confirmbox from '../utils/confirmbox.vue'
import changebooking from "./changebooking.vue"
export default {
    name:'booking-dashboard',
    components:{
        datatable,
        loader,
        changebooking,
        confirmbox
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
                        vm.selected_booking = {};
                    },
                    autoclose: true
                }],
                id: 'cancelBooking'
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
                },
                columns:[
                    {
                        data:"campground_name"
                    },
                    {
                        data:"campground_region"
                    },
                    {
                        data:"legacy_name"
                    },
                    {
                        data:"legacy_id"
                    },
                    {
                        data:"campground_site_type"
                    },
                    {
                        mRender: function(data, type, full) {
                            var status = (data == true) ? "Open" : "Temporarily Closed";
                            var column = "<td >__Status__</td>";
                            return column.replace('__Status__', status);
                        }
                    },
                    {
                        data:"arrival"
                    },
                    {
                        data:"departure"
                    },
                    {
                        mRender: function(data, type, full) {
                            var status = (data == true) ? "Open" : "Temporarily Closed";
                            var booking = JSON.stringify(full);
                            var column = "<td > \
                                            <a href='#' class='text-primary' data-rec-payment='' > Record Payment</a><br/>\
                                            <a href='#' class='text-primary' data-cancel='"+booking+"' > Cancel</a><br/>\
                                            <a href='#' class='text-primary' data-change = '"+booking+"' > Change</a><br/>\
                                        </td>";
                            return column.replace('__Status__', status);
                        }
                    },
                ]
            },
            dtHeaders:["Campground","Region","Person","Confirmation #"," Campsite(Type)","Status","From","To","Action"],
            dateFromPicker:null,
            dateToPicker:null,
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true
            },
            loading:[],
            parks:[],
            campgrounds:[],
            selected_booking:{},
            filterCampground:"All",
            filterRegion:"All",
            filterDateFrom:"",
            filterDateTo:""
        }
    },
    watch:{
        filterCampground: function() {
            let vm = this;
            if (vm.filterCampground != 'All') {
                vm.$refs.bookings_table.vmDataTable.columns(0).search(vm.filterCampground).draw();
            } else {
                vm.$refs.bookings_table.vmDataTable.columns(0).search('').draw();
            }
        },
        filterRegion: function() {
            let vm = this;
            if (vm.filterRegion != 'All') {
                vm.$refs.bookings_table.vmDataTable.columns(1).search(vm.filterRegion).draw();
            } else {
                vm.$refs.bookings_table.vmDataTable.columns(1).search('').draw();
            }
        },
        filterDateFrom: function() {
            let vm = this;
            if (vm.filterDateFrom) {
                vm.$refs.bookings_table.vmDataTable.draw();
            } else {
                vm.$refs.bookings_table.vmDataTable.draw();
            }
        },
        filterDateTo: function() {
            let vm = this;
            if (vm.filterDateTo) {
                vm.$refs.bookings_table.vmDataTable.draw();
            } else {
                vm.$refs.bookings_table.vmDataTable.draw();
            }
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
        fetchParks:function () {
            let vm =this;
            vm.loading.push('fetching parks');
            vm.$http.get(api_endpoints.parks).then((response) => {
                vm.parks = response.body;
                vm.loading.splice('fetching parks',1);
            }, (response) => {
              vm.loading.splice('fetching parks',1);
            });
        },
        cancelBooking:function (booking) {
            //TODO cancelbooking logic
            console.log('cancelling booking');
        },
        addEventListeners:function () {
            let vm =this;
            vm.$refs.bookings_table.vmDataTable.on('click','a[data-change]',function (e) {
                vm.selected_booking = JSON.parse($(this).attr('data-change'));
                vm.$refs.changebooking.isModalOpen = true;
            });

            vm.$refs.bookings_table.vmDataTable.on('click','a[data-cancel]',function (e) {
                vm.selected_booking = JSON.parse($(this).attr('data-cancel'));
                bus.$emit('showAlert', 'cancelBooking');
            });
            vm.dateToPicker.on('dp.change', function(e){
                 vm.filterDateTo =  vm.dateToPicker.data('DateTimePicker').date().format('YYYY-MM-DD');
             });

            vm.dateFromPicker.on('dp.change',function (e) {
                vm.filterDateFrom = vm.dateFromPicker.data('DateTimePicker').date().format('YYYY-MM-DD');
                vm.dateToPicker.data("DateTimePicker").minDate(e.date);
            });
            $.fn.dataTable.ext.search.push(
                function( settings, data, dataIndex ) {
                    if (vm.filterDateFrom && vm.filterDateTo) {
                        var fromDate = new Date(data[6]);
                        var fromFilterDate = new Date(vm.filterDateFrom);
                        var toFilterDate = new Date(vm.filterDateTo);
                        return (fromDate.getTime() >= fromFilterDate.getTime() && fromDate.getTime() < toFilterDate.getTime());
                    }else{
                        return true;
                    }
                    return false;
                }
            );
        }
    },
    mounted:function () {
        let vm = this;
        vm.dateFromPicker = $('#booking-date-from').datetimepicker(vm.datepickerOptions);
        vm.dateToPicker = $('#booking-date-to').datetimepicker(vm.datepickerOptions);
        vm.fetchCampgrounds();
        vm.fetchParks();
        vm.addEventListeners();
    }

}
</script>

<style lang="css">
    .text-warning{
        color:#f0ad4e;
    }
</style>
