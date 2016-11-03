<template>

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
                                    <select @change="updateTable()" v-model="status" class="form-control" name="status" id="campgrounds-filter-status">
                                        <option value="All">All</option>
                                        <option value="Open">Open</option>
                                        <option value="Temporarily Closed">Temporarily Closed</option>
                                    </select>
                                </div>
                           </div>
                           <div class="col-md-3">
                                <div class="form-group">
                                    <label for="applications-filter-region">Region: </label>
                                    <select @change="updateTable()" class="form-control" v-model="selected_region" id="campgrounds-filter-region">
                                        <option value="All" selected="true">All</option>
                                        <option v-for="region in regions" v-bind:value=region.name>{{ region.name }}</option>
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
               </div>
           </div>
      </div>
   </div>



</template>

<script>
import {$, DataTable, DataTableBs} from '../../hooks'
//import openclose from 'openclose'

$.fn.dataTable.ext.search.push(
     function( settings, data, dataIndex ) {
         var _stat = $('#campgrounds-filter-status').val();
         var status = data[2]; // use data for the status column
         if ( _stat === status ||
             _stat === "All" )
         {
             return true;
         }
         return false;
     }
 );
$.fn.dataTable.ext.search.push(
     function( settings, data, dataIndex ) {
         var _reg = $('#campgrounds-filter-region').val();
         var region = data[3]; // use data for the region column
         if ( _reg === region ||
             _reg === "All" )
         {
             return true;
         }
         return false;
     }
 );
module.exports = {
    name: 'groundsList',
    data: function() {
        return{
            grounds: [],
            rows: [],
            dtGrounds: null,
            regions: [],
            status: 'All',
            selected_region: 'All',
            title: 'Campgrounds'
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
        }
    },
    mounted: function () {
        var vm = this;
        vm.dtGrounds = $('#groundsTable').DataTable({
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
                    return '<a href="#">Edit Campground Details</a>';
                }
            },
          ],
            processing: true
       });
       vm.update();
   }
};

</script>
