<template lang="html" id="pkCGADD">

   <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
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
                     <campgroundAttr @create="create" >
                        <h1 slot="cg_name">My Slot</h1>
                     </campgroundAttr>
                  </div>
               </div>
            </div>
         </div>
      </div>
   </div>

</template>

<script>
import campgroundAttr from './campground-attr.vue'
import {
    $,
    Moment,
    api_endpoints
} from '../../hooks.js'

export default {
    name: 'addCampground',
    components: {
        campgroundAttr
    },
    data: function() {
        return {
        }
    },
    methods: {
        create: function() {
            console.log('create in Campground');
            alert('Create was clicked')
        },
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
