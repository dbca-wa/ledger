<template lang="html">
    <div id="campsite-type">
       <div class="panel panel-default" id="applications">
         <div class="panel-heading" role="tab" id="applications-heading">
             <h4 class="panel-title">
                 <a role="button" data-toggle="collapse" href="#applications-collapse"
                    aria-expanded="false" aria-controls="applications-collapse">
                     <h3>Campsite Type</h3>
                 </a>
             </h4>
         </div>
         <div id="applications-collapse" class="panel-collapse collapse in" role="tabpanel"
              aria-labelledby="applications-heading">
          </div>
       </div>
   </div>
</template>

<script>
import {
    $,
    api_endpoints,
    helpers,
    Moment,
    bus
}
from '../../hooks.js';
import datatable from '../utils/datatable.vue'
import confirmbox from '../utils/confirmbox.vue'
import loader from '../utils/loader.vue'
import closureHistory from '../utils/closureHistory.vue'
import priceHistory from '../utils/priceHistory/priceHistory.vue'
export default {
    name: 'campsite-type',
    components: {
    },
    computed: {

    },
    data: function() {
        let vm = this;
        return {

        }
    },
    watch: {

    },
    methods: {
        goBack: function() {
            helpers.goBack(this);
        },

    },
    mounted: function() {
        let vm = this;
    }
}

</script>

<style lang="css">

</style>
