<template lang="html">
   <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
        <pkCsClose ref="closeCampsite" @closeCampsite="closeCampsite()"></pkCsClose>
        <pkCsOpen ref="openCampsite" @openCampsite="openCampsite()"></pkCsOpen>
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
                <stay-history :object_id="ID" :datatableURL="stayHistoryURL"style="margin-top:100px;"></stay-history>
                <priceHistory ref="price_dt" level="campground" :dt_options="ph_options" :historyDeleteURL="priceHistoryDeleteURL" :showAddBtn="hasCampsites" v-show="campground.price_level==0" :object_id="ID"></priceHistory>
                <closureHistory ref="cg_closure_dt" :object_id="ID" :datatableURL="closureHistoryURL"></closureHistory>
               </div>
            </div>
         </div>
      </div>
      <div class="panel panel-default" id="applications" style="margin-top:50px; display:none;">
        <div class="panel-heading" role="tab" id="applications-heading">
            <h4 class="panel-title">
                <a role="button" data-toggle="collapse" href="#campsites"
                   aria-expanded="false" aria-controls="collapseOne">
                    <h3>Mooring Sites</h3>
                </a>
            </h4>
        </div>
        <div class="panel-collapse collapse in" role="tabpanel"
             aria-labelledby="applications-heading" id="campsites">
            <div class="panel-body">
               <div class="col-lg-12">
                  <div class="row">
                     <div class="well">
                        <div class="col-sm-offset-8 col-sm-4">
                            <button @click="showBulkCloseCampsites = true" class="btn btn-primary pull-right table_btn" >Close Mooring Sites</button> 
                            <router-link :to="{name:'add_campsite',params:{id:campground_id}}" class="btn btn-primary pull-right table_btn" style="margin-right: 1em;">Add Mooring site</router-link>
                        </div>
                        <datatable ref="cg_campsites_dt" :dtHeaders ="cs_headers" :dtOptions="cs_options" id="cs_table"></datatable>
                     </div>
                  </div>
               </div>
            </div>
        </div>
    </div>
    <confirmbox id="deleteRange" :options="deletePrompt"></confirmbox>
    <bulk-close-campsites v-on:bulkCloseCampsites="bulkCloseCampsites" v-if="showBulkCloseCampsites" v-on:close="showBulkCloseCampsites = false" ref="bulkCloseCampsites" v-bind:campsites="campsites"/>
   </div>

</template>

<script>
import datatable from '../utils/datatable.vue'
import closureHistory from '../utils/closureHistory.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
import campgroundAttr from './campground-attr.vue'
import confirmbox from '../utils/confirmbox.vue'
import bulkCloseCampsites from '../campsites/closureHistory/bulkClose.vue'
import pkCsClose from '../campsites/closureHistory/closeCampsite.vue'
import pkCsOpen from '../campsites/closureHistory/openCampsite.vue'
import stayHistory from '../utils/stayHistory/stayHistory.vue'
import {
    bus
}
from '../utils/eventBus.js'
import {
    $,
    Moment,
    api_endpoints,
    helpers
}
from '../../hooks.js'

