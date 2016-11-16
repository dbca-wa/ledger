<template lang="html">
    <div id="campsite">
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
                       <div class="well">
                           <!--campsiteAttr :createCampsite="createCampsite" :campsite.sync="campsite"></campsiteAttr-->
                       </div>
                   </div>
                   <div class="row">
                      <div class="well">
                         <h1>Maximum Stay History</h1>
                         <datatable :dtHeaders ="msh_headers" :dtOptions="msh_options" :table.sync="msh_table" id="stay_history"></datatable>
                      </div>
                   </div>
                   <div class="row">
                      <div class="well">
                         <h1>Price History</h1>
                         <datatable :dtHeaders ="ph_headers" :dtOptions="ph_options" :table.sync="ph_table" id="price_history"></datatable>
                      </div>
                   </div>
                   <div class="row">
                      <div class="well">
                         <h1>Closure History</h1>
                         <datatable :dtHeaders ="ch_headers" :dtOptions="ch_options" :table.sync="ch_table" id="closure_history"></datatable>
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
    api_endpoints
} from '../../hooks.js';
import datatable from '../utils/datatable.vue'
export default {
    name:'campsite',
    components:{
        datatable
    },
    data:function (){
        let vm = this;
        return{
            createCampsite:true,
            campsite:{},
            msh_headers:['ID','Period Start', 'Period End','Maximum Stay(Nights)', 'Comment', 'Action'],
            ph_headers:['ID','Period Start','Period End','Adult Price','Concession Price','Child Price','Comment','Action'],
            ch_headers:['ID','Closure Start','Reopen','Closure Reason','Reopen Reason','Action'],
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
            }

        }
    }
}
</script>

<style lang="css">
</style>
