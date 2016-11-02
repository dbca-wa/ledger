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
    <table class="hover table table-striped table-bordered dt-responsive nowrap" cellspacing="0" width="100%" id="groundsTable">
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
var DataTableRes = require( 'datatables.net-responsive-bs' )();

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
         if(vm.selected_region != 'All'){
           vm.dtGrounds.columns(3).search(vm.selected_region).draw();
         }else{
           vm.dtGrounds.columns(3).search('').draw();
         }
       },
       selected_status: function () {
         let vm = this;
         if(vm.selected_status != 'All'){
           vm.dtGrounds.columns(2).search(vm.selected_status).draw();
         }else{
           vm.dtGrounds.columns(2).search('').draw();
         }
       }
   },
   methods: {
       flagFormat: function(flag){
           return flag ? 'Yes' : 'No'
       },
       update: function() {
         var vm = this;
         var url = '/api/regions.json';
          $.ajax({
              url: url,
              dataType: 'json',
              success: function(data, stat, xhr) {
                  vm.regions = data;
              }
          });
       }
   },
   mounted: function () {
      var table =$('#groundsTable');
      let vm = this;
       this.dtGrounds = $(table).DataTable({
         responsive: true,
          columnDefs: [
            { responsivePriority: 1, targets: 1 },
            { responsivePriority: 2, targets: 2 }
           ],
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
                   return vm.flagFormat(data);
               }
             },
             {
               "data":"dog_permitted", //TODO replace with campfire"data":"campfire",
               "mRender": function (data, type, full)
                {
                    return vm.flagFormat(data);
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
