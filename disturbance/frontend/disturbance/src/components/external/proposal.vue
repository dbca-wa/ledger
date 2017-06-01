<template lang="html">
    <div >
        <form action="/" method="post" name="new_proposal">
            <Proposal v-if="!isLoading" :proposal="proposal" >
                <input type="button" class="btn btn-primary" @click.prevent.stop="submit" value="Save">
            </Proposal>
        </form>
    </div>
</template>
<script>
import Proposal from '../form.vue'
import {api_endpoints } from '@/utils/hooks'
export default {
    data:function () {
        return {
            "proposal":[],
            "loading":[],
            form:null
        }
    },
    components:{
        Proposal
    },
    computed:{
        isLoading:function () {
            return this.loading.length > 0
        }
    },
    methods:{
        submit:function (e) {
            let vm =this;
            console.log($(vm.form).serializeArray());
        }
    },
    mounted:function(){
        let vm = this;
        vm.form = document.forms.new_proposal;
        var url = api_endpoints.proposal_type;
        vm.loading.push('fetching proposal');
        vm.$http.get(url).then((response)=>{
            vm.proposal = response.body.schema;
            vm.loading.splice('fetching proposal',1);
        },(response)=>{
            console.log(response);
            vm.loading.splice('fetching proposal',1);
        });

    }
}
</script>

<style lang="css">
</style>
