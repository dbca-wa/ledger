<template lang="html">
    <div class="panel-group" id="details-accordion" role="tablist" aria-multiselectable="true" style="padding:0;">
        <pkCsClose ref="closeCampsite" @closeCampsite="closeCampsite()"></pkCsClose>
        <pkCsOpen ref="openCampsite" @openCampsite="openCampsite()"></pkCsOpen>
        <div class="row">
            <div class="panel panel-default" id="details">
                <div class="panel-heading" role="tab" id="details-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#details-collapse"
                        aria-expanded="false" ref="top" aria-controls="details-collapse" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">Mooring Details</h3>
                                <span id="collapse_details_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id="details-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="details-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <campgroundAttr :createCampground=false :campground="campground" @updated="updateCampground" @save="sendData">
                                </campgroundAttr>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" style="margin-top:20px;">
            <div class="panel panel-default" id="contact">
                <div class="panel-heading" role="tab" id="contact-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#contact-collapse" id="collapse_contact"
                        aria-expanded="false" aria-controls="contact-collapse" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">Contact</h3>
                                <span id="collapse_contact_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id="contact-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="contact-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <campgroundContact :createCampground=false :campground="campground" @error="swalMessage" @updated="updateCampground" @save="sendData">
                                </campgroundContact>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" style="margin-top:20px;">
            <div class="panel panel-default" id="limits">
                <div class="panel-heading" role="tab" id="limits-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#limits-collapse" id="collapse_limits"
                        aria-expanded="false" aria-controls="limits-collapse" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">Vessel Limits</h3>
                                <span id="collapse_limits_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id="limits-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="limits-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <campgroundLimits :createCampground=false :campground="campground" @error="swalMessage" @updated="updateCampground" @save="sendData">
                                </campgroundLimits>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" style="margin-top:20px;">
            <div class="panel panel-default" id="images">
                <div class="panel-heading" role="tab" id="images-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#images-collapse" id="collapse_images"
                        aria-expanded="false" aria-controls="images-collapse" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">Mooring Images</h3>
                                <span id="collapse_images_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id="images-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="images-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <campgroundImages :createCampground=false :campground="campground" @updated="updateCampground" @save="sendData">
                                </campgroundImages>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" style="margin-top:20px;">
            <div class="panel panel-default" id="mappanel">
                <div class="panel-heading" role="tab" id="map-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#map-collapse" id="collapse_map"
                        aria-expanded="false" aria-controls="map-collapse" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">Mooring Location</h3>
                                <span id="collapse_map_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id="map-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="map-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <campgroundMap :createCampground=false :campground="campground" @error="swalMessage" @updated="updateCampground" @save="sendData">
                                </campgroundMap>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" style="margin-top:20px;">
            <div class="panel panel-default" id="additional">
                <div class="panel-heading" role="tab" id="additional-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#additional-collapse" id="collapse_additional"
                        aria-expanded="false" aria-controls="additional-collapse" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">Additional Details</h3>
                                <span id="collapse_additional_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id="additional-collapse" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="additional-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <campgroundAdditional :createCampground=false :campground="campground" @updated="updateCampground" @save="sendData">
                                </campgroundAdditional>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" style="margin-top:20px;">
            <div class="panel panel-default" id="stayhistory">
                <div class="panel-heading" role="tab" id="stayhistory-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#stayhistory-collapse" id="collapse_stayhistory"
                        aria-expanded="false" aria-controls="stayhistory-collapse" style="outline:none;">
                        <div>
                            <h3 style="display:inline;">Maximum Stay History</h3>
                            <span id="collapse_stay_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                        </div>
                        </a>
                    </h4>
                </div>
                <div id="stayhistory-collapse" class="panel-collapse collapse in" role="tabpanel"
                    aria-labelledby="stayhistory-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <stay-history :object_id="ID" :datatableURL="stayHistoryURL"></stay-history>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" style="margin-top:20px;">
            <div class="panel panel-default" id="bookingperiod">
                <div class="panel-heading" role="tab" id="bookingperiod-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#bookingperiod-collapse" id="collapse_pricehistory"
                        aria-expanded="false" aria-controls="bookingperiod-collapse" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">Booking Period History</h3>
                                <span id="collapse_booking_period_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id="bookingperiod-collapse" class="panel-collapse collapse in" role="tabpanel"
                    aria-labelledby="bookingperiod-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <priceHistory ref="price_dt" level="campground" :dt_options="ph_options" :historyDeleteURL="priceHistoryDeleteURL" :showAddBtn="hasCampsites" v-show="campground.price_level==0" :object_id="ID"></priceHistory>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row" style="margin-top:20px;margin-bottom:60px;">
            <div class="panel panel-default" id="closures">
                <div class="panel-heading" role="tab" id="closures-heading">
                    <h4 class="panel-title">
                        <a role="button" data-toggle="collapse" href="#closures-collapse" id="collapse_closurehistory"
                        aria-expanded="false" aria-controls="closures-collapse" style="outline:none;">
                            <div>
                                <h3 style="display:inline;">Closure History</h3>
                                <span id="collapse_closure_span" class="glyphicon glyphicon-menu-up" style="float:right;"></span>
                            </div>
                        </a>
                    </h4>
                </div>
                <div id="closures-collapse" class="panel-collapse collapse in" role="tabpanel"
                    aria-labelledby="closures-heading">
                    <div class="panel-body">
                        <div class="col-lg-12">
                            <div class="row">
                                <closureHistory ref="cg_closure_dt" :object_id="ID" :datatableURL="closureHistoryURL"></closureHistory>
                            </div>
                        </div>
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
    <div class="navbar navbar-default" id="footer" v-if="invent">
        <div class="container">
            <div class="navbar navbar-nav navbar-right" style="margin-top:5px;">
                <a href="#" class="btn btn-primary" @click.prevent="sendData">Update</a>
                <a href="/dashboard/moorings/" class="btn btn-default">Cancel</a>
            </div>
        </div>
    </div>
   </div>
