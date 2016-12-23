<template lang="html" id="booking-dashboard">
<div class="row">
  <div class="col-lg-12" v-show="!isLoading">
      <div class="well">
          <div class="row">
            <div class="col-md-3">
                <div class="form-group">
                  <label for="">Campground</label>
                  <select v-show="isLoading" class="form-control" name="">
                      <option value="">Loading...</option>
                  </select>
                  <select v-if="!isLoading" class="form-control" name="">
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
                  <select v-if="!isLoading" class="form-control" name="">
                        <option value="">All</option>
                        <option v-for="park in parks" value="park.id">{{park.name}}</option>
                  </select>
                </div>
            </div>
            <div class="col-md-3">
                <label for="">Date From</label>
                <div class="input-group">
                  <input type="text" class="form-control" id="booking-date-from" placeholder="DD/MM/YYYY">
                  <span class="input-group-addon">
                      <span class="glyphicon glyphicon-calendar"></span>
                  </span>
                </div>
            </div>
            <div class="col-md-3">
                <label for="">Date To</label>
                <div class="input-group">
                  <input type="text" class="form-control" id="booking-date-to" placeholder="DD/MM/YYYY">
                  <span class="input-group-addon">
                      <span class="glyphicon glyphicon-calendar"></span>
                  </span>
                </div>
            </div>
            <div class="col-md-12">
                <router-link :to="{name:'add-booking'}" type="button" class="btn btn-primary pull-right">Add Booking</router-link>
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

</div>
</template>

<script>
import {$,datetimepicker,api_endpoints} from "../../hooks.js"
import loader from "../utils/loader.vue"
import datatable from '../utils/datatable.vue'
import changebooking from "./changebooking.vue"
export default {
    name:'booking-dashboard',
    components:{
        datatable,
        loader,
        changebooking
    },
    data:function () {
        let vm =this;
        return {
            dtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": api_endpoints.bookings,
                    "dataSrc": ''
                },
                columns:[
                    {
                        data:"campground.name"
                    },
                    {
                        data:"campground.region"
                    },
                    {
                        data:"legacy_name"
                    },
                    {
                        data:"legacy_id"
                    },
                    {
                        data:"campground.site_type"
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
                                            <a href='#' class='text-primary' data-cancel= '' > Cancel</a><br/>\
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
                minDate:new Date(),
                format: 'DD/MM/YYYY',
                showClear:true
            },
            loading:[],
            parks:[],
            campgrounds:[],
            selected_booking:{}
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
        addEventListeners:function () {
            let vm =this;
            //change event
            vm.$refs.bookings_table.vmDataTable.on('click','a[data-change]',function (e) {
                vm.selected_booking = JSON.parse($(this).attr('data-change'));
                vm.$refs.changebooking.isModalOpen = true;
            });
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
</style>
