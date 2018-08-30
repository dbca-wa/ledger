<!DOCTYPE html>
<template id="admissionsCost">
    <div class="container">
        <div class="row">
            <div class="well">
                <h3>Admissions Fees</h3>

                <div class="col-lg-12">
                      <price-history  :addParkPrice="true" :dt_options="priceHistoryDt" :dt_headers="priceHistoryDtHeaders" :object_id="35" level='park' ></price-history>
                  </div>
            </div>            
        </div>
    </div>
</template>

<script>
import priceHistory from './priceHistory/priceHistory.vue'
export default {
    name: 'admissionsCost',
    el: '#admissionsCosts',
    
    components: {

    },
    computed: {
    },
    data: function() {
    
    },
    methods: {
        
    },
    mounted: function() {
        
    }
}
</script>

<style>
</style>
