<template id="proposal_dashboard">
    <div class="row">
        <p>Payments Dashboard</p>

        <div class="col-md-3">
            <router-link  style="margin-top:25px;" class="btn btn-primary pull-right" :to="{ name: 'payment_order' }">Make Payment</router-link>
        </div>

        <!--
        <PaymentOrder ref="payment_order"  @refreshFromResponse="refreshFromResponse"/>
        <div v-if="is_external" class="col-md-3">
        <ApprovalExtend ref="approval_extend"  @refreshFromResponse="refreshFromResponse"></ApprovalExtend>
        <EClassLicence ref="eclass_licence"></EClassLicence>
        -->

    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import Vue from 'vue'
//import ApprovalExtend from '../internal/approvals/approval_extend.vue'
//import EClassLicence from '../internal/approvals/approval_eclass.vue'
import PaymentOrder from '@/components/common/tclass/payment_order.vue'

import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'ProposalTableDash',
    props: {
        level:{
            type: String,
            required: true,
            validator:function(val) {
                let options = ['internal','referral','external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        url:{
            type: String,
            required: true
        }
    },
    components:{
        datatable,
        PaymentOrder,
        //ApprovalExtend,
        //EClassLicence,
    },
    data() {
        let vm = this;
        return {

            }
    },
    watch:{
    },
    computed: {
        is_external: function(){
            return this.level == 'external';
        },
        is_internal: function(){
            return this.level == 'internal';
        }
    },
    methods:{
        createEClassLicence: function(){
            //this.save_wo();
            this.$refs.eclass_licence.isModalOpen = true;
        },

        extendApproval: function(approval_id){
            this.$refs.approval_extend.approval_id = approval_id;
            this.$refs.approval_extend.isModalOpen = true;
        },

        refreshFromResponse: function(){
            this.$refs.proposal_datatable.vmDataTable.ajax.reload();
        }
    },
    mounted: function(){
    }
}
</script>
<style scoped>
</style>