</template>

<style>
#footer {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    height: 40px;
    width: 100%;
    margin: 0;
    z-index:50;
}
</style>

<script>
import {
    $,
    Moment,
    select2,
    api_endpoints,
    helpers
}
from '../../hooks.js'
import datatable from '../utils/datatable.vue'
import closureHistory from '../utils/closureHistory.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
import campgroundAttr from './campground-details.vue'
import campgroundContact from './campground-contact.vue'
import campgroundLimits from './campground-limits.vue'
import campgroundImages from './campground-images.vue'
import campgroundMap from './campground-map.vue'
import campgroundAdditional from './campground-additional.vue'
import confirmbox from '../utils/confirmbox.vue'
import bulkCloseCampsites from '../campsites/closureHistory/bulkClose.vue'
import pkCsClose from '../campsites/closureHistory/closeCampsite.vue'
import pkCsOpen from '../campsites/closureHistory/openCampsite.vue'
import stayHistory from '../utils/stayHistory/stayHistory.vue'
import swal from 'sweetalert2';
import {
    bus
}
from '../utils/eventBus.js'
import { mapGetters } from 'vuex'

$.extend($.fn.dataTableExt.oSort, {
    "extract-date-pre": function(value){
        if (value == '-'){
            return Infinity;
        }
        var date = value.split('/');
        return Date.parse(date[2] + '/' + date[1] + '/' + date[0])
        
    },
    "extract-date-asc": function(a, b){
        return ((a < b) ? -1 : ((a > b) ? 1 : 0));
    },
    "extract-date-desc": function(a, b){
        return ((a < b) ? 1 : ((a > b) ? -1 : 0));
    }
});

