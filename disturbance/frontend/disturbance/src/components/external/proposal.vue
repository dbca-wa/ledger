<template lang="html">
    <div >
        <form action="/" method="post">
            <Proposal :proposal="proposal" />
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
    }
}
</script>

<style lang="css">
</style>
