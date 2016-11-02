<template>
  <div id="groundsList">
    <form class="form" id="campgrounds-filter-form">
        <div class="col-md-8">
            <div class="col-md-3">
                <div class="form-group">
                    <label for="campgrounds-filter-status">Status: </label>
                    <select class="form-control" v-model="selected_status">
                        <option value="All">All</option>
                        <option value="Open">Open</option>
                        <option value="Temporarily Closed">Temporarily Closed</option>
                    </select>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label for="applications-filter-region">Region: </label>
                    <select class="form-control" v-model="selected_region" >
                        <option value="All" selected="true">All</option>
                        <option v-for="region in regions" :value="region.name"> {{ region.name }}</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="form-group pull-right">
                <a style="margin-top: 20px;"class="btn btn-primary ">Add Campground</a>
            </div>
        </div>
    </form>
    <table class="hover table table-striped table-bordered" id="groundsTable">
          <thead>
              <tr>
                  <th class="id">Campground ID</th>
                  <th class="name">Campground Name</th>
                  <th class="status">Status</th>
                  <th class="region">Region</th>
                  <th class="dogs_allowed">Dogs Allowed</th>
                  <th class="campfires_allowed">Campfires Allowed</th>
                  <th class="action">Action</th>
              </tr>
          </thead>
          <tbody>
          </tbody>
      </table>
</div>

</template>

<script>
var $ = require( 'jquery' );
var DataTable = require( 'datatables.net' )();
var DataTableBs = require( 'datatables.net-bs' )();

var debounce = function (func, wait, immediate) {
    // Returns a function, that, as long as it continues to be invoked, will not
    // be triggered. The function will be called after it stops being called for
    // N milliseconds. If `immediate` is passed, trigger the function on the
    // leading edge, instead of the trailing.
    'use strict';
    var timeout;
    return function () {
        var context = this;
        var args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    }
};

module.exports = {
   name: 'groundsList',
   data: function() {
     return{
       grounds: [],
       rows: [],
       dtGrounds: null,
       regions: [],
       selected_region: "All",
       selected_status: "All"
     }
   },
   watch: {
       grounds: function(){
           let vm = this;
       },
       selected_region: function () {
         let vm = this;
         console.log(vm.selected_region);
         vm.dtGrounds.columns(3).search(vm.selected_region).draw();
       }
   },
   methods: {
       flagFormat: function(flag){
           return flag ? 'Yes' : 'No'
       },
       update: function() {
         var vm = this;
         var url = '/api/regions.json';
          console.log('AJAX '+url)
          $.ajax({
              url: url,
              dataType: 'json',
              success: function(data, stat, xhr) {
                  console.log(data);
                  vm.regions = data;
              }
          });
       }
   },
   mounted: function () {
     console.log('hello');
       this.dtGrounds = $('#groundsTable').DataTable({
           language: {
               processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
           },
           ajax:{
             "url":"/api/campgrounds.json",
             "dataSrc": ''
           },
           columns:[
             {
               "data":"id",
             },
             { "data":"name"},
             {
               "data": "active",
               "mRender": function (data, type, full)
               {
                   var status = (data == true) ? "Open" : "Temporarily Closed";
                   var column = "<td > __Status__</td>";
                   return column.replace('__Status__', status);
               }
             },
             { "data":"region"},
             {
               "data":"dog_permitted",
               "mRender": function (data, type, full)
               {
                   var permitted = (data == true) ? 'Yes' : 'No';
                   var column = "<td >__Perm__</td>";
                   return column.replace('__Perm__', permitted);
               }
             },
             {
               "data":"dog_permitted", //TODO replace with campfire"data":"campfire",
               "mRender": function (data, type, full)
                {
                   var permitted = (data == true) ? 'Yes' : 'No';
                   var column = "<td >__Perm__</td>";
                   return column.replace('__Perm__', permitted);
                 }
             },
             {

              "mRender": function (data, type, full)
               {
                   var id = full.id;
                   return '<a href="#">Edit Campground Details</a>';
               }
             },
          ],
           processing: true
       });
       this.update();
   }
};

</script>
