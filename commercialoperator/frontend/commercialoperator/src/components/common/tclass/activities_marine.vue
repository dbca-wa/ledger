<template lang="html">
    <div>
      <div v-if="proposal.processing_status=='Draft'">
        Activities Marine: <input type="text" name="activities_marine" :value="proposal.activities_marine.activities_marine"><br>
      </div>
      <div v-else>
        Activities Marine: <input readonly="readonly" type="text" name="activities_marine" :value="proposal.activities_marine.activities_marine"><br>
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

