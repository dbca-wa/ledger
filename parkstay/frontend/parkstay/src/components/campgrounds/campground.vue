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
                     <campgroundAttr @create="create" >
                        <h1 slot="cg_name">My Slot</h1>
                     </campgroundAttr>
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
import datatable from '../utils/datatable.vue'
import campgroundAttr from './campground-attr.vue'
import {$,Moment} from '../../hooks.js'

export default {
   name:'campground',
   components:{
      datatable,campgroundAttr
   },
   data:function () {
      return {
         options : {
            responsive:true,
            processing:true,
            deferRender: true,
            ajax:{
               url:'/api/campgrounds/'+this.$route.params.id+'/status_history.json',
               dataSrc:''
            },
            columns:[
               {
                  data:'range_start',
                  mRender:function (data,type,full) {
                     return Moment(data).format('MMMM Do, YYYY');
                  }

               },
               {
                  data:'range_end',
                  mRender:function (data,type,full) {
                     return Moment(data).format('MMMM Do, YYYY');
                  }

               },
               {data: 'details'},
               {
                  data:'editable',
                  mRender:function (data,type,full) {
                     if (data){
                        return "<a href=#'>Edit</a>";
                     }
                     else{ return "" }
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
   },
   methods:{
      create:function () {
         console.log('create in Campground');
         alert('Create was clicked')
      }
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
