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
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label for="applications-filter-region">District: </label>
                                        <select class="form-control" v-model="selected_district">
                                            <option value="All">All</option>
                                            <option v-for="district in districts" :value="district.name">{{ district.name }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="form-group">
                                        <label for="applications-filter-region">Park: </label>
                                        <select class="form-control" v-model="selected_park">
                                            <option value="All">All</option>
                                            <option v-for="park in parks" :value="park.name">{{ park.name }}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="form-group pull-right">
                                    <a style="margin-top: 20px;" class="btn btn-primary" @click="addCampground()">Add Mooring</a>
                                    <a style="margin-top: 20px;" class="btn btn-primary" @click="showBulkClose = true">Close Moorings</a>
                                </div>
                            </div>
                        </form>
                        <datatable :dtHeaders="['Mooring','Status','Region','District','Park','Action']" :dtOptions="dtoptions" ref="dtGrounds" id="campground-table" ></datatable>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <bulk-close :show="showBulkClose" ref="bulkClose"/>
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
import bulkClose from '../utils/closureHistory/bulk-close.vue'
import {bus} from '../utils/eventBus.js'
import { mapGetters } from 'vuex'
module.exports = {
    name: 'pk-campgrounds',
    data: function() {
        let vm =this;
        return {
            grounds: [],
            rows: [],
            title: 'Moorings',
            selected_status: 'All',
            selected_region: 'All',
            selected_park: 'All',
            selected_district: 'All',
            isOpenAddCampground: false,
            isOpenOpenCG: false,
            isOpenCloseCG: false,
            showBulkClose:false,
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
                    "url": api_endpoints.campgrounds_datatable,
                    "dataSrc": ''
                },
                columns: [{
                    "data": "name"
                }, {
                    "data": "active",
                    "mRender": function(data, type, full) {
                        var status = (data == true) ? "Open" : "Temporarily Closed";
                        var column = "<td >__Status__</td>";
                        column += data ? "" : "<br/><br/>"+full.current_closure  ;
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
//                        var addBooking = "<br/><a href='#' class='addBooking' data-campground=\"__ID__\" >Add Booking</a>";
                        var addBooking = "";
                        // var availability_admin = "<br/><a target='_blank' href='/availability_admin/?site_id=__ID__' >Availability</a>";
                        var availability_admin = "<br/><a target='_blank' href='/availability/?site_id=__ID__&vessel_size=0' >Availability</a>";
                        var column = "";

                        if (full.active) {
                            var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit </a><br/><a href='#' class='statusCG' data-status='close' data-campground=\"__ID__\" > Close </a>";
                        } else {
                            var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit </a><br/><a href='#' class='statusCG' data-status='open' data-campground=\"__ID__\" data-current_closure=\"__Current_Closure__\">Open</a>";
                        }

                        column += full.mooring_type == '0' ? addBooking : "";
                        column += full.mooring_type == '0' ? availability_admin:"";
                        column += "</td>";
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
        datatable,
        "bulk-close":bulkClose,
    },
    computed:{
       ...mapGetters([
         'regions',
         'districts',
         'parks'
       ]),
    },
    watch: {
        showBulkClose:function () {
            this.$refs.bulkClose.isModalOpen = this.showBulkClose;
            this.$refs.bulkClose.initSelectTwo();
        },
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
        },
        selected_district: function() {
            let vm = this;
            if (vm.selected_district != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(3).search(vm.selected_district).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(3).search('').draw();
            }
        },
        selected_park: function() {
            let vm = this;
            if (vm.selected_park != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(4).search(vm.selected_park).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(4).search('').draw();
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
            if (vm.regions.length == 0) {
                vm.$store.dispatch("fetchRegions");
            }
        },
        fetchParks: function() {
            let vm = this;
            if (vm.parks.length == 0) {
                vm.$store.dispatch("fetchParks");
            }
        },
        fetchDistricts: function() {
            let vm = this;
            if (vm.districts.length == 0) {
                vm.$store.dispatch("fetchDistricts");
            }
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
        vm.fetchParks();
        vm.fetchDistricts();
    }
};
</script>
