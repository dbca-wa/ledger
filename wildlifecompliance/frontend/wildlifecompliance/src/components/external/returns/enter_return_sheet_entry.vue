<template lang="html">
    <div id="externalReturnSheetEntry">
        <modal transition="modal fade" title="[Species Type 1]  Current stock: 75" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="returnSheetForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Activity:</label>
                                </div>
                                <div class="col-md-6">
                                    <input type='text' v-model='entryActivity'>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Number:</label>
                                </div>
                                <div class="col-md-6">
                                    <input type='text' v-model='entryNumber' >
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Total Number:</label>
                                </div>
                                <div class="col-md-6">
                                    <input type='text' v-model='entryTotalNumber' >
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Receiving licence:</label>
                                </div>
                                <div class="col-md-6">
                                    <input type='text' v-model='entryLicence' >
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left"  for="Name">Comments:</label>
                                </div>
                                <div class="col-md-6">
                                    <textarea style="width: 95%;"class="form-control" name="entry_comments" v-model="entryComments"></textarea>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button class="btn btn-primary" @click.prevent="close()">Pay</button>
                <button class="btn btn-primary" @click.prevent="close()">Cancel</button>
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
            entryActivity: 'Out through transfer other',
            entryNumber: '45',
            entryTotalNumber: '30',
            entryLicence: 'L245375',
            entryComments: '',
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        }
    },
    methods:{
        ok:function () {
            let vm =this;
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
        let vm =this;
    }
}
</script>

<style lang="css">
</style>
