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
                <button type="button" class="btn btn-primary pull-right">Add Booking</button>
            </div>
          </div>
          <div class="row">
            <div class="col-lg-12">
                <datatable id="bookings-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders"></datatable>
            </div>
          </div>
      </div>
      <changebooking :campsites="[]" :campgrounds="campgrounds"/>
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
            campgrounds:[]
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
        }
    },
    mounted:function () {
        let vm = this;
        vm.dateFromPicker = $('#booking-date-from').datetimepicker(vm.datepickerOptions);
        vm.dateToPicker = $('#booking-date-to').datetimepicker(vm.datepickerOptions);
        vm.fetchCampgrounds();
        vm.fetchParks();
    }

}
</script>

<style lang="css">
</style>
