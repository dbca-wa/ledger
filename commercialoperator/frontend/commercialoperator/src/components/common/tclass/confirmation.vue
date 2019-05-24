<template lang="html">

    <div class="container">
        <div class="well">
            <div v-if="proposal.fee_paid" class="row">
                <div class="col-sm-12">
                    <h2>Application Fee: Paid</h2>
                    <p>A confirmation email has been sent to {{proposal.applicant }}. </p>
                </div>
            </div>
            <div v-else class="row">
                <div class="col-sm-12">
                <h2>Application Fee: Unpaid</h2>
            </div>
        </div>
        <div v-if="proposal.fee_paid" class="row">
            <div class="col-sm-12" style="margin-top: 1em">
                <a :href="proposal.fee_invoice_url" class="btn btn-info btn-lg"  target="_blank">Invoice</a>
            </div>
        </div>
    </div>

</template>

<script>
    export default {
        name:'application_fee',
        components:{
        },
        props:{
            proposal:{
                type: Object,
                required:true
            }
        },
        data:function () {
            return {
            }
        },
        computed: {
            fee_invoice_url: function(){
                return this.fee_paid ? this.proposal.fee_invoice_url : '';
            }
        },
        methods:{
        },
        mounted:function () {
        }
    }
</script>

<style lang="css" scoped>
</style>

