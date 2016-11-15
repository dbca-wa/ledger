<template lang="html">

   <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
      <div class="panel panel-default" id="applications">
        <div class="panel-heading" role="tab" id="applications-heading">
            <h4 class="panel-title">
                <a role="button" data-toggle="collapse" href="#applications-collapse"
                   aria-expanded="false" aria-controls="applications-collapse">
                    <h3>{{title}}</h3>
                </a>
            </h4>
        </div>
        <div id="applications-collapse" class="panel-collapse collapse in" role="tabpanel"
             aria-labelledby="applications-heading">
            <div class="panel-body">
               <div class="col-lg-12">
                  <div class="row">
                      <campgroundAttr :createCampground=false :campground="campground">
                      </campgroundAttr>
                  </div>
                  <div class="row">
                     <div class="well">
                        <h1>Price History</h1>
                     </div>
                  </div>
                  <div class="row">
                     <div class="well">
                        <h1>Closure History</h1>
                        <datatable :dtHeaders ="ch_headers" :dtOptions="ch_options" id="cg_table"></datatable>
                     </div>
                  </div>
               </div>
            </div>
         </div>
      </div>
      <div class="panel panel-default" id="applications">
        <div class="panel-heading" role="tab" id="applications-heading">
            <h4 class="panel-title">
                <a role="button" data-toggle="collapse" href="#campsites"
                   aria-expanded="false" aria-controls="collapseOne">
                    <h3>Campsites</h3>
                </a>
            </h4>
        </div>
        <div class="panel-collapse collapse in" role="tabpanel"
             aria-labelledby="applications-heading" id="campsites">
            <div class="panel-body">
               <div class="col-lg-12">
                  <div class="row">
                     <div class="well">
                        <datatable :dtHeaders ="cs_headers" :dtOptions="cs_options" id="cs_table"></datatable>
                     </div>
                  </div>
               </div>
            </div>
        </div>
    </div>
    <confirmbox id="deleteRange" :options="deletePrompt"></confirmbox>
   </div>

</template>

<script>
import datatable from '../utils/datatable.vue'
import campgroundAttr from './campground-attr.vue'
import confirmbox from '../utils/confirmbox.vue'
import {
    bus
}
from '../utils/eventBus.js'
import {
    $,
    Moment,
    api_endpoints
}
from '../../hooks.js'

export default {
    name: 'campground',
    components: {
        datatable,
        campgroundAttr,
        confirmbox
    },
    data: function() {
        let vm = this;
        return {
            campground: {
                address:{}
            },
            deleteRange: null,
            ch_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                ajax: {
                    url: api_endpoints.status_history(this.$route.params.id),
                    dataSrc: ''
                },
                columns: [{
                    data: 'range_start',
                    mRender: function(data, type, full) {
                        return Moment(data).format('MMMM Do, YYYY');
                    }

                }, {
                    data: 'range_end',
                    mRender: function(data, type, full) {
                        if (data) {
                            return Moment(data).add(1, 'day').format('MMMM Do, YYYY');
                        }
                        else {
                            return '';
                        }
                    }

                }, {
                    data: 'status'
                }, {
                    data: 'details'
                }, {
                    data: 'editable',
                    mRender: function(data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editRange' data-range=\"__ID__\" >Edit</a><br/><a href='#' class='deleteRange' data-range=\"__ID__\" >Delete</a></td>";
                            return column.replace(/__ID__/g, id);
                        }
                        else {
                            return "";
                        }
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            ch_headers: ['Closure Start', 'Reopen', 'Closure Reason', 'Details', 'Action'],
            title: 'Campground',
            cs_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                ajax: {
                    url: api_endpoints.campgroundCampsites(this.$route.params.id),
                    dataSrc: ''
                },
                columnDefs: [{
                    responsivePriority: 1,
                    targets: 0
                }, {
                    responsivePriority: 2,
                    targets: 4
                }, {
                    responsivePriority: 3,
                    targets: 2
                }, {
                    responsivePriority: 4,
                    targets: 3
                }],
                columns: [{
                    data: 'name'
                }, {
                    data: 'type'
                }, {
                    data: 'active',
                    mRender: function(data, type, full) {
                        return data ? 'Open' : 'Closed'
                    }
                }, {
                    data: 'price'
                }, {
                    "mRender": function(data, type, full) {
                        var id = full.id;
                        if (full.status) {
                            var column ="<td ><a href='#' class='detailRoute' data-campsite=\"__ID__\" >Edit Campsite Details</a><br/><a href='#' class='statusCS' data-status='close' data-campsite=\"__ID__\" >(Temporarily) Close Campsite </a></td>";
                        }
                        else {
                            var column = "<td ><a href='#' class='detailRoute' data-campsite=\"__ID__\" >Edit Campsite Details</a><br/>";
                            if ( full.campground_open ){
                                column += "<a href='#' class='statusCS' data-status='close' data-campsite=\"__ID__\" >(Temporarily) Close Campsite </a></td>";
                            }
                        }

                        return column.replace(/__ID__/g, id);
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            cs_headers: ['Campsite Id', 'Type', 'Status', 'Price', 'Action'],
            deletePrompt: {
                icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
                message: "Are you sure you want to Delete!!!",
                buttons: [{
                    text: "Delete",
                    event: "delete",
                    bsColor: "btn-danger",
                    handler: function() {
                        vm.deleteBookingRange(vm.deleteRange);
                        vm.deleteRange = null;
                    },
                    autoclose: true
                }]
            },

        }
    },
    methods: {
        deleteBookingRange: function(id) {
            var vm = this;
            var url = api_endpoints.deleteBookingRange(id);
            $.ajax({
                method: "DELETE",
                url: url,
            }).done(function(msg) {
                vm.$children[1].vmDataTable.ajax.reload();
            });
        },
        fetchCampground:function () {
            let vm =this;
            $.ajax({
                url: api_endpoints.campground(vm.$route.params.id),
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.campground = data;
                }
            });
        }

    },
    mounted: function() {
        var vm = this;
        vm.$children[1].vmDataTable.on('click', '.deleteRange', function(e) {
            e.preventDefault();
            var id = $(this).attr('data-range');
            vm.deleteRange = id;
            bus.$emit('showAlert', 'deleteRange');
        });
        vm.fetchCampground();
    }
}

</script>

<style lang="css">
.well{
   background-color: #fff;
}
.btn{
   margin-bottom: 10px;
}
</style>
