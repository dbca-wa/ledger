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
                  <select v-if="!isLoading" class="form-control" v-model="filterRegion">
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
                        data:"legacy_name",
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"legacy_id",
                        orderable:false,
                        searchable:false
                    },
                    {
                        data:"campground_site_type",
                        orderable:false,
                        searchable:false
                    },
                    {
                        mRender: function(data, type, full) {
                            var status = (data == true) ? "Open" : "Temporarily Closed";
                            var column = "<td >__Status__</td>";
                            return column.replace('__Status__', status);
                        },
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
                            var column = "<td > \
                                            <a href='#' class='text-primary' data-rec-payment='' > Record Payment</a><br/>\
                                            <a href='#' class='text-primary' data-cancel='"+booking+"' > Cancel</a><br/>\
                                            <a href='#' class='text-primary' data-change = '"+booking+"' > Change</a><br/>\
                                        </td>";
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
</style>
