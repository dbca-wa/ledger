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
        const self = this;
        if (self.isAddEntry) {
          let _currentDateTime = new Date();
          self.entryDateTime = Date.parse(new Date());
          let newRowId = (self.row_of_data.data().count()) + '';
          let _data = { rowId: newRowId,
                        date: self.entryDateTime,
                        activity: self.entryActivity,
                        qty: self.entryQty,
                        total: self.entryTotal,
                        comment: self.entryComment,
                        licence: self.entryLicence
                      };

          if (self.isLicenceRequired) { // licence only required for stock transfers.
            _data['transfer'] = self.returns.sheet_species
            self.checkTransfer(_data)
          };

          self.row_of_data.row.add(_data).node().id = newRowId;
          self.row_of_data.draw();
          self.species_cache[self.returns.sheet_species] = self.row_of_data.ajax.json();
          self.species_cache[self.returns.sheet_species].push(self.row_of_data.context[0].aoData[newRowId]._aData);
        };

        if (self.isChangeEntry) {
          self.row_of_data.data().activity = self.entryActivity;
          self.row_of_data.data().qty = self.entryQty;
          self.row_of_data.data().total = self.entryTotal;
          self.row_of_data.data().licence = self.entryLicence;
          self.row_of_data.data().comment = self.entryComment;

          if (self.isLicenceRequired) { // licence only required for stock transfers.
            let _data = self.row_of_data.data()
            _data['transfer'] = self.returns.sheet_species
            self.checkTransfer(_data)
          };

          self.row_of_data.invalidate().draw()
          self.species_cache[self.returns.sheet_species] = self.row_of_data.ajax.json();
        };

        self.close();
      },
      pay: function() {
        const self = this;
        self.form=document.forms.external_returns_form;
        var data = new FormData(self.form);

        //  data.append(speciesID, speciesJSON)

        self.$http.post(helpers.add_endpoint_json(api_endpoints.returns,self.returns.id+'/pay'),data,{
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
        const self = this;
        self.form=document.forms.external_returns_form;
        self.errors = true;
        var data = new FormData(self.form);
        data.append('licence', self.entryLicence)
        self.$http.post(helpers.add_endpoint_json(api_endpoints.returns,self.returns.id+'/sheet_check_transfer'),data,{
                      emulateJSON:true,
                    }).then((response)=>{
                        self.errors = false;
                        return true;
                    },(error)=>{
                        console.log(error)
                        self.errorString = helpers.apiVueResourceError('Licence is not Valid.');
                        self.close;

        });
      },
      checkTransfer: function(row_data) {
        const self = this;
        self.form=document.forms.external_returns_form;
        self.isValidLicence(row_data['licence']);
        let transfer = {}  //{speciesID: {this.entryDateTime: row_data},}
        if (self.returns.sheet_species in self.species_transfer){
          transfer = self.species_transfer[self.returns.sheet_species]
        } 
        transfer[self.entryDateTime] = row_data;
        self.species_transfer[self.returns.sheet_species] = transfer
      },
      cancel: function() {
        const self = this;
        self.errors = false;
        self.close()
      },
      close: function() {
        const self = this;
        if (!self.errors) {
          self.isChangeEntry = false;
          self.isAddEntry = false;
          self.isModalOpen = false;
        }
      },
    },
}
</script>
