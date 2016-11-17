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
                        <div class="col-sm-8">
                            <h1>Maximum Stay History</h1>
                        </div>
                        <div class="col-sm-4">
                         <button @click="showAddStay()" class="btn btn-primary pull-right table_btn">Add Max Stay Period</button>
                        </div>
                         <datatable ref="addMaxStayModal" :dtHeaders ="msh_headers" :dtOptions="msh_options" :table.sync="msh_table" id="stay_history"></datatable>
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
                         <button class="btn btn-primary pull-right table_btn">Add Closure Period</button>
                        </div>
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
    $
} from '../../hooks.js';
import datatable from '../utils/datatable.vue'
export default {
    name:'campsite',
    components:{
        datatable
    },
    data:()=>{
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
            msh_options:{
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            ph_options:{
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            ch_options:{
                responsive: true,
                processing: true,
                deferRender: true,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            }

        }
    }
}
</script>

<style lang="css">
    .table_btn {
        margin-top: 25px;
        margin-right: -14px;
    }
</style>
