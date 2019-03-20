<template lang="html">
    <div id="externalReturnSheetEntry">
        <modal transition="modal fade" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="returnSheetForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Activity:</label>
                                </div>
                                <div class="col-md-3">
                                    <select class="form-control" v-model="entryActivity">
                                        <option value="ALL">All</option>
                                        <option value="001">Stock</option>
                                        <option value="002">In through Import</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Quantity:</label>
                                </div>
                                <div class="col-md-3">
                                    <input type='text' v-model='entryQty' >
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Total Number:</label>
                                </div>
                                <div class="col-md-3">
                                    <input type='text' v-model='entryTotal' >
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Receiving licence:</label>
                                </div>
                                <div class="col-md-3">
                                    <input type='text' v-model='entryLicence' >
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Comments:</label>
                                </div>
                                <div class="col-md-9">
                                    <textarea style="width: 95%;"class="form-control" name="entry_comments" v-model="entryComment"></textarea>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button style="width: 15%;" class="btn btn-primary" @click.prevent="close()">Pay</button>
                <button style="width: 15%;" class="btn btn-primary" @click.prevent="update()">Update</button>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import {
    api_endpoints,
    helpers
} from "@/utils/hooks.js"
export default {
    name:'externalReturnSheetEntry',
    components:{
        modal,
        alert
    },
    props:{
            return_id:{
                type:Number,
            },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            errors: false,
            errorString: '',
            successString: '',
            success:false,
            entryActivity: '',
            entryQty: 0,
            entryTotal: 0,
            entryLicence: '',
            entryComment: '',
            currentStock: 0,
            speciesType: '',
            row_of_data: null,
            table: null
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            this.currentStock = +this.entryQty + +this.entryTotal;
            return this.speciesType + '   Current stock: ' + this.currentStock;
        }

    },
    methods:{
        update:function () {
            console.log('update function')
            var vm = this;
            vm.row_of_data.data().activity = vm.entryActivity;
            vm.row_of_data.data().qty = vm.entryQty;
            vm.row_of_data.data().total = vm.entryTotal;
            vm.row_of_data.data().licence = vm.entryLicence;
            vm.row_of_data.data().comment = vm.entryComment;
            vm.row_of_data.invalidate().draw()
            this.isModalOpen = false;
        },
        cancel:function () {
            console.log('cancel function')
            this.isModalOpen = false;
        },
        close:function () {
            console.log('close function')
            this.isModalOpen = false;
        },
        eventListeners:function () {
            let vm = this;
        }
    },
    mounted:function () {
        console.log('modal Mounted');
        let vm = this;
    }
}
</script>

<style lang="css">
</style>
