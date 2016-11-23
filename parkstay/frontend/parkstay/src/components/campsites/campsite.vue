<template lang="html">
    <div id="campsite">
        <pkCsClose ref="closeCampsite" @closeCampsite="closeCampsite()"></pkCsClose>
        <addMaxStayCS :stay.sync="stay" :campsite.sync="campsite" ref="addMaxStayModal"></addMaxStayCS>
       <div class="panel panel-default" id="applications">
         <div class="panel-heading" role="tab" id="applications-heading">
             <h4 class="panel-title">
                 <a role="button" data-toggle="collapse" href="#applications-collapse"
                    aria-expanded="false" aria-controls="applications-collapse">
                     <h3>Campsite</h3>
                 </a>
             </h4>
         </div>
         <div id="applications-collapse" class="panel-collapse collapse in" role="tabpanel"
              aria-labelledby="applications-heading">
             <div class="panel-body">
                <div class="col-lg-12">
                   <div class="row" >
                       <form >
                           <div class="panel panel-primary">
    							<div class="panel-heading">
    								<h3 class="panel-title">Campsite Details</h3>
    							</div>
    							<div class="panel-body" v-show="!isLoading">
    								<div class="row">
    									<div class="col-md-6">
    										<div class="form-group">
    											<label class="control-label" >Campsite Name</label>
    											<input type="text" name="name" class="form-control"  v-model="campsite.name"required/>
    										</div>
    									</div>
    									<div class="col-md-6">
    										<div class="form-group ">
    											<label class="control-label" >Class</label>
    											<select name="park" class="form-control" v-model="campsite.campsite_class" >
    												<option v-for="campsite_class in campsite_classes" :value="campsite_class.url" >{{campsite_class.name}}</option>
    											</select>
    										</div>
    									</div>
    								</div>
    								<div class="row">
    									<div class="col-sm-12">
                                        <select-panel :options="features" :selected="selected_features" id="select-features" ref="select_features"></select-panel>
    									</div>
    								</div>
                                    <div class="row">
                                      <div class="col-sm-6">

                                      </div>
                                      <div class="col-sm-6">
                                          <div class="pull-right">
                                              <button type="button" v-show="!createCampsite" @click="updateCampsite" class="btn btn-primary">Update</button>
                                              <button type="button" v-show="createCampsite" class="btn btn-primary">Create</button>
                                              <button type="button" class="btn btn-default" @click="goBack">Cancel</button>
                                          </div>
                                      </div>
                                    </div>
    							</div>
    						</div>
                       </form>
                       <loader :isLoading="isLoading">Saving Campsite Data...</loader>
                   </div>

                   <div v-if="!createCampsite" class="row">
                      <div class="well">
                        <alert ref="retrieveStayAlert" :show.sync="retrieve_stay.error" type="danger" :duration="retrieve_stay.timeout">{{retrieve_stay.errorString}}</alert>
                        <div class="col-sm-8">
                            <h1>Maximum Stay History</h1>
                        </div>
                        <div class="col-sm-4">
                         <button @click="showAddStay()" class="btn btn-primary pull-right table_btn">Add Max Stay Period</button>
                        </div>
                         <datatable ref="addMaxStayDT" :dtHeaders ="msh_headers" :dtOptions="msh_options" :table.sync="msh_table" id="stay_history"></datatable>
                      </div>
                   </div>
                    <priceHistory v-if="!createCampsite" ref="price_dt" :object_id="myID" :datatableURL="priceHistoryURL"></priceHistory>
                    <closureHistory v-if="!createCampsite" ref="cg_closure_dt" :closeCampground=false :object_id="myID" :datatableURL="closureHistoryURL"></closureHistory>
                </div>
             </div>
          </div>
       </div>
    <confirmbox id="deleteStay" :options="deleteStayPrompt"></confirmbox>
   </div>
</template>

