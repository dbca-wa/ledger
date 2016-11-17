<template lang="html">
    <div id="campsite">
        <pkCsClose ref="closeCampsite" @closeCampsite="closeCampsite()"></pkCsClose>
        <addMaxStayCS :campsite.sync="campsite" ref="addMaxStayModal"></addMaxStayCS>
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
                   <div class="row">
                       <form>
                           <div class="panel panel-primary">
    							<div class="panel-heading">
    								<h3 class="panel-title">Campsite Details</h3>
    							</div>
    							<div class="panel-body">
    								<div class="row">
    									<div class="col-md-6">
    										<div class="form-group">
    											<label class="control-label" >Campsite Name</label>
    											<input type="text" name="name" class="form-control"  required/>
    										</div>
    									</div>
    									<div class="col-md-6">
    										<div class="form-group ">
    											<label class="control-label" >Class</label>
    											<select name="park" class="form-control" >
    												<option >Class...</option>
    											</select>
    										</div>
    									</div>
    								</div>
    								<div class="row">
    									<div class="col-sm-12">
                                        <select-panel :options="features" :selected="selected_features" id="select-features" refs="select-features"></select-panel>
    									</div>
    								</div>
    							</div>
    						</div>
                       </form>
                   </div>
                   <div class="row">
                      <div class="well">
                        <div class="col-sm-8">
                            <h1>Maximum Stay History</h1>
                        </div>
                        <div class="col-sm-4">
                         <button @click="showAddStay()" class="btn btn-primary pull-right table_btn">Add Max Stay Period</button>
                        </div>
                         <datatable ref="addMaxStayDT" :dtHeaders ="msh_headers" :dtOptions="msh_options" :table.sync="msh_table" id="stay_history"></datatable>
                      </div>
                   </div>
                   <div class="row">
                      <div class="well">
                        <div class="col-sm-8">
                            <h1>Price History</h1>
                        </div>
                        <div class="col-sm-4">
                         <button class="btn btn-primary pull-right table_btn">Add Price Period</button>
                        </div>
                         <datatable :dtHeaders ="ph_headers" :dtOptions="ph_options" :table.sync="ph_table" id="price_history"></datatable>
                      </div>
                   </div>
                   <div class="row">
                      <div class="well">
                        <div class="col-sm-8">
                            <h1>Closure History</h1>
                        </div>
                        <div class="col-sm-4">
                         <button @click="showCloseCS()" class="btn btn-primary pull-right table_btn">Add Closure Period</button>
                        </div>
                         <datatable ref="closureHistDT" :dtHeaders ="ch_headers" :dtOptions="ch_options" :table.sync="ch_table" id="closure_history"></datatable>
                      </div>
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
    api_endpoints,
    helpers
} from '../../hooks.js';
import datatable from '../utils/datatable.vue'
import addMaxStayCS from './stayHistory/addMaximumStayPeriod.vue'
import select_panel from '../utils/select-panel.vue'
import alert from '../utils/alert.vue'
import pkCsClose from './closureHistory/closeCampsite.vue'
export default {
    name:'campsite',
    components:{
        datatable,
        addMaxStayCS,
        "select-panel":select_panel,
        alert,
        pkCsClose
    },
    data:function (){
        let vm = this;
        return{
            features:[],
            selected_features:[],
            createCampsite:true,
            campsite:{},
            msh_headers:['ID','Period Start', 'Period End','Maximum Stay(Nights)', 'Comment', 'Action'],
            ph_headers:['ID','Period Start','Period End','Adult Price','Concession Price','Child Price','Comment','Action'],
            ch_headers:['ID','Closure Start','Reopen','Closure Reason','Details','Action'],
            msh_table:{},
            ph_table:{},
            ch_table:{},
            default_dtOptions:{
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
            msh_options:{
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                ajax:{
                    //TODO
                    /*
                    * change end point to closure history
                    */
                    url:api_endpoints.campsiteStayHistory(vm.$route.params.campsite_id),
                    dataSrc:''
                },
                columns:[
                    {
                        "data": "id"
                    },
                    {
                        "data":"range_start"
                    },
                    {
                        "data":"range_end"
                    },
                    {
                        "data":"max_days"
                    },
                    {
                        "data":"details"
                    },
                    {
                        "mRender": function(data, type, full) {
                            var id = full.id;
                            if (full.editable){
                                var column = "<td ><a href='#' class='editStay' data-stay_period=\"__ID__\" >Edit</a>";
                                return column.replace('__ID__', id);
                            }
                            return '';
                        }
                    }
                ]
            },
            ph_options:{
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                ajax:{
                    //TODO
                    /*
                    * change end point to closure history
                    */
                    url:api_endpoints.campsiteStayHistory(vm.$route.params.campsite_id),
                    dataSrc:''
                },
                columns:[
                    {
                        "data": "id"
                    },
                    {
                        "data":"closure_start"
                    },
                    {
                        "data":"closure_end"
                    },
                    {
                        "data":"closure_reason"
                    },
                    {
                        "data":"reopen_reason"
                    },
                    {
                        "mRender": function(data, type, full) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit Campground Details</a>";
                            return column.replace('__ID__', id);
                        }
                    }
                ]
            },
            ch_options:{
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                ajax:{
                    //TODO
                    /*
                    * change end point to closure history
                    */
                    url:api_endpoints.campsites_status_history(vm.$route.params.campsite_id),
                    dataSrc:''
                },
                columns:[
                    {
                        "data": "id"
                    },
                    {
                        "data":"range_start"
                    },
                    {
                        "data":"range_end"
                    },
                    {
                        "data":"status"
                    },
                    {
                        "data":"details"
                    },
                    {
                        "mRender": function(data, type, full) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='detailRoute' data-campground=\"__ID__\" >Edit Campground Details</a>";
                            return column.replace('__ID__', id);
                        }
                    }
                ]
            }

        }
    },
    methods: {
        showAddStay: function(){
            this.$refs.addMaxStayModal.isOpen = true;
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
                xhrFields: { withCredentials:true },
                data: data,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.closeCampsite.close();
                    vm.$refs.closureHistDT.vmDataTable.ajax.reload();
                },
                error:function (resp){
                    vm.$refs.closeCampsite.errors = true;
                    vm.$refs.closeCampsite.errorString = helpers.apiError(resp);
                }
            });
        },
        fetchCampsite: function() {
            let vm = this;
             $.ajax({
                url: api_endpoints.campsite(vm.$route.params.campsite_id),
                method: 'GET',
                xhrFields: { withCredentials:true },
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.campsite = data;
                },
                error:function (resp){
                    vm.errors = true;
                    if (resp.status == 404){
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
        attachEventListenersMaxStayDT: function() {
            let vm = this;
            vm.$refs.addMaxStayDT.vmDataTable.on('click','.editStay', function(e){
                e.preventDefault();
            });
        }
    },
    mounted: function() {
        let vm = this;
        if (vm.$route.params.campsite_id){
            vm.createCampiste = false;
            vm.fetchCampsite();
        }
        vm.loadFeatures();

    }
}
</script>

<style lang="css">
    .table_btn {
        margin-top: 25px;
        margin-right: -14px;
    }
</style>
