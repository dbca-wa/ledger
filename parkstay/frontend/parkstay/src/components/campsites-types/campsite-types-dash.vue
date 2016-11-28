<template lang="html">
    <div id="campsite-type-dash">
       <div class="panel panel-default" id="applications">
         <div class="panel-heading" role="tab" id="applications-heading">
             <h4 class="panel-title">
                 <a role="button" data-toggle="collapse" href="#applications-collapse"
                    aria-expanded="false" aria-controls="applications-collapse">
                     <h3>Campsite Types</h3>
                 </a>
             </h4>
         </div>
         <div id="applications-collapse" class="panel-collapse collapse in" role="tabpanel"
              aria-labelledby="applications-heading">
            <div class="panel-body">
              <div id="groundsList">
                  <form class="form" id="campgrounds-filter-form">
                      <div class="col-md-8">
                          <div class="col-md-6">
                              <div class="form-group">
                                  <label for="campgrounds-filter-status">Status: </label>
                                  <select v-model="selected_status" class="form-control">
                                      <option value="All">All</option>
                                      <option value="Active">Active</option>
                                      <option value="Deleted">Deleted</option>
                                  </select>
                              </div>
                          </div>
                      </div>
                      <div class="col-md-4">
                          <div class="form-group pull-right">
                              <router-link :to="{name:'campsite-type'}" style="margin-top: 20px;" class="btn btn-primary" >Add Campsite Type</router-link>
                          </div>
                      </div>
                  </form>
                  <datatable :dtOptions="dt_options" :dtHeaders="dt_headers" ref="campsite_type_table" id="campsite-type-table"></datatable>
              </div>
            </div>
          </div>
       </div>
   </div>
</template>

<script>
import {
    $,
    api_endpoints,
    helpers,
    Moment,
    bus
}
from '../../hooks.js';
import datatable from '../utils/datatable.vue'
import confirmbox from '../utils/confirmbox.vue'
import loader from '../utils/loader.vue'
import closureHistory from '../utils/closureHistory.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
export default {
    name: 'campsite',
    components: {
        datatable
    },
    computed: {

    },
    data: function() {
        let vm = this;
        return {
            selected_status:'All',
            dt_headers:["Campsite ID", "Campsite Type Name","Status","Action"],
            dt_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                processing:true,
                columnDefs: [
                    {
                    responsivePriority: 1,
                    targets: 1
                    },
                    {
                    responsivePriority: 2,
                    targets: 2
                    },
                    {
                        responsivePriority: 3,
                        targets: 3
                    }
                ],
                ajax: {
                    "url": api_endpoints.campsite_classes,
                    "dataSrc": ''
                },
                columns: [
                    {
                        "data": "id",
                    },
                    {
                        "data": "name",
                        mRender:function (data,type,full) {
                            var max_length = 25;
                            var name = (data.length > max_length) ? data.substring(0,max_length-1)+'...' : data;
                            var column = '<td> <div class="name_popover" tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >'+ name +'</div></td>';
                            return column.replace('__NAME__', data);
                        }
                    },
                    {
                        "data": "deleted",
                        "mRender": function(data, type, full) {
                            var status = (!data) ? "Active" : "Deleted";
                            var column = "<td >__Status__</td>";
                            return column.replace('__Status__', status);
                        }
                    },
                    {
                        "mRender": function(data, type, full) {
                            var id = full.id;
                            var column = "<td ><a href='__URL__' data-id='__ID__'> Edit</a> </br> ";
                            if (!full.deleted){
                                column += "<a href='__URL__' data-id='__ID__'> Delete</a> </td>";
                            }
                            return column.replace(/__URL__/g, full.url);
                        }
                    }
                ]
            },
        };
    },
    watch: {
        selected_status: function() {
            let vm = this;
            if (vm.selected_status != 'All') {
                vm.$refs.campsite_type_table.vmDataTable.columns(2).search(vm.selected_status).draw();
            } else {
                vm.$refs.campsite_type_table.vmDataTable.columns(2).search('').draw();
            }
        }
    },
    methods: {
        goBack: function() {
            helpers.goBack(this);
        },
        namePopover:function () {
            let vm = this;
            vm.$refs.campsite_type_table.vmDataTable.on('mouseover','.name_popover',function (e) {
                $(this).popover('show');
                $(this).on('mouseout',function () {
                    $(this).popover('hide');
                })

            });
        }

    },
    mounted: function() {
        let vm = this;
        vm.namePopover();

    }
}

</script>

<style lang="css">
    .name_popover{
        padding: 10px;
        cursor: pointer;
    }
</style>
