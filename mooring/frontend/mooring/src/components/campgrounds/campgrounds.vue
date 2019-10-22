<template>
<div id="groundsList">
    <pkCgClose></pkCgClose>
    <pkCgOpen></pkCgOpen>
    <div class="panel-group" id="returns-accordion" role="tablist" aria-multiselectable="true">
        <div class="row">
            <div class="panel panel-default" id="returns">
                <div class="panel-heading" role="tab" id="returns-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#returns-collapse"
                            aria-expanded="true" aria-controls="collapseOne" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">{{title}}</h3>
                                <span id="collapse_returns_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
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
                                        <a style="margin-top: 20px;" v-if="invent" class="btn btn-primary" @click="addCampground()">Add Mooring</a>
                                        <a style="margin-top: 20px;" v-if="invent" class="btn btn-primary" @click="showBulkClose = true">Close Moorings</a>
                                        <a style="margin-top: 20px;" v-if="invent" class="btn btn-primary" @click="showBulkBookingPeriod = true">Set Periods</a>
                                    </div>
                                </div>
                            </form>
                            <datatable :dtHeaders="['Mooring','Type', 'Status','Region','District','Park','Action']" :dtOptions="dtoptions" ref="dtGrounds" id="campground-table" ></datatable>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <bulk-close :show="showBulkClose" ref="bulkClose"/>
    <bulk-booking :show="showBulkBookingPeriod" ref="bulkBooking"/>
</div>
</template>

<script>
import {
    $,
    api_endpoints
} from '../../hooks'
import alert from '../utils/alert.vue'
import datatable from '../utils/datatable.vue'
import pkCgClose from './closeCampground.vue'
import pkCgOpen from './openCampground.vue'
import bulkClose from '../utils/closureHistory/bulk-close.vue'
import bulkBooking from '../utils/priceHistory/bulkPriceHistory.vue'
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
            showBulkBookingPeriod: false,
            invent: false,
            dtoptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                fnInitComplete: function(oSettings, json){
                    if(!vm.invent){
                        vm.$refs.dtGrounds.vmDataTable.rows().every(function(){
                            var rowdata = this.data();
                            rowdata['noinvent'] = true;
                            this.data(rowdata);
                        });
                    }
                },
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
                    "data": "mooring_physical_type",
                    "mRender": function(data, type, full){
                        if (data == 0){
                            return "Mooring"
                        } else if (data == 1) {
                            return "Jetty Pen"
                        } else {
                            return "Beach Pen"
                        }
                    }
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
                    data: 'editable',
                    mRender: function(data, type, full) {
                        var id = full.id;
//                        var addBooking = "<br/><a href='#' class='addBooking' data-campground=\"__ID__\" >Add Booking</a>";
                        var addBooking = "";
                        var today = vm.date_today(0);
                        var today_week_later = vm.date_today(7);
                        // var availability_admin = "<br/><a target='_blank' href='/availability_admin/?site_id=__ID__' >Availability</a>";
                        var availability_admin = "<a target='_blank' href='/availability2/?site_id=__ID__&arrival="+today+"&departure="+today_week_later+"&gear_type=all&num_adult=2&num_child=0&num_concession=0&num_infant=0&vessel_size=0.1&vessel_draft=0.1&vessel_beam=0.1&vessel_weight=0.1' >Availability</a>";
                        var column = "";
                        if(full.noinvent){
                            column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >View</a><br/>";
                        } else {
                            column = "<td ><a href='__ID__' class='detailRoute' data-campground=\"__ID__\" >Edit</a><br/>";
                            if (full.active) {
                                column += "<a href='#' class='statusCG' data-status='close' data-campground=\"__ID__\" > Close </a><br/>";
                            } else {
                                column += "<a href='#' class='statusCG' data-status='open' data-campground=\"__ID__\" data-current_closure=\"__Current_Closure__\">Open</a><br/>";
                            }
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
        alert,
        pkCgClose,
        pkCgOpen,
        datatable,
        "bulk-close":bulkClose,
        "bulk-booking": bulkBooking
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
        showBulkBookingPeriod: function() {
            this.$refs.bulkBooking.isModalOpen = this.showBulkBookingPeriod;
            this.$refs.bulkBooking.initSelectTwo();
        },
        selected_region: function() {
            let vm = this;
            if (vm.selected_region != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(3).search(vm.selected_region).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(3).search('').draw();
            }
        },
        selected_status: function() {
            let vm = this;
            if (vm.selected_status != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(2).search(vm.selected_status).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(2).search('').draw();
            }
        },
        selected_district: function() {
            let vm = this;
            if (vm.selected_district != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(4).search(vm.selected_district).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(4).search('').draw();
            }
        },
        selected_park: function() {
            let vm = this;
            if (vm.selected_park != 'All') {
                vm.$refs.dtGrounds.vmDataTable.columns(5).search(vm.selected_park).draw();
            } else {
                vm.$refs.dtGrounds.vmDataTable.columns(5).search('').draw();
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
        date_today(days) {
           var today = new Date();
           var res = today.setTime(today.getTime() + (days * 24 * 60 * 60 * 1000));
        
           var today = new Date(res);
           var dd = today.getDate();
           var mm = today.getMonth() + 1; //January is 0!
           
           var yyyy = today.getFullYear();
           if (dd < 10) {
             dd = '0' + dd;
           } 
           if (mm < 10) {
             mm = '0' + mm;
           } 
           var today = yyyy + '/' + mm + '/'+ dd; 
           return today
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
        },
        addTableListeners: function(){
            let vm = this;
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
        }
    },
    created: function(){
        let vm = this;
        $.ajax({
            url: api_endpoints.profile,
            method: 'GET',
            dataType: 'json',
            success: function(data, stat, xhr){
                if(data.is_inventory){
                    vm.invent = true;
                }
                if(!vm.invent){
                    
                }
            }
        });
    },
    mounted: function() {
        var vm = this;
        vm.addTableListeners();
        vm.fetchRegions();
        vm.fetchParks();
        vm.fetchDistricts();

        $('#returns-collapse').on('shown.bs.collapse', function(){
            $('#collapse_returns_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_returns_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#returns-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_returns_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_returns_span').addClass("glyphicon glyphicon-menu-down");
        });
    }
};
</script>
