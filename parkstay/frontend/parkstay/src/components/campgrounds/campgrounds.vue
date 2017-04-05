<template>
<div id="groundsList">
    <pkCgClose></pkCgClose>
    <pkCgOpen></pkCgOpen>
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
            <div id="returns-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="returns-heading">
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
                                        <select class="form-control" v-model="selected_region">
                                            <option value="All">All</option>
                                            <option v-for="region in regions" :value="region.name">{{ region.name }}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="form-group pull-right">
                                    <a style="margin-top: 20px;" class="btn btn-primary" @click="addCampground()">Add Campground</a>
                                </div>
                            </div>
                        </form>
                        <datatable :dtHeaders="['Campground','Status','Region','District','Park','Action']" :dtOptions="dtoptions" ref="dtGrounds" id="campground-table" ></datatable>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script>
import {
    $,
    api_endpoints
} from '../../hooks'
import datatable from '../utils/datatable.vue'
import pkCgClose from './closeCampground.vue'
import pkCgOpen from './openCampground.vue'
import {bus} from '../utils/eventBus.js'
module.exports = {
    name: 'pk-campgrounds',
    data: function() {
        let vm =this;
        return {
            grounds: [],
            rows: [],
            regions: [],
            title: 'Campgrounds',
            selected_status: 'All',
            selected_region: 'All',
            isOpenAddCampground: false,
            isOpenOpenCG: false,
            isOpenCloseCG: false,
            dtoptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,

                columnDefs: [{
                    responsivePriority: 1,
                    targets: 0
                }, {
                    responsivePriority: 2,
                    targets: 3
                }],
                ajax: {
                    "url": api_endpoints.campgrounds+"?formatted=True",
                    "dataSrc": ''
                },
                columns: [{
                    "data": "name"
                }, {
                    "data": "active",
                    "mRender": function(data, type, full) {
                        var status = (data == true) ? "Open" : "Temporarily Closed";
                        var column = "<td >__Status__</td>";
                        return column.replace('__Status__', status);
                    }
                }, {
                    "data": "region"
                },{
                    "data": "district"
                },{
                    "data": "park"
                }, {
                    "mRender": function(data, type, full) {
                        var id = full.id;
                        var addBooking = "<br/><a href='#' class='addBooking' data-campground=\"__ID__\" >Add Booking</a>";
                        if (full.active) {
                            var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit </a><br/><a href='#' class='statusCG' data-status='close' data-campground=\"__ID__\" > Close </a>\
                            "+addBooking+"</td>";
                        } else {
                            var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit </a><br/><a href='#' class='statusCG' data-status='open' data-campground=\"__ID__\" data-current_closure=\"__Current_Closure__\">Open</a>\
                            "+addBooking+"</td>";
                        }
                        column = column.replace(/__Current_Closure__/,full.current_closure);
                        return column.replace(/__ID__/g, id);
                    }
                }, ],
                processing: true
            }
        }
    },
    components: {
        pkCgClose,
        pkCgOpen,
        datatable
    },
    watch: {
        selected_region: function() {
            let vm = this;
            if (vm.selected_region != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(2).search(vm.selected_region).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(2).search('').draw();
            }
        },
        selected_status: function() {
            let vm = this;
            if (vm.selected_status != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(1).search(vm.selected_status).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(1).search('').draw();
            }
        }
    },
    methods: {
        flagFormat: function(flag) {
            return flag ? 'Yes' : 'No'
        },
        update: function() {
            var vm = this;
            var url =  api_endpoints.regions;
            $.ajax({
                url: url,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.regions = data;
                }
            });
        },
        updateTable: function() {
            var vm = this;
            vm.$refs.dtGrounds.vmDataTable.draw();
        },
        showOpenCloseCG: function() {
            this.isOpenCloseCG = true;
        },
        showOpenOpenCG: function() {
            this.isOpenOpenCG = true;
        },
        openDetail: function(cg_id) {
            this.$router.push({
                name: 'cg_detail',
                params: {
                    id: cg_id
                }
            });
        },
        addCampground: function(cg_id) {
            this.$router.push({
                name: 'cg_add',
            });
        },
        fetchRegions: function() {
            let vm = this;
            $.get(api_endpoints.regions,function(data){
                vm.regions = data;
            });
        }
    },
    mounted: function() {
        var vm = this;
        vm.$refs.dtGrounds.vmDataTable.on('click', '.detailRoute', function(e) {
            e.preventDefault();
            var id = $(this).attr('data-campground');
            vm.openDetail(id);
        });
        vm.$refs.dtGrounds.vmDataTable.on('click', '.statusCG', function(e) {
            e.preventDefault();
            var id = $(this).attr('data-campground');
            var status = $(this).attr('data-status');
            var current_closure = $(this).attr('data-current_closure') ? $(this).attr('data-current_closure') : '';
            var data = {
                'status': status,
                'id': id,
                'closure': current_closure
            }
            bus.$emit('openclose', data);
            if (status === 'open'){
                vm.showOpenOpenCG();
            }else if (status === 'close'){
                vm.showOpenCloseCG();
            }
        });
        vm.$refs.dtGrounds.vmDataTable.on('click', '.addBooking', function(e) {
            e.preventDefault();
            var id = $(this).attr('data-campground');
            vm.$router.push({
                name: 'add-booking',
                params: {
                    "cg": id
                }
            });
        });
         bus.$on('refreshCGTable', function(){
            vm.$refs.dtGrounds.vmDataTable.ajax.reload();
        });
        vm.fetchRegions();
    }
};
</script>
