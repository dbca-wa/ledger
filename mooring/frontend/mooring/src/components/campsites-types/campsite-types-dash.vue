<template lang="html">
    <div id="campsite-type-dash">
       <div class="panel panel-default" id="applications">
         <div class="panel-heading" role="tab" id="applications-heading">
             <h4 class="panel-title">
                 <a role="button" data-toggle="collapse" href="#applications-collapse"
                    aria-expanded="false" aria-controls="applications-collapse">
                     <h3>Camp Site Types</h3>
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
                              <router-link :to="{name:'campsite-type'}" style="margin-top: 20px;" class="btn btn-primary table_btn" >Add Camp Site Type</router-link>
                          </div>
                      </div>
                  </form>
                  <datatable :dtOptions="dt_options" :dtHeaders="dt_headers" ref="campsite_type_table" id="campsite-type-table"></datatable>
              </div>
            </div>
          </div>
       </div>
    <confirmbox id="deleteCampsiteType" :options="deleteCampsiteTypePrompt"></confirmbox>
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
        datatable,
        confirmbox,
    },
    computed: {

    },
    data: function() {
        let vm = this;
        return {
            selected_status:'All',
            deleteCampsiteType: null,
            deleteCampsiteTypePrompt: {
                icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
                message: "Are you sure you want to Delete this campsite type",
                buttons: [{
                    text: "Delete",
                    event: "delete",
                    bsColor: "btn-danger",
                    handler: function() {
                        vm.deleteCampsiteTypeRecord(vm.deleteCampsiteType);
                        vm.deleteCampsiteType = null;
                    },
                    autoclose: true,
                }],
                id: 'deleteCampsiteType'
            },
            dt_headers:["Name","Status","Action"],
            dt_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                processing:true,
                columnDefs: [
                    {
                    responsivePriority: 1,
                    targets: 0
                    },
                    {
                    responsivePriority: 2,
                    targets: 1
                    },
                    {
                        responsivePriority: 3,
                        targets: 2
                    }
                ],
                ajax: {
                    "url": api_endpoints.campsite_classes,
                    "dataSrc": ''
                },
                columns: [
                    {
                        "data": "name",
                        mRender:function (data,type,full) {
                            var max_length = 120;
                            var popover_class = (data.length > max_length) ? "class='name_popover'" : "";
                            var name = (data.length > max_length) ? data.substring(0,max_length-1)+'...' : data;
                            var column = '<td> <div '+popover_class+'tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >'+ name +'</div></td>';
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
                            if (!full.deleted){
                                var column = "<td ><a href='#' class=\"detailRoute\" data-campsite-type='__ID__'> Edit</a> </br> ";
                                column += "<a href='#' class=\"deleteCT\" data-campsite-type='__ID__'> Delete</a> </td>";
                                return column.replace(/__ID__/g, full.id);
                            }
                            return '';
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
                vm.$refs.campsite_type_table.vmDataTable.columns(1).search(vm.selected_status).draw();
            } else {
                vm.$refs.campsite_type_table.vmDataTable.columns(1).search('').draw();
            }
        }
    },
    methods: {
        deleteCampsiteTypeRecord: function(id) {
            var vm = this;
            var url = api_endpoints.campsite_class(id);
            $.ajax({
                method: "DELETE",
                url: url,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}
            }).done(function(msg) {
                vm.$refs.campsite_type_table.vmDataTable.ajax.reload();
            });
        },
        goBack: function() {
            helpers.goBack(this);
        },
        attachTableEventListeners: function() {
            let vm = this;
            vm.$refs.campsite_type_table.vmDataTable.on('click', '.detailRoute', function(e) {
                e.preventDefault();
                var id = $(this).data('campsite-type');
                vm.$router.push({
                    name: 'campsite-type-detail',
                    params: {
                        campsite_type_id: id
                    }
                });
            });
            vm.$refs.campsite_type_table.vmDataTable.on('click','.deleteCT', function(e) {
                e.preventDefault();
                var id = $(this).data('campsite-type');
                vm.deleteCampsiteType = id;
                bus.$emit('showAlert', 'deleteCampsiteType');
            });
        }
    },
    mounted: function() {
        let vm = this;
        helpers.namePopover($,vm.$refs.campsite_type_table.vmDataTable);
        vm.attachTableEventListeners();
    }
}

</script>

<style lang="css">
    .name_popover{
        padding: 10px;
        cursor: pointer;
    }
</style>