export default {
    name: 'campground',
    components: {
        datatable,
        campgroundAttr,
        campgroundContact,
        campgroundLimits,
        campgroundImages,
        campgroundMap,
        campgroundAdditional,
        confirmbox,
        pkCsClose,
        pkCsOpen,
        closureHistory,
        priceHistory,
        "stay-history":stayHistory,
        "bulk-close-campsites":bulkCloseCampsites,
    },
    computed: {
        ...mapGetters([
          'booking_periods'
        ]),
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
            invent: false,
            loadingDetails: false,
            loadingContact: false,
            loadingLimits: false,
            loadingImages: false,
            loadingMap: false,
            loadingAdditional: false,
            features_selected: [],
            campsites: [],
            editor: null,
            isOpenOpenCS: false,
            isOpenCloseCS: false,
            showBulkCloseCampsites: false,
            deleteRange: null,
            limits: null,
            class_val: null,
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
                    sType: 'extract-date',
                    mRender: function(data, type, full) {
                        return new Date(data).toLocaleDateString('en-GB');
                    }

                }, {
                    data: 'date_end',
                    sType: 'extract-date',
                    mRender: function(data, type, full) {
                        if(data){
                            return new Date(data).toLocaleDateString('en-GB');
                        } else {
                            return '-';
                        }   
                    }

                }, {
                    data: 'period_name',
                    mRender: function(data, type, full){
                        if(data){
                            return data;
                        } else {
                            return "";
                        }
                    }
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
                            var column = "<td ><a href='#' class='editPrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\" data-booking_period_id=\"__BOOKING__\" data-price_id=\"__PRICEID__\" >Edit</a><br/>"
                            if (full.deletable){
                                column += "<a href='#' class='deletePrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" data-reason=\"__REASON__\" data-details=\"__DETAILS__\" data-booking_period_id=\"__BOOKING__\" data-price_id=\"__PRICEID__\">Delete</a></td>";
                            }
                            column = column.replace(/__START__/g, full.date_start)
                            column = column.replace(/__END__/g, full.date_end)
                            column = column.replace(/__RATE__/g, full.rate_id)
                            column = column.replace(/__REASON__/g, full.reason)
                            column = column.replace(/__DETAILS__/g, full.details)
                            column = column.replace(/__BOOKING__/g, full.booking_period_id)
                            column = column.replace(/__PRICEID__/g, full.price_id)
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
                    data: 'editable',
                    mRender: function(data, type, full) {
                        var id = full.id;
                        if (full.active) {
                            var column ="<td ><a href='__ID__' class='detailRoute' data-campsite=\"__ID__\" >Edit</a><br/>";
                            if ( full.campground_open ){
                                column += "<a href='#' class='statusCS' data-status='close' data-campsite=\"__ID__\" >Close</a></td>";
                            }
                        }
                        else {
                            var column = "<td ><a href='__ID__' class='detailRoute' data-campsite=\"__ID__\" >Edit</a><br/>";
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
        updateCampground: function(value){
            var vm = this;
            vm.campground = value;
            console.log("Campground updated");
        },
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
                async: false,
                success: function(data, stat, xhr) {
                    vm.campground = data;
                    vm.fetchCampsites();
                    bus.$emit('campgroundFetched');
                    for (var i = 0; i < data.features.length; i++){
                        vm.features_selected.push(data.features[i].id);
                    }
                    vm.campground.features = vm.features_selected;
                    console.log("Features updated");
                }
            });
            vm.updateCampground(vm.campground);
            // vm.stopLoadingSection("all");
        },
        // loadSection: function(section){
        //     let vm = this;
        //     if (section == "details"){
        //         vm.loadingDetails = true;
        //     } else if (section == "contact"){
        //         vm.loadingContact = true;
        //     } else if (section == "limits"){
        //         vm.loadingLimits = true;
        //     } else if (section == "images"){
        //         vm.loadingImages = true;
        //     } else if (section == "map"){
        //         vm.loadingMap = true;
        //     } else if (section == "additional"){
        //         vm.loadingAdditional = true;
        //     } else if (section == "all"){
        //         vm.loadingDetails = true;
        //         vm.loadingContact = true;
        //         vm.loadingLimits = true;
        //         vm.loadingImages = true;
        //         vm.loadingMap = true;
        //         vm.loadingAdditional = true;
        //     }
        // },
        // stopLoadingSection: function(section){
        //     let vm = this;
        //     console.log(section);
        //     console.log("ending the loading");
        //     if (section == "details"){
        //         vm.loadingDetails = false;
        //     } else if (section == "contact"){
        //         vm.loadingContact = false;
        //     } else if (section == "limits"){
        //         console.log("Ending limit loading");
        //         vm.loadingLimits = false;
        //     } else if (section == "images"){
        //         vm.loadingImages = false;
        //     } else if (section == "map"){
        //         vm.loadingMap = false;
        //     } else if (section == "additional"){
        //         vm.loadingAdditional = false;
        //     } else if (section == "all"){
        //         vm.loadingDetails = false;
        //         vm.loadingContact = false;
        //         vm.loadingLimits = false;
        //         vm.loadingImages = false;
        //         vm.loadingMap = false;
        //         vm.loadingAdditional = false;
        //     }
        // },
        swalMessage: function(value){
            swal({
            title: value.title,
            text: value.text,
            type: value.type,
            showCancelButton: false,
            confirmButtonText: 'OK',
            showLoaderOnConfirm: true,
            allowOutsideClick: false
            });
        },
        addFormValidations: function() {
            $('form').each(function(){
                $(this).validate({
                    ignore:'div.ql-editor',
                    rules: {
                        name: "required",
                        park: "required",
                        campground_type: "required",
                        campground_type_physical: "required",
                        campground_class: "required",
                        contact: "required",
                        email: {
                            required: true,
                            email: true
                        },
                        telephone: "required",
                        vessel_size_limit: "required",
                        vessel_draft_limit: "required",
                        longitude: "required",
                        latitude: "required",
                        editor: "required",
                        oracle_code: "required",
                    },
                    messages: {
                        name: "Enter a mooring name",
                        park: "Select a park from the options",
                        campground_type: "Select a booking type from the options",
                        campground_type_physical: "Select a mooring type from the options",
                        campground_class: "Select a mooring class from the options",
                        contact: "Select a contact",
                        email: "Please select a contact",
                        telephone: "Please select a contact",
                        vessel_size_limit: "Please set a size limit greater than 0",
                        vessel_draft_limit: "Please set a draft limit greater than 0",
                        longitude: "Please set a longitude",
                        latitude: "Please set a latitude",
                        editor : "Please enter a valid description",
                        oracle_code: "Enter a valid oracle code",
                    },
                    showErrors: function(errorMap, errorList) {
                        $.each(this.validElements(), function(index, element) {
                            var $element = $(element);
                            $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                        });

                        // destroy tooltips on valid elements
                        $("." + this.settings.validClass).tooltip("destroy");

                        // add or update tooltips
                        for (var i = 0; i < errorList.length; i++) {
                            var error = errorList[i];
                            $('#' + error.element.id).focus();
                            $(error.element)
                                .tooltip({
                                    trigger: "focus"
                                })
                                .attr("data-original-title", error.message)
                                .parents('.form-group').addClass('has-error');
                        }
                    }
                });
            });
        },
        validateSize: function(){
            let vm = this;
            var isValid = true;
            console.log('VESSEL SIZE'); 
            console.log(vm.campground.vessel_size_limit)
            if(!parseFloat(vm.campground.vessel_size_limit) > 0){
                isValid = false;
                var error = {
                    title : "Invalid Size",
                    text : "Please select a size greater than 0",
                    type : "warning",
                }
                $('#vessel_size_limit').focus();
                vm.swalMessage(error);
            }
            if (isValid){
                if (vm.campground.mooring_class == "small"){
                    vm.class_val = 0;
                } else if (vm.campground.mooring_class == "medium"){
                    vm.class_val = 1;
                } else if (vm.campground.mooring_class == "large"){
                    vm.class_val = 2;
                }
                if (parseInt(vm.campground.vessel_size_limit) > vm.limits[vm.class_val].value){
                    isValid = false;
                    var error = {
                        title : "Invalid Size",
                        text : "Maximum size limited by Mooring Class. Please select a size limit of " + vm.limits[vm.class_val].value + " or less.",
                        type : "warning",
                    }
                    $('#vessel_size_limit').focus();
                    vm.swalMessage(error);
                }
            }
            
            return isValid;
        },
        validateDraft: function(){
            let vm = this;
            var isValid = true;
            if(!parseFloat(vm.campground.vessel_draft_limit) > 0){
                isValid = false;
                var error = {
                    title : "Invalid Draft",
                    text : "Please select a draft greater than 0",
                    type : "warning",
                }
                $('#vessel_draft_limit').focus();
                vm.swalMessage(error);
            }
            if (isValid){
                if (parseFloat(vm.campground.vessel_draft_limit) > vm.limits[vm.class_val + 3].value){
                    isValid = false;
                    var error = {
                        title : "Invalid Draft",
                        text : "Maximum draft limited by Mooring Class. Please select a draft limit of " + vm.limits[vm.class_val + 3].value + " or less.",
                        type : "warning",
                    }
                    $('#vessel_draft_limit').focus();
                    vm.swalMessage(error);
                }
            }
            return isValid;
        },
        validateBeamWeight: function(){
            let vm = this;
            var isValid = true;
            if(vm.campground.mooring_physical_type == 1 || vm.campground.mooring_physical_type == 2) {
                if(!parseFloat(vm.campground.vessel_beam_limit) > 0){
                    isValid = false;
                    var error = {
                        title : "Invalid Beam",
                        text : "Please select a beam greater than 0",
                        type : "warning",
                    }
                    $('#vessel_beam_limit').focus();
                    vm.swalMessage(error);
                }
                if (isValid){
                    if (parseFloat(vm.campground.vessel_beam_limit) > vm.limits[vm.class_val + 6].value){
                        isValid = false;
                        var error = {
                            title : "Invalid Beam",
                            text : "Maximum beam limited by Mooring Class. Please select a beam limit of " + vm.limits[vm.class_val + 6].value + " or less.",
                            type : "warning",
                        }
                        $('#vessel_beam_limit').focus();
                        vm.swalMessage(error);
                    }
                }
            } else {
                if(!parseFloat(vm.campground.vessel_weight_limit) > 0){
                    isValid = false;
                    var error = {
                        title : "Invalid Weight",
                        text : "Please select a weight greater than 0",
                        type : "warning",
                    }
                    $('#vessel_weight_limit').focus();
                    vm.swalMessage(error);
                }
                if (isValid){
                    if (parseFloat(vm.campground.vessel_weight_limit) > vm.limits[vm.class_val + 9].value){
                        isValid = false;
                        var error = {
                            title : "Invalid Weight",
                            text : "Maximum weight limited by Mooring Class. Please select a weight limit of " + vm.limits[vm.class_val + 9].value + " or less.",
                            type : "warning",
                        }
                        $('#vessel_weight_limit').focus();
                        vm.swalMessage(error);
                    }
                }
            }
            return isValid;
        },
        validateContact: function(){
            let vm = this;
            var isValid = true;
            if (vm.campground.contact == "undefined"){
                isValid = false;
                var error = {
                    title: "Invalid Contact",
                    text: "Please select a valid contact from the list",
                    type: "warning"
                }
                $('#contact').focus();
                vm.swalMessage(error);
            }
            return isValid;
        },
        validateMooringGroups: function(){
            let vm = this;
            var isValid = true;
            if (vm.campground.mooring_group.length == 0){
                isValid = false;
                var error = {
                    title: "No Group",
                    text: "Please select at least 1 mooring group (permissions)",
                    type: "warning"
                }
                $('#mooring_groups').focus();
                vm.swalMessage(error);
            }

            return isValid;
        },
        validateDescription: function(){
            let vm = this;
            var isValid = true;
            if (vm.campground.description){
                if (vm.campground.description.trim().length <= 11){
                    isValid = false;
                }
            } else {
                isValid = false;
            }
            if (!isValid){
                var error = {
                    title: "Invalid Description",
                    text: "Please enter some valid description text.\nMust be 5 characters or more.",
                    type: "warning",
                }
                $("#editor").focus();
                vm.swalMessage(error);
            }
            return isValid;
        },
        validateForm: function(){
            let vm = this;
            var isValid = true;
            if (!vm.limits){
                $.ajax({
                    url: api_endpoints.global_settings + "?mooring=" + vm.campground.id,
                    dataType: 'json',
                    method: 'GET',
                    async: false,
                    success: function(data, stat, xhr){
                        console.log(data)
                        vm.limits = data;
                    },
                });
            }
            isValid = vm.validateContact();
            if (isValid){
                isValid = vm.validateSize();
            }
            if (isValid){
                isValid = vm.validateDraft();
            }
            if (isValid){
                isValid = vm.validateBeamWeight();
            }
            if (isValid){
                isValid = vm.validateMooringGroups();
            }
            if (isValid){
                isValid = vm.validateDescription();
            }

            if (isValid){
                // console.log("Page has found to be valid up until form checks")
                $('form').each(function(){
                    if (!$(this).valid()){
                        isValid = false;
                        var message = {
                            title: "Failure",
                            text: "Mooring not updated, there was an error.\nPlease check all mandatory fields are complete.",
                            type: "error"
                        }
                        vm.swalMessage(message);
                        return false;
                    }
                }); 
            }
            
            return isValid;
        },
        sendData: function(){
            let vm = this;
            var isValid = vm.validateForm();
            // vm.loadSection(section);
            if (isValid){
                $.ajax({
                    beforeSend: function(xhrObj) {
                        xhrObj.setRequestHeader("Content-Type", "application/json");
                        xhrObj.setRequestHeader("Accept", "application/json");
                    },
                    url: api_endpoints.campground(this.campground.id),
                    method: "PUT",
                    xhrFields: {
                        withCredentials: true
                    },
                    data: JSON.stringify(vm.campground),
                    headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                    contentType: "application/x-www-form-urlencoded",
                    dataType: 'json',
                    success: function(data, stat, xhr) {
                        console.log("SUCCESS!!");
                        // if (method == 'POST') {
                        //     vm.$router.push({
                        //         name: 'cg_detail',
                        //         params: {
                        //             id: data.data.id
                        //         }
                        //     });
                        // }
                        // else if (method == 'PUT') {
                            // vm.showUpdate = true;
                        // }
                        // vm.stopLoadingSection(section);
                        vm.$store.dispatch("updateAlert",{
                            visible:false,
                            type:"danger",
                            message: ""
                        });
                        var message = {
                            title: "Success",
                            text: "Mooring updated",
                            type: "success"
                        }
                        vm.swalMessage(message);
                    },
                    error: function(resp) {
                        // vm.stopLoadingSection(section);
                        console.log("There was an error sending data.");
                        console.log(resp);
                        var message = {
                            title: "Failure: There was and error updating the mooring",
                            text: resp.responseText,
                            type: "error"
                        }
                        vm.swalMessage(message);
                        vm.$store.dispatch("updateAlert",{
                            visible:true,
                            type:"danger",
                            message: helpers.apiError(resp)
                        });
                    }
                });
            }
            // vm.addFormValidations();
        }

    },
    mounted: function() {
        var vm = this;
        // vm.loadSection("all");
        vm.$store.dispatch("fetchBookingPeriods");
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
        $.ajax({
            url: api_endpoints.profile,
            method: 'GET',
            dataType: 'json',
            success: function(data, stat, xhr){
                if(data.is_inventory){
                    vm.invent = true;
                }
                if(!vm.invent){
                    $('.form-control-input').prop('readonly', true);
                    $('.form-control-input').prop('disabled', true);
                }
            }
        });
        //Details
        $('#details-collapse').on('shown.bs.collapse', function(){
            $('#collapse_details_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_details_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#details-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_details_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_details_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Contact
        $('#contact-collapse').on('shown.bs.collapse', function(){
            $('#collapse_contact_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_contact_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#contact-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_contact_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_contact_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Limits
        $('#limits-collapse').on('shown.bs.collapse', function(){
            $('#collapse_limits_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_limits_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#limits-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_limits_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_limits_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Images
        $('#images-collapse').on('shown.bs.collapse', function(){
            $('#collapse_images_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_images_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#images-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_images_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_images_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Map
        $('#map-collapse').on('shown.bs.collapse', function(){
            $('#collapse_map_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_map_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#map-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_map_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_map_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Additional
        $('#additional-collapse').on('shown.bs.collapse', function(){
            $('#collapse_additional_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_additional_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#additional-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_additional_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_additional_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Max stay
        $('#stayhistory-collapse').on('shown.bs.collapse', function(){
            $('#collapse_stay_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_stay_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#stayhistory-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_stay_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_stay_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Booking Period
        $('#bookingperiod-collapse').on('shown.bs.collapse', function(){
            $('#collapse_booking_period_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_booking_period_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#bookingperiod-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_booking_period_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_booking_period_span').addClass("glyphicon glyphicon-menu-down");
        });
        //Closure
        $('#closures-collapse').on('shown.bs.collapse', function(){
            $('#collapse_closure_span').removeClass("glyphicon glyphicon-menu-down");
            $('#collapse_closure_span').addClass("glyphicon glyphicon-menu-up");

        });
        $('#closures-collapse').on('hidden.bs.collapse', function(){
            $('#collapse_closure_span').removeClass("glyphicon glyphicon-menu-up");
            $('#collapse_closure_span').addClass("glyphicon glyphicon-menu-down");
        });

        // $('#collapse_contact').click();
        // $('#collapse_limits').click();
        // $('#collapse_additional').click();
        // $('#collapse_stayhistory').click();
        // $('#collapse_pricehistory').click();
        // $('#collapse_closurehistory').click();

        setTimeout(function(){
            $(vm.$refs.top).focus();
            vm.addFormValidations();
        }, 50);
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
