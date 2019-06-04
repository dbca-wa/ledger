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
                                <div class="col-md-6" v-show="isAddEntry">
                                <select class="form-control" v-model="entryActivity">
                                  <option v-for="(activity, activityId) in activityList" :value="activityId">{{activity['label']}}</option>
                                </select>
                                </div>
                                <div class="col-md-3" v-show="isChangeEntry">
                                    <label>{{activityList[entryActivity]['label']}} </label>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="control-label pull-left" for="Name">Quantity:</label>
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
                                    <input type='text' v-model='computeTotal' disabled='true' >
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
                <button v-show="isPayable" style="width:150px;" class="btn btn-primary" @click.prevent="close()">Pay</button>
                <button v-show="isSubmitable" style="width:150px;" class="btn btn-primary" @click.prevent="update()">Update</button>
                <button style="width:150px;" class="btn btn-primary" @click.prevent="close()">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import { mapActions, mapGetters } from 'vuex'
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
        entrySpecies: '',
        entryDateTime: '',
        entryActivity: 'null',
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
        isPayable: false,
        isSubmitable: false,
        activityList: {'null': {'label': null}},
      }
    },
    computed: {
      ...mapGetters([
        'species_cache',
        'returns',
      ]),
      showError: function() {
        return this.errors;
      },
      title: function(){
        this.currentStock = +this.entryTotal;
        return this.entrySpecies + '   Current stock: ' + this.computeTotal;
      },
      computeTotal: function() {
        let new_total = 0
        if (this.entryActivity in this.returns.sheet_activity_inward) { // Tansfer-Ins
            new_total = this.entryTotal + (this.entryQty !== '' ? parseInt(this.entryQty) : 0)
        } else {
            new_total = this.entryTotal - (this.entryQty !== '' ? parseInt(this.entryQty) : 0)
        }
        this.entryTotal = new_total
        return new_total
      },
    },
    methods:{
      update:function () {
        if (this.isAddEntry) {
          let _currentDateTime = new Date()
          this.entryDateTime = Date.parse(new Date())
          let newRowId = (this.row_of_data.data().count()) + ''
          let _data = { rowId: newRowId,
                        date: this.entryDateTime,
                        activity: this.entryActivity,
                        qty: this.entryQty,
                        total: this.entryTotal,
                        comment: this.entryComment,
                        licence: this.entryLicence
                      };
          this.row_of_data.row.add(_data).node().id = newRowId
          this.row_of_data.draw()
          this.species_cache[this.returns.sheet_species] = this.row_of_data.ajax.json()
          this.species_cache[this.returns.sheet_species].push(this.row_of_data.context[0].aoData[newRowId]._aData)
        }

        if (this.isChangeEntry) {
          this.row_of_data.data().activity = this.entryActivity;
          this.row_of_data.data().qty = this.entryQty;
          this.row_of_data.data().total = this.entryTotal;
          this.row_of_data.data().licence = this.entryLicence;
          this.row_of_data.data().comment = this.entryComment;
          this.row_of_data.invalidate().draw()
        }

        this.close();
      },
      cancel:function () {
        this.close()
      },
      close:function () {
        this.isChangeEntry = false;
        this.isAddEntry = false;
        this.isModalOpen = false;
      },
    },
}
</script>

<style lang="css">
</style>
