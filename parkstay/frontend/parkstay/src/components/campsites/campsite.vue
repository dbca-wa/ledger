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
    											<label class="control-label" >Campsite Type</label>
    											<select class="form-control" v-show="!campsite_classes.length > 0" >
    												<option>Loading...</option>
    											</select>
    											<select v-if="campsite_classes.length > 1" @change="onCampsiteClassChange" name="campsite_class" class="form-control" v-model="campsite.campsite_class" >
                                                    <option value=""></option>
    												<option v-for="campsite_class in campsite_classes" :value="campsite_class.url" >{{campsite_class.name}}</option>
    											</select>
    										</div>
    									</div>
    									<div v-show="showName" class="col-md-6">
    										<div class="form-group">
    											<label class="control-label" >Campsite Name</label>
    											<input type="text" name="name" class="form-control"  v-model="campsite.name"required/>
    										</div>
    									</div>
    								</div>
                                    <div class="row">
                                        <div class="col-md-4">
                                            <div class="form-group">
                                                <label class="control-label" >Tents</label>
                                                <input type="number" name="name" class="form-control"  v-model="campsite.tents"required :disabled="selected_campsite_class_url() != ''"/>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="form-group">
                                                <label class="control-label" >Parking Spaces</label>
    											<select name="parking_spaces" class="form-control" v-model="campsite.parking_spaces" :disabled="selected_campsite_class_url() != ''" >
    												<option value="0" >Parking within site</option>
    												<option value="1" >Parking for exclusive use of site occupiers next to site, but separated from tent space</option>
    												<option value="2" >Parking for exclusive use of occupiers, short walk from tent space</option>
    												<option value="3" >Shared parking (not allocated), short walk from tent space</option>
    											</select>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="form-group">
                                                <label class="control-label" >Number of Vehicles</label>
    											<select name="parking_spaces" class="form-control" v-model="campsite.number_vehicles" :disabled="selected_campsite_class_url() != ''" >
    												<option value="0" >One vehicle</option>
    												<option value="1" >Two vehicles</option>
    												<option value="2" >One vehicle + small trailer</option>
    												<option value="3" >One vehicle + small trailer/large vehicle</option>
    											</select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-4">
                                            <div class="form-group">
                                                <label class="control-label" >Minimum Number of People</label>
                                                <input type="number" name="name" class="form-control"  v-model="campsite.min_people"required :disabled="selected_campsite_class_url() != ''"/>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="form-group">
                                                <label class="control-label" >Maximum Number of People</label>
                                                <input type="number" name="name" class="form-control"  v-model="campsite.max_people"required :disabled="selected_campsite_class_url() != ''"/>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="form-group">
                                                <label class="control-label" >Dimensions</label>
                                                <input type="text" name="name" class="form-control"  v-model="campsite.dimensions"required :disabled="selected_campsite_class_url() != ''"/>
                                            </div>
                                        </div>
                                    </div>
    								<div class="row">
    									<div class="col-sm-12">
                                        <select-panel v-show="!createCampsite" :options="features" :selected="selected_features" id="select-features" ref="select_features"></select-panel>
    									</div>
    								</div>
                                    <div class="row">
                                      <div class="col-sm-6">

                                      </div>
                                      <div class="col-sm-6">
                                          <div class="row">

                                              <div class="form-group">
                                                  <div class="col-sm-6 col-xs-8">
                                                      <button @click.prevent="addCampsite" type="button" v-show="createCampsite" class="btn btn-primary btn-create">Create</button>
                                                  </div>
                                                  <div class="col-sm-2 col-xs-4  pull-right">
                                                      <input type="number" v-show="createCampsite" class="form-control" name="number" v-model="campsite.number" value="">
                                                  </div>
                                              </div>
                                          </div>
                                          <div class="row" style="margin-top:10px;">
                                              <div class="col-sm-6 pull-right">
                                                  <div class="pull-right">
                                                      <button type="button" v-show="!createCampsite" style="margin-right:5px" @click="updateCampsite" class="btn btn-primary">Update</button>
                                                      <button type="button" class="btn btn-default pull-right" @click="goBack">Cancel</button>
                                                  </div>

                                              </div>
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
        },
        showName: function() {
            return (this.createCampsite && this.campsite.number == 1) || !this.createCampsite;
        },

    },
    data: function() {
        let vm = this;
        return {
            isLoading: false,
            features: [],
            selected_features: [],
            createCampsite: true,
            temp_campsite: {},
            campground: {},
            campsite: {
                number: 1,
            },
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
                        if (data && full.update_level == 2) {
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
        selected_campsite_class_url:function () {
            return (this.campsite.campsite_class != null) ? this.campsite.campsite_class :'';
        },
        onCampsiteClassChange:function () {
            let vm =this;
            if(vm.selected_campsite_class_url()){
                $.ajax({
                    url:vm.selected_campsite_class_url(),
                    dataType: 'json',
                    success:function (sel_class) {
                        vm.campsite.tents = sel_class.tents;
                        vm.campsite.number_vehicles = sel_class.number_vehicles;
                        vm.campsite.dimensions = sel_class.dimensions;
                        vm.campsite.max_people = sel_class.max_people;
                        vm.campsite.min_people= sel_class.min_people;
                        vm.campsite.parking_spaces= sel_class.parking_spaces;
                    }

                });
            }else{
                vm.campsite.tents = temp_campsite.tents;
                vm.campsite.number_vehicles = temp_campsite.number_vehicles;
                vm.campsite.dimensions = temp_campsite.dimensions;
                vm.campsite.max_people = temp_campsite.max_people;
                vm.campsite.min_people= temp_campsite.min_people;
                vm.campsite.parking_spaces= temp_campsite.parking_spaces;
            }

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
                    vm.temp_campsite = JSON.parse(JSON.stringify(data));
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
        fetchCampground: function() {
            let vm = this;
            $.get(api_endpoints.campground(vm.$route.params.id), function(data) {
                vm.campground = data;
                vm.campsite.campground = data.url;
            })
        },
        fetchCampsiteClasses: function() {
            let vm = this;
            $.get(api_endpoints.campsite_classes_active, function(data) {
                vm.campsite_classes = data;
            })
        },
        goBack: function() {
            helpers.goBack(this);
        },
        addCampsite: function() {
            this.sendData(api_endpoints.campsites,'POST')
        },
        updateCampsite: function() {
            this.sendData(api_endpoints.campsite(this.campsite.id),'PUT')
        },
        sendData: function(url,method) {
            let vm = this;
            vm.isLoading = true;
            var data = vm.campsite;
            if (vm.selected_campsite_class_url() == ''){
                data.cs_tents = data.tents;
                data.cs_parking_spaces = data.parking_spaces;
                data.cs_number_vehicles = data.number_vehicles;
                data.cs_min_people = data.min_people;
                data.cs_max_people = data.max_people;
                data.cs_dimensions = data.dimensions;
            }
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                xhrFields: {
                    withCredentials: true
                },
                url: url,
                method: method,
                data: JSON.stringify(data),
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
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
        vm.fetchCampground();
    }
}

</script>

<style lang="css">
    .table_btn {
        margin-top: 25px;
        margin-right: -14px;
    }
    @media(max-width: 768px) {
        .btn-create{
            position: absolute;
            left: 13px;
        }
    }
    @media(min-width: 768px) {
        .btn-create{
            position: absolute;
            left: 220px;
        }
    }
    @media(min-width: 992px) {
        .btn-create{
            position: absolute;
            left: 300px;
        }
    }
    @media(min-width: 1200px) {
        .btn-create{
            position: absolute;
            left: 390px;
        }
    }
</style>
