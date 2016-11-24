<template lang="html">
    <div id="campsite">
        <pkCsClose ref="closeCampsite" @closeCampsite="closeCampsite()"></pkCsClose>
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
                    <stayHistory v-if="!createCampsite" ref="stay_dt" :object_id="myID" :datatableURL="stayHistoryURL"></stayHistory>
                    <priceHistory v-if="!createCampsite" level="campsite" ref="price_dt" :object_id="myID" :dt_options="ph_options" :showAddBtn="canAddRate"></priceHistory>
                    <closureHistory v-if="!createCampsite" ref="cg_closure_dt" :closeCampground=false :object_id="myID" :datatableURL="closureHistoryURL"></closureHistory>
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
    Moment
}
from '../../hooks.js';
import datatable from '../utils/datatable.vue'
import stayHistory from './stayHistory/stayHistory.vue'
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
        "select-panel": select_panel,
        alert,
        pkCsClose,
        confirmbox,
        closureHistory,
        priceHistory,
        stayHistory,
        loader
    },
    computed: {
        closureHistoryURL: function() {
            return api_endpoints.campsites_status_history(this.$route.params.campsite_id);
        },
        stayHistoryURL: function() {
            return api_endpoints.campsites_stay_history;
        },
        myID: function() {
            return parseInt(this.$route.params.campsite_id);
        },
        canAddRate: function (){
            return this.campsite.can_add_rate ? this.campsite.can_add_rate : false;
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
            createCampiste: true,
            ph_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                order: [
                    [0,'desc']
                ],
                ajax: {
                    url: api_endpoints.campsites_price_history(this.$route.params.campsite_id),
                    dataSrc: ''
                },
                columns: [{
                    data: 'date_start',
                    mRender: function(data, type, full) {
                        return Moment(data).format('MMMM Do, YYYY');
                    }

                }, {
                    data: 'date_end',
                    mRender: function(data, type, full) {
                        if (data) {
                            return Moment(data).add(1, 'day').format('MMMM Do, YYYY');
                        }
                        else {
                            return '';
                        }
                    }

                }, {
                    data: 'adult'
                }, {
                    data: 'concession'
                }, {
                    data: 'child'
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
                            var column = "<td ><a href='#' class='editPrice' data-rate=\"__ID__\" >Edit</a><br/>"
                            if (full.deletable){
                                column += "<a href='#' class='deletePrice' data-rate=\"__ID__\">Delete</a></td>";
                            }
                            column = column.replace(/__ID__/g, full.id)
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
