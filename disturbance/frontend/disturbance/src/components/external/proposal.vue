<template lang="html">
    <div >
        <form action="/proposal/" method="post" name="new_proposal" enctype="multipart/form-data">
            <Proposal v-if="!isLoading" :proposal="proposal" :data="ans">
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token">
                <input type="submit" class="btn btn-primary" value="Save"/>
            </Proposal>
        </form>
    </div>
</template>
<script>
import Proposal from '../form.vue'
import {api_endpoints,helpers } from '@/utils/hooks'
export default {
    data:function () {
        return {
            "proposal":[],
            "loading":[],
            form:null,
            "ans":require('@/assets/ans.json')
        }
    },
    components:{
        Proposal
    },
    computed:{
        isLoading:function () {
            return this.loading.length > 0
        },
        csrf_token:function () {
            return helpers.getCookie('csrftoken')
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
