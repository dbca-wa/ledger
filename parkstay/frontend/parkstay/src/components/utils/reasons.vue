<template lang="html">
    <div class="row" id="reasons">
        <div class="form-group">
            <div class="col-md-2">
                <label for="open_cg_reason">Reason: </label>
            </div>
            <div class="col-md-4">
                <select v-if="!reasons.length > 0" class="form-control" >
                    <option value="">Loading...</option>
                </select>
                <select v-else name="open_reason" v-model="selected" class="form-control" id="open_cg_reason">
                    <option value=""></option>
                    <option v-for="reason in reasons" :value="reason.id">{{reason.text}}</option>
                </select>
            </div>
        </div>
    </div>
</template>

<script>
import {
    $,
    api_endpoints,
    bus
}from '../../hooks.js'
export default {
    name:'reasons',
    data:function () {
        let vm =this;
        return {
            reasons:[],
            selected:''
        }
    },
    props:{
        type:{
            required:true
        }
    },
    watch:{
        selected:function () {
            this.$emit('reason_updated',this.selected);
        }
    },
    methods:{
        fetchOpenReasons:function () {
            let vm = this;
            $.get(api_endpoints.openReasons(),function (data) {
                vm.reasons = data;
            });
        },
        fetchClosureReasons:function () {
            let vm = this;
            $.get(api_endpoints.closureReasons(),function (data) {
                vm.reasons = data;
            });
        },
        fetchMaxStayReasons:function () {
            let vm = this;
            $.get(api_endpoints.maxStayReasons(),function (data) {
                vm.reasons = data;
            });
        },
        fetchPriceReasons:function () {
            let vm = this;
            $.get(api_endpoints.priceReasons(),function (data) {
                vm.reasons = data;
            });
        },
    },
    mounted:function(){
        let vm =this;
        if(vm.type){
            switch (vm.type.toLowerCase()) {
                case 'close':
                    vm.fetchClosureReasons();
                    break;
                case 'open':
                    vm.fetchOpenReasons();
                    break;
                case 'stay':
                    vm.fetchMaxStayReasons();
                    break;
                case 'price':
                    vm.fetchPriceReasons();
                    break;
            }
        }
    }
}
</script>

<style lang="css">
</style>
