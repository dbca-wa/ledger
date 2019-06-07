<template lang="html">
    <div id="externalReturnSheetEntry">
        <modal transition="modal fade" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                        <div class="row">
                            <div class="col-md-3">
                                <label class="control-label pull-left"  for="Name">Activity:</label>
                            </div>
                            <div class="col-md-6" v-show="isAddEntry">
                                <select class="form-control" v-model="entryActivity">
                                    <option v-for="(activity, activityId) in activityList" v-if="activity['auto']=='false'" :value="activityId">{{activity['label']}}</option>
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
                        <div class="row" v-if="isLicenceRequired">
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
                </div>
            </div>
            <div slot="footer">
                <button v-show="!isPayable" style="width:150px;" class="btn btn-primary" @click.prevent="update()">Update</button>
                <button v-show="isPayable" style="width:150px;" class="btn btn-primary" >Pay</button>
                <button style="width:150px;" class="btn btn-primary" @click.prevent="cancel()">Cancel</button>
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
        entryActivity: '0',
        entryQty: 0,
        entryTotal: 0,
        entryLicence: '',
        entryComment: '',
        currentStock: '0',
        speciesType: '',
        row_of_data: null,
        table: null,
        isAddEntry: false,
        isChangeEntry: false,
        activityList: {'0': {'label': null, 'licence': false, 'pay': false}},
      }
    },
    computed: {
      ...mapGetters([
        'species_cache',
        'returns',
        'species_transfer',
      ]),
      showError: function() {
        return this.errors;
      },
      title: function(){
        return this.entrySpecies + '   Current stock: ' + this.computeTotal;
      },
      computeTotal: function() {
        if (this.isInStock) {
            this.entryTotal = parseInt(this.entryTotal) + (this.entryQty !== '' ? parseInt(this.entryQty) : 0)
        } else {
            this.entryTotal = parseInt(this.entryTotal) - (this.entryQty !== '' ? parseInt(this.entryQty) : 0)
        };
        if (this.isLicenceRequired) { // notify required before total update.
            this.entryTotal = parseInt(this.currentStock)
        };
        return this.entryTotal;
      },
      isOutStock: function() {
        return 'outward' in this.returns.sheet_activity_list[this.entryActivity] ? true : false
      },
      isInStock: function() {
        return 'inward' in this.returns.sheet_activity_list[this.entryActivity] ? true : false
      },
      isLicenceRequired: function() {
        return (this.returns.sheet_activity_list[this.entryActivity]['licence'] === 'true');
      },
      isPayable: function() {
        return (this.returns.sheet_activity_list[this.entryActivity]['pay'] === 'true');
      },
    },
    methods:{
      update:function () {
        if (this.isAddEntry) {
          let _currentDateTime = new Date();
          this.entryDateTime = Date.parse(new Date());
          let newRowId = (this.row_of_data.data().count()) + '';
          let _data = { rowId: newRowId,
                        date: this.entryDateTime,
                        activity: this.entryActivity,
                        qty: this.entryQty,
                        total: this.entryTotal,
                        comment: this.entryComment,
                        licence: this.entryLicence
                      };
          if (this.isLicenceRequired) { // licence only required for stock transfer.
            _data['transfer'] = ''
            this.checkTransfer(_data)
          };
          this.row_of_data.row.add(_data).node().id = newRowId;
          this.row_of_data.draw();
          this.species_cache[this.returns.sheet_species] = this.row_of_data.ajax.json();
          this.species_cache[this.returns.sheet_species].push(this.row_of_data.context[0].aoData[newRowId]._aData);
        };

        if (this.isChangeEntry) {
          this.row_of_data.data().activity = this.entryActivity;
          this.row_of_data.data().qty = this.entryQty;
          this.row_of_data.data().total = this.entryTotal;
          this.row_of_data.data().licence = this.entryLicence;
          this.row_of_data.data().comment = this.entryComment;

          if (this.isLicenceRequired) { // licence only required for stock transfer.
            let _data = this.row_of_data.data()
            _data['transfer'] = ''
            this.checkTransfer(_data)
          };

          this.row_of_data.invalidate().draw()
        };

        this.close();
      },
      pay: function() {
        this.form=document.forms.external_returns_form;
        var data = new FormData(this.form);

        //  data.append(speciesID, speciesJSON)

        this.$http.post(helpers.add_endpoint_json(api_endpoints.returns,this.returns.id+'/pay'),data,{
                      emulateJSON:true,
                    }).then((response)=>{
                       //let species_id = this.returns.sheet_species;
                       //this.setReturns(response.body);
                       //this.returns.sheet_species = species_id;
                       swal('Save',
                            'Return Details Paid',
                            'success'
                       );
                    },(error)=>{
                        console.log(error);
        });
      },
      isValidLicence: function(licence) {
        this.form=document.forms.external_returns_form;
        this.errors = true;
        var data = new FormData(this.form);

        //  data.append(speciesID, speciesJSON)

        this.$http.post(helpers.add_endpoint_json(api_endpoints.returns,this.returns.id+'/sheet_check_transfer'),data,{
                      emulateJSON:true,
                    }).then((response)=>{
                       //let species_id = this.returns.sheet_species;
                       //this.setReturns(response.body);
                       //this.returns.sheet_species = species_id;
                        this.errors = false;
                        return true
                    },(error)=>{
                        console.log(error)
                        this.errorString = helpers.apiVueResourceError('Licence is not Valid.');
                        this.close;

        });

      },
      checkTransfer: function(row_data) {
        this.form=document.forms.external_returns_form;
        this.isValidLicence(row_data['licence']);
        let transfer = {}
        transfer[this.returns.sheet_species] = row_data
        this.species_transfer['transfer'] = transfer;
      },
      cancel: function() {
        this.errors = false;
        this.close()
      },
      close: function() {
        if (!this.errors) {
          this.isChangeEntry = false;
          this.isAddEntry = false;
          this.isModalOpen = false;
        }
      },
    },
}
</script>
