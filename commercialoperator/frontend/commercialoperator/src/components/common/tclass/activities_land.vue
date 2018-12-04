<template lang="html">
    <div>
      <div v-for="a in accessTypes">
        <div>Access Types: {{a.name}}</div>
      </div>
      <div v-if="proposal.processing_status=='Draft'">
        <!-- Activities Land: <input type="text" name="activities_land" :value="proposal.activities_land.activities_land"><br> -->
      </div>
      <div v-else>
        <!-- Activities Land: <input readonly="readonly" type="text" name="activities_land" :value="proposal.activities_land.activities_land"><br> -->
      </div>
    </div>
</template>


<script>
import Vue from 'vue' 
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
        props:{
            proposal:{
                type: Object,
                required:true
            }
        },
        data:function () {
            return{
                values:null,
                accessTypes:null,
            }
        },
        methods:{
        },
        mounted: function() {
            let vm = this;
            Vue.http.get('/api/access_types.json').then((res) => {
                     
                      vm.accessTypes=res.body;
                      console.log(vm.accessTypes);
                  
                },
              err => { 
                        console.log(err);
                  });    
        }
    }
</script>

<style lang="css" scoped>
</style>

