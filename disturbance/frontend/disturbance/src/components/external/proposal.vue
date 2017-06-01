<template lang="html">
    <div >
        <form action="/" method="post" name="new_proposal">
            <Proposal :proposal="proposal" />
            <input type="button" @click.prevent.stop="submit">
        </form>
    </div>
</template>

<script>
import Proposal from '../form.vue'
const data = require("@/assets/data.json")
export default {
    data:function () {
        return {
            "proposal":data
        }
    },
    components:{
        Proposal
    },
    methods:{
        submit:function (e) {
            console.log($(form).serializeArray());
        }
    },
    mounted:function(){
        var form = document.forms.new_proposal;
    }
}
</script>

<style lang="css">
</style>
