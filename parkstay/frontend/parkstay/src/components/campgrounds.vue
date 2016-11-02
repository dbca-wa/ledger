<template>
  <div id="groundsList">
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
       dtGrounds: null
     }
   },
   watch: {
       grounds: function(){
           let vm = this;
           /*
           vm.grounds.forEach(function (g) {
               let row = [];
               let status = false;

               row.push(g.id);
               row.push(g.name);
               // Status
               status = g.active;
               status ? row.push('Open') : row.push('Temporarily Closed');
               row.push(g.region);
               row.push(vm.flagFormat(g.dog_permitted));
               row.push('No');
               // Action
               let action = '<a href={{ground.id}}>Edit Campground Details</a><br/>';
               status ? row.push(action + '<a href="">(Temporarily) Close Campground</a>') :  row.push(action + '<a href="">Open Campground</a>')
               vm.rows.push(row);
           });
           console.log(vm.dtGrounds);
           vm.dtGrounds.clear();
           vm.dtGrounds.rows.add(vm.rows);
           vm.dtGrounds.draw();
           vm.dtGrounds.processing = false;
           */
       }
   },
   methods: {
       flagFormat: function(flag){
           return flag ? 'Yes' : 'No'
       },
       update: function() {
           var vm = this;
           /*
           vm.dtGrounds.processing = true;
           debounce(function() {
               var url = 'http://0.0.0.0:8888/api/campgrounds.json';
               //console.log('AJAX '+url)
               $.ajax({
                   url: url,
                   dataType: 'json',
                   success: function(data, stat, xhr) {
                       console.log(data);
                       vm.grounds = data;
                   }
               });
           }, 500)();
           */
       }
   },
   mounted: function () {
     console.log('hello');
       this.dtGrounds = $('#groundsTable').DataTable({
           language: {
               processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
           },
           ajax:{
             "url":"http://0.0.0.0:8888/api/campgrounds.json",
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
