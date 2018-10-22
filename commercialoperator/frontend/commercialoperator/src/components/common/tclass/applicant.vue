<template lang="html">
    <div>
      <div v-if="proposal.processing_status=='Draft'">
        First name: <input type="text" name="first_name" :value="proposal.applicant_details.first_name"><br>
      </div>
      <div v-else>
        First name: <input readonly="readonly" type="text" name="first_name" :value="proposal.applicant_details.first_name"><br>
      </div>
    </div>
</template>

<script>
    export default {
        //props:["type","name","id", "comment_value","value","isRequired","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly", "help_text_url", "help_text_assessor_url"],
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

