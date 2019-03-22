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
                                        <option v-for="(value, key) in activityList" :value="key">{{value}}</option>
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
                                    {{ entryTotal }}
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
            entryDateTime: '',
            entryActivity: '',
            entryQty: 0,
            entryTotal: 0,
            entryLicence: '',
            entryComment: '',
            currentStock: 0,
            speciesType: '',
            row_of_data: null,
            table: null,
            isAddEntry: false,
            isChangeEntry: false,
            activityList: []
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        title: function(){
            this.currentStock = +this.entryTotal;
            return this.speciesType + '   Current stock: ' + this.currentStock;
        }

    },
    methods:{
        update:function () {
            console.log('update function')
            var vm = this;

            if (vm.entryActivity.match(/^(SA01|SA02|SA03|SA04)$/)) {
              vm.entryTotal = vm.entryTotal + vm.entryQty
            }

            if (vm.entryActivity.match(/^(SA05|SA06|SA07|SA08)$/)) {
              vm.entryTotal = vm.entryTotal - vm.entryQty
            }

            if (vm.isAddEntry) {
              var _currentDateTime = new Date()
              vm.entryDateTime = Date.parse(new Date())
              let newRowId = (vm.row_of_data.data().count()-1) + ''
              let _data = { rowId: newRowId,
                            date: vm.entryDateTime,
                            activity: vm.entryActivity,
                            qty: vm.entryQty,
                            total: vm.entryTotal,
                            comment: vm.entryComment,
                            licence: vm.entryLicence
                          };
              vm.row_of_data.row.add(_data).node().id = newRowId
              vm.row_of_data.draw()
              vm.isAddEntry = false;
            }

            if (vm.isChangeEntry) {
              vm.row_of_data.data().activity = vm.entryActivity;
              vm.row_of_data.data().qty = vm.entryQty;
              vm.row_of_data.data().total = vm.entryTotal;
              vm.row_of_data.data().licence = vm.entryLicence;
              vm.row_of_data.data().comment = vm.entryComment;
              vm.row_of_data.invalidate().draw()
              vm.isChangeEntry = false
            }

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
        console.log(vm)
    }
}
</script>

<style lang="css">
</style>