<script>
import {
    $,
    api_endpoints,
    helpers
}
from '../../hooks.js';
import datatable from '../utils/datatable.vue'
import addMaxStayCS from './stayHistory/addMaximumStayPeriod.vue'
import select_panel from '../utils/select-panel.vue'
import alert from '../utils/alert.vue'
import pkCsClose from './closureHistory/closeCampsite.vue'
import confirmbox from '../utils/confirmbox.vue'
import loader from '../utils/loader.vue'
import {
    bus
}
from '../utils/eventBus.js'
import closureHistory from '../utils/closureHistory.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
export default {
    name: 'campsite',
    components: {
        datatable,
        addMaxStayCS,
        "select-panel": select_panel,
        alert,
        pkCsClose,
        confirmbox,
        closureHistory,
        priceHistory,
        loader
    },
    computed: {
        closureHistoryURL: function() {
            return api_endpoints.campsites_status_history(this.$route.params.campsite_id);
        },
        priceHistoryURL: function() {
            return api_endpoints.campsites_price_history(this.$route.params.campsite_id);
        },
        myID: function() {
            return parseInt(this.$route.params.campsite_id);
        }
    },
    data: function() {
        let vm = this;
        return {
            isLoading: false,
            features: [],
            selected_features: [],
            createCampsite: true,
            campsite: {},
            campsite_classes: [],
            stay: {},
            createCampiste: true,
            deleteStay: null,
            deleteStayPrompt: {
                icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
                message: "Are you sure you want to Delete this stay Period",
                buttons: [{
                    text: "Delete",
                    event: "delete",
                    bsColor: "btn-danger",
                    handler: function() {
                        vm.deleteStayRecord(vm.deleteStay);
                        vm.deleteStay = null;
                    },
                    autoclose: true,
                }],
                id: 'deleteStay'
            },
            retrieve_stay: {
                error: false,
                timeout: 5000,
                errorString: ''
            },
            msh_headers: ['ID', 'Period Start', 'Period End', 'Maximum Stay(Nights)', 'Comment', 'Action'],
            ph_headers: ['ID', 'Period Start', 'Period End', 'Adult Price', 'Concession Price', 'Child Price', 'Comment', 'Action'],
            ch_headers: ['ID', 'Closure Start', 'Reopen', 'Closure Reason', 'Details', 'Action'],
            msh_table: {},
            ph_table: {},
            ch_table: {},
            default_dtOptions: {
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            //TODO
            /**
             *replace all with actual values
             */
            msh_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                order: [
                    [0,'desc']
                ],
                ajax: {
                    url: api_endpoints.campsiteStayHistory(vm.$route.params.campsite_id),
                    dataSrc: ''
                },
                columns: [{
                    "data": "id"
                }, {
                    "data": "range_start"
                }, {
                    "data": "range_end"
                }, {
                    "data": "max_days"
                }, {
                    "data": "details"
                }, {
                    "mRender": function(data, type, full) {
                        var id = full.id;
                        if (full.editable) {
                            var column = "<td ><a href='#' class='editStay' data-stay_period=\"__ID__\" >Edit</a>";
                            column += "<br/><a href='#' class='deleteStay' data-stay_period=\"__ID__\" >Delete</a></td>";
                            return column.replace(/__ID__/g, id);
                        }
                        return '';
                    }
                }]
            },
            ph_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                ajax: {
                    //TODO
                    /*
                     * change end point to closure history
                     */
                    url: api_endpoints.campsiteStayHistory(vm.$route.params.campsite_id),
                    dataSrc: ''
                },
                columns: [{
                    "data": "id"
                }, {
                    "data": "closure_start"
                }, {
                    "data": "closure_end"
                }, {
                    "data": "closure_reason"
                }, {
                    "data": "reopen_reason"
                }, {
                    "mRender": function(data, type, full) {
                        var id = full.id;
                        var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit Campground Details</a>";
                        return column.replace('__ID__', id);
                    }
                }]
            },
            ch_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                ajax: {
                    //TODO
                    /*
                     * change end point to closure history
                     */
                    url: api_endpoints.campsites_status_history(vm.$route.params.campsite_id),
                    dataSrc: ''
                },
                columns: [{
                    "data": "id"
                }, {
                    "data": "range_start"
                }, {
                    "data": "range_end"
                }, {
                    "data": "status"
                }, {
                    "data": "details"
                }, {
                    "mRender": function(data, type, full) {
                        var id = full.id;
                        var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit</a>";
                        return column.replace('__ID__', id);
                    }
                }]
            }

        }
    },
    watch: {
        selected_features: {
            handler: function() {
                let vm = this;
                this.campsite.features = [];
                $.each(vm.selected_features, function(i, feature) {
                    vm.campsite.features.push(feature.url);
                });
            },
            deep: true
        }
    },
    methods: {
        showAddStay: function(create) {
            create = typeof create !== 'undefined' ? create : true;
            this.$refs.addMaxStayModal.isOpen = true;
            this.$refs.addMaxStayModal.create = create;
        },
        showCloseCS: function() {
            var id = this.campsite.id;
            // Update close modal attributes
            this.$refs.closeCampsite.id = id;
            this.$refs.closeCampsite.isOpen = true;
        },
        loadFeatures: function() {
            var vm = this;
            var url = api_endpoints.features;
            $.ajax({
                url: url,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.features = data;
                }
            });
        },
        closeCampsite: function() {
            let vm = this;
            var data = vm.$refs.closeCampsite.formdata;
            data.status = vm.$refs.closeCampsite.formdata.reason;
            $.ajax({
                url: api_endpoints.opencloseCS(vm.$refs.closeCampsite.id),
                method: 'POST',
                xhrFields: {
                    withCredentials: true
                },
                data: data,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.closeCampsite.close();
                    vm.$refs.closureHistDT.vmDataTable.ajax.reload();
                },
                error: function(resp) {
                    vm.$refs.closeCampsite.errors = true;
                    vm.$refs.closeCampsite.errorString = helpers.apiError(resp);
                }
            });
        },
        fetchStay: function(id) {
            let vm = this;
            $.ajax({
                url: api_endpoints.campsites_stay_history_detail(id),
                method: 'GET',
                xhrFields: {
                    withCredentials: true
                },
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.stay = data;
                    vm.showAddStay(false);
                },
                error: function(resp) {
                    vm.retrieve_stay.error = true;
                    vm.retrieve_stay.errorString = 'There was a problem trying to retrive this stay period';
                    setTimeout(function() {
                        vm.retrieve_stay.error = false;
                    }, vm.retrieve_stay.timeout);
                }
            });
        },
        fetchCampsite: function() {
            let vm = this;
            $.ajax({
                url: api_endpoints.campsite(vm.$route.params.campsite_id),
                method: 'GET',
                xhrFields: {
                    withCredentials: true
                },
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.campsite = data;

                    vm.$refs.select_features.loadSelectedFeatures(data.features);
                    //vm.selected_features = ;
                },
                error: function(resp) {
                    if (resp.status == 404) {
                        vm.$router.push({
                            name: '404'
                        });
                    }
                }
            });
        },
        refreshMaxStayTable: function() {
            this.$refs.addMaxStayDT.vmDataTable.ajax.reload();
        },
        deleteStayRecord: function(id) {
            var vm = this;
            var url = api_endpoints.campsites_stay_history_detail(id);
            $.ajax({
                method: "DELETE",
                url: url,
            }).done(function(msg) {
                vm.refreshMaxStayTable();
            });
        },
        attachEventListenersMaxStayDT: function() {
            let vm = this;
            vm.$refs.addMaxStayDT.vmDataTable.on('click', '.editStay', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-stay_period');
                vm.fetchStay(id);
            });
            vm.$refs.addMaxStayDT.vmDataTable.on('click', '.deleteStay', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-stay_period');
                vm.deleteStay = id;
                bus.$emit('showAlert', 'deleteStay');
            });
        },
        fetchCampsiteClasses: function() {
            let vm = this;
            $.get(api_endpoints.campsite_classes, function(data) {
                vm.campsite_classes = data;
            })
        },
        goBack: function() {
            this.$route.go(window.history.back());
        },
        updateCampsite: function() {
            let vm = this;
            vm.isLoading = true;
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                xhrFields: {
                    withCredentials: true
                },
                url: api_endpoints.campsite(vm.$route.params.campsite_id),
                method: 'PUT',
                data: JSON.stringify(vm.campsite),
                success: function(data) {

                    vm.campsite = data;
                    setTimeout(function () {
                        vm.isLoading = false;
                    },500);

                }
            })
        }
    },
    mounted: function() {
        let vm = this;
        if (vm.$route.params.campsite_id) {
            vm.createCampsite = false;
            vm.fetchCampsite();
        }
        vm.loadFeatures();
        if ( !vm.createCampsite ){ vm.attachEventListenersMaxStayDT(); }
        vm.fetchCampsiteClasses();
    }
}

</script>

<style lang="css">
    .table_btn {
        margin-top: 25px;
        margin-right: -14px;
    }
</style>
