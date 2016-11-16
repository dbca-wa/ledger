<template lang="html">
    <div id="campsite">
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
                       <div class="well">
                           <campsiteAttr :createCampsite="createCampsite" :campsite.sync="campsite"></campsiteAttr>
                       </div>
                   </div>
                   <div class="row">
                      <div class="well">
                         <h1>Maximum Stay History</h1>
                         <datatable :dtHeaders ="msh_headers" :dtOptions="msh_options" id="msh_table"></datatable>
                      </div>
                   </div>
                   <div class="row">
                      <div class="well">
                         <h1>Price History</h1>
                         <datatable :dtHeaders ="ph_headers" :dtOptions="ph_options" id="ph_table"></datatable>
                      </div>
                   </div>
                   <div class="row">
                      <div class="well">
                         <h1>Closure History</h1>
                         <datatable :dtHeaders ="ch_headers" :dtOptions="ch_options" id="cg_table"></datatable>
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

export default {
    name:'campsite',
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
            msh_options:()=>{
                let vm =this;
                return $.extend({},{

                },vm.default_dtOptions);
            },
            ph_options:()=>{
                let vm =this;
                return $.extend({},{

                },vm.default_dtOptions);
            },
            ch_options:()=>{
                let vm =this;
                return $.extend({},{

                },vm.default_dtOptions);
            }



        }
    }
}
</script>

<style lang="css">
</style>
