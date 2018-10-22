<template lang="html">
    <div>
      <div v-if="proposal.processing_status=='Draft'">
        Activities Land: <input type="text" name="activities_land" :value="proposal.activities_land.activities_land"><br>
      </div>
      <div v-else>
        Activities Land: <input readonly="readonly" type="text" name="activities_land" :value="proposal.activities_land.activities_land"><br>
      </div>
    </div>
</template>

<script>
    export default {
        props:{
            proposal:{
                type: Object,
                required:true
            }
        },
        data:function () {
            return{
                values:null
            }
        },
        methods:{
        }
    }
</script>

<style lang="css" scoped>
</style>

