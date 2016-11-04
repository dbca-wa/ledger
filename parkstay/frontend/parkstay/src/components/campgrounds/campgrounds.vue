<template>
   <div id="groundsList">
      <pkCgStatus ></pkCgStatus>
      <pkCgAdd></pkCgAdd>
      <div class="panel-group" id="returns-accordion" role="tablist" aria-multiselectable="true">
      <div class="panel panel-default" id="returns">
           <div class="panel-heading" role="tab" id="returns-heading">
               <h4 class="panel-title">
                   <a role="button" data-toggle="collapse" href="#returns-collapse"
                      aria-expanded="true" aria-controls="collapseOne">
                       <h3>{{title}}</h3>
                   </a>
               </h4>
           </div>
           <div id="returns-collapse" class="panel-collapse collapse in" role="tabpanel"
                aria-labelledby="returns-heading">
               <div class="panel-body">
                  <div id="groundsList">
                    <form class="form" id="campgrounds-filter-form">
                        <div class="col-md-8">
                           <div class="col-md-3">
                                <div class="form-group">
                                    <label for="campgrounds-filter-status">Status: </label>
                                    <select v-model="selected_status" class="form-control" name="status" id="campgrounds-filter-status">
                                        <option value="All">All</option>
                                        <option value="Open">Open</option>
                                        <option value="Temporarily Closed">Temporarily Closed</option>
                                    </select>
                                </div>
                           </div>
                           <div class="col-md-3">
                                <div class="form-group">
                                    <label for="applications-filter-region">Region: </label>
                                    <select class="form-control" v-model="selected_region" id="campgrounds-filter-region">
                                        <option value="All" selected="true">All</option>
                                        <option v-for="region in regions" v-bind:value=region.name>{{ region.name }}</option>
                                    </select>
                                </div>
                           </div>
                        </div>
                        <div class="col-md-4">
                           <div class="form-group pull-right">
                               <a style="margin-top: 20px;"class="btn btn-primary" @click="showAddCampground()">Add Campground</a>
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
               </div>
           </div>
      </div>
   </div>
   </div>

</template>

<script>
import {$, DataTable, DataTableBs,DataTableRes} from '../../hooks'
import pkCgStatus from './openclose.vue'
import pkCgAdd from './addCampground.vue'
module.exports = {
    name: 'pk-campgrounds',
    data: function() {
        return{
            grounds: [],
            rows: [],
            dtGrounds: null,
            regions: [],
            title: 'Campgrounds',
            selected_status: 'All',
            selected_region: 'All',
            isOpenAddCampground: false,
            isOpenStatus: false
        }
    },
    components:{ pkCgStatus, pkCgAdd },
    watch:{
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
            console.log('AJAX '+url)
            $.ajax({
                url: url,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    console.log(data);
                    vm.regions = data;
                }
            });
        },
        updateTable: function(){
            var vm = this;
            vm.dtGrounds.draw();
        },
        showAddCampground: function(){
            this.isOpenAddCampground = true;
        },
        openDetail: function (cg_id) {
           this.$router.push({name:'cg_detail',params:{id:cg_id}});
        }
    },
    mounted: function () {
        var vm = this;
        vm.dtGrounds = $('#groundsTable').DataTable({
            language: {
                processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
            },
            responsive:true,
            columnDefs: [
               { responsivePriority: 1, targets: 1 },
               { responsivePriority: 2, targets: 6 }
            ],
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
                    var column = "<td >__Status__</td>";
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
                    var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit Campground Details</a></td>";
                    return column.replace('__ID__', id);
                }
            },
          ],
            processing: true
       });
       vm.update();
       vm.dtGrounds.on('click','a[data-campground]', function(e){
          e.preventDefault();
          var id = $(this).attr('data-campground');
          vm.openDetail(id);
       });

   }
};
$('a[data-campgroud]').on('click',function(event){
   event.preventDefault();
   var id = $(this).attr('data-campgroud');
   console.log(id);
});

</script>