export default {
    name: 'campground',
    components: {
        datatable,
        campgroundAttr,
        confirmbox,
        pkCsClose,
        pkCsOpen,
        closureHistory,
        priceHistory,
        "stay-history":stayHistory,
        "bulk-close-campsites":bulkCloseCampsites
    },
    computed: {
        closureHistoryURL: function() {
            return api_endpoints.status_history(this.$route.params.id);
        },
        priceHistoryURL: function() {
            return api_endpoints.campground_price_history(this.$route.params.id);
        },
        ID: function(){
            return parseInt(this.$route.params.id);
        },
        hasCampsites: function() {
            return this.campsites.length > 0;
        },
        campground_id: function (){
            return this.campground.id ? this.campground.id : 0;
        },
        priceHistoryDeleteURL: function (){
            return api_endpoints.delete_campground_price(this.ID);
        }
    },
    data: function() {
        let vm = this;
        return {
            stayHistoryURL:api_endpoints.campgroundStayHistory(this.$route.params.id),
            campground: {
                address:{},
                images: []
            },
            campsites: [],
            isOpenOpenCS: false,
            isOpenCloseCS: false,
            showBulkCloseCampsites: false,
            deleteRange: null,
            ph_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                order: [],
                ajax: {
                    url: api_endpoints.campground_price_history(this.$route.params.id),
                    dataSrc: ''
                },
                columns: [{
                    data: 'date_start',
                    mRender: function(data, type, full) {
                        return Moment(data).format('DD/MM/YYYY');
                    }

                }, {
                    data: 'date_end',
                    mRender: function(data, type, full) {
                        if (data) {
                            return Moment(data).add(1, 'day').format('DD/MM/YYYY');
                        }
                        else {
                            return '';
                        }
                    }

                }, {
                    data: 'mooring'
//                }, {
//                    data: 'concession'
//                }, {
//                    data: 'child'
                }, {
                    data: 'details',
                    mRender: function(data, type, full) {
                        if (data){
                            return data;
                        }
                        return '';
                    }
                }, {
                    data: 'editable',
                    mRender: function(data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editPrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\">Edit</a><br/>"
                            if (full.deletable){
                                column += "<a href='#' class='deletePrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\">Delete</a></td>";
                            }
                            column = column.replace(/__START__/g, full.date_start)
                            column = column.replace(/__END__/g, full.date_end)
                            column = column.replace(/__RATE__/g, full.rate_id)
                            column = column.replace(/__REASON__/g, full.reason)
                            column = column.replace(/__DETAILS__/g, full.details)
                            return column
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
            title: 'Mooring',
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
                    targets: 3
                }, {
                    responsivePriority: 3,
                    targets: 1
                }, {
                    responsivePriority: 4,
                    targets: 2
                }],
                columns: [{
                    data:'name'
                },{
                    data: 'type',
                    mRender:function (data,type,full) {
                        if (data){
                            var max_length = 25;
                            var name = (data.length > max_length) ? data.substring(0,max_length-1)+'...' : data;
                            var column = '<td> <div class="name_popover" tabindex="0" data-toggle="popover" data-placement="top" data-content="__NAME__" >'+ name +'</div></td>';
                            return column.replace('__NAME__', data);
                        }
                        return '';
                    }
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
                        if (full.active) {
                            var column ="<td ><a href='#' class='detailRoute' data-campsite=\"__ID__\" >Edit</a><br/>";
                            if ( full.campground_open ){
                                column += "<a href='#' class='statusCS' data-status='close' data-campsite=\"__ID__\" >Close</a></td>";
                            }
                        }
                        else {
                            var column = "<td ><a href='#' class='detailRoute' data-campsite=\"__ID__\" >Edit</a><br/>";
                            if ( full.campground_open ){
                                column += "<a href='#' class='statusCS' data-status='open' data-campsite=\"__ID__\" data-current_closure='"+ full.current_closure +"'>Open</a></td>";
                            }
                        }

                        return column.replace(/__ID__/g, id);
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            cs_headers: [ 'Name','Type', 'Status', 'Price', 'Action'],
            deletePrompt: {
                icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
                message: "Are you sure you want to Delete ?",
                buttons: [{
                    text: "Delete",
                    event: "deleteRange",
                    bsColor: "btn-danger",
                    handler: function() {
                        vm.deleteBookingRange(vm.deleteRange);
                        vm.deleteRange = null;
                    },
                    autoclose: true
                }],
                id: 'deleteRange'
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
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}
            }).done(function(msg) {
                vm.$refs.cg_closure_dt.vmDataTable.ajax.reload();
            });
        },
        showCloseCS: function() {
            this.$refs.closeCampsite.isOpen = true;
        },
        openCampsite: function() {
            let vm = this;
            var data = vm.$refs.openCampsite.formdata;
            $.ajax({
                url: api_endpoints.opencloseCS(vm.$refs.openCampsite.id),
                method: 'POST',
                xhrFields: { withCredentials:true },
                data: data,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.openCampsite.close();
                    vm.refreshCampsiteClosures();
                },
                error:function (data){
                    vm.$refs.openCampsite.errors = true;
                    vm.$refs.openCampsite.errorString = helpers.apiError(data);
                }
            });

        },
        closeCampsite: function() {
            let vm = this;
            var data = vm.$refs.closeCampsite.formdata;
            $.ajax({
                url: api_endpoints.opencloseCS(vm.$refs.closeCampsite.id),
                method: 'POST',
                xhrFields: { withCredentials:true },
                data: data,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.closeCampsite.close();
                    vm.refreshCampsiteClosures();
                },
                error:function (resp){
                    vm.$refs.closeCampsite.errors = true;
                    vm.$refs.closeCampsite.errorString = helpers.apiError(resp);
                }
            });
        },
        bulkCloseCampsites: function() {
            let vm = this;
            var data = vm.$refs.bulkCloseCampsites.formdata;
            console.log(vm.$refs.bulkCloseCampsites);
            console.log(data);
            $.ajax({
                url: api_endpoints.bulk_close_campsites(),
                method: 'POST',
                xhrFields: { withCredentials:true },
                data: data,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.bulkCloseCampsites.close();
                    vm.refreshCampsiteClosures();
                },
                error:function (resp){
                    vm.$refs.bulkCloseCampsites.errors = true;
                    vm.$refs.bulkCloseCampsites.errorString = helpers.apiError(resp);
                }
            });
        },
        refreshCampsiteClosures: function(dt) {
            this.$refs.cg_campsites_dt.vmDataTable.ajax.reload();
        },
        showOpenOpenCS: function() {
            this.$refs.openCampsite.isOpen = true;
        },
        fetchCampsites: function(){
            let vm = this;
            $.get(api_endpoints.campgroundCampsites(this.$route.params.id), function(data){
                vm.campsites = data;
            });
        },
        fetchCampground:function () {
            let vm =this;
            $.ajax({
                url: api_endpoints.campground(vm.$route.params.id),
                dataType: 'json', 
                async: true,
                success: function(data, stat, xhr) {
                    vm.campground = data;
                    vm.fetchCampsites();
                    bus.$emit('campgroundFetched');
                }
            });
        }

    },
    mounted: function() {
        var vm = this;
        vm.$refs.cg_campsites_dt.vmDataTable.on('click', '.detailRoute', function(e) {
            e.preventDefault();
            var id = $(this).attr('data-campsite');
            vm.$router.push({
                name: 'view_campsite',
                params: {
                    id: vm.campground.id,
                    campsite_id: id
                }
            });
        });
        vm.$refs.cg_campsites_dt.vmDataTable.on('click', '.statusCS', function(e) {
            e.preventDefault();
            var id = $(this).attr('data-campsite');
            var status = $(this).attr('data-status');
            var current_closure = $(this).attr('data-current_closure') ? $(this).attr('data-current_closure') : '';

            if (status === 'open'){
                vm.showOpenOpenCS();
                // Update open modal attributes
                vm.$refs.openCampsite.status = 0;
                vm.$refs.openCampsite.id = id;
                vm.$refs.openCampsite.current_closure = current_closure;
            }else if (status === 'close'){
                vm.showCloseCS();
                // Update close modal attributes
                vm.$refs.closeCampsite.status = 1;
                vm.$refs.closeCampsite.id = id;
                vm.$refs.closeCampsite.current_closure = current_closure;
            }
        });
        helpers.namePopover($,vm.$refs.cg_campsites_dt.vmDataTable);
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
