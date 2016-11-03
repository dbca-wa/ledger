<template lang="html">

   <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
      <div class="panel panel-default" id="applications">
           <div class="panel-heading" role="tab" id="applications-heading">
               <h4 class="panel-title">
                   <a role="button" data-toggle="collapse" href="#applications-collapse"
                      aria-expanded="true" aria-controls="collapseOne">
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
                           <h1>Campground attributes</h1>
                        </div>
                     </div>
                     <div class="row">
                        <div class="well">
                           <h1>Price History</h1>
                        </div>
                     </div>
                     <div class="row">
                        <div class="well">
                           <datatable :dtHeaders ="headers" :dtOptions="options"/>
                        </div>
                     </div>
                  </div>
               </div>
           </div>
      </div>
   </div>




</template>

<script>
import datatable from './datatable.vue'
export default {
   name:'campground',
   components:{
      datatable
   },
   data:function () {
      return {
         options : {
            responsive:true,
            processing:true,
            ajax:'/api/campgrounds/1/status_history.json',
            columns:[
               {data:'range_start'},
               {data: 'range_end'},
               {data: 'details'},
               {
                  mRender:function (data,type,full) {
                     return "<a href=#'>Edit</a>";
                  }
               }
            ],
            language: {
                processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
            },
         },
         headers:['Closure Start','Reopen', 'Closure Reason', 'Action'],
         title: 'Campground'
      }
   }
}
</script>

<style lang="css">
.well{
   background-color: #fff;
}
</style>
