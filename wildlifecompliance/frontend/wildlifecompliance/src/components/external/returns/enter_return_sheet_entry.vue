<template lang="html">
    <div id="externalReturnSheetEntry">
        <modal transition="modal fade" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                <form class="form-horizontal" name="sheetEntryForm">
                    <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                        <div class="row">
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Activity:</label>
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
                                <label class="control-label pull-left" >Quantity:</label>
                            </div>
                            <div class="col-md-3">
                                <input type='text' v-model='entryQty' >
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Total Number:</label>
                            </div>
                            <div class="col-md-3">
                                <input type='text' v-model='entryTotal' disabled='true' >
                            </div>
                        </div>
                        <div class="row" v-if="isLicenceRequired">
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Receiving licence:</label>
                            </div>
                            <div class="col-md-3">
                                <input type='text' v-model='entryLicence' >
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-3">
                                <label class="control-label pull-left" >Comments:</label>
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
        validation_form: null,
        successString: '',
        success:false,
        entrySpecies: '',
        entryDateTime: '',
        entryActivity: '0',
        entryQty: 0,
        entryTotal: 0,
        entryLicence: '',
        entryComment: '',
        entryTransfer: '',
        currentStock: 0,
        speciesType: '',
        row_of_data: null,
        return_table: null,
        table: null,
        isAddEntry: false,
        isChangeEntry: false,
        activityList: {'0': {'label': null, 'licence': false, 'pay': false}},
        initialQty: 0,
      }
    },
    watch: {
      entryQty: function(value) {
        this.addToStock(value)
      },
      entryActivity: function(value) {
        this.addToStock(this.entryQty);
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
        return this.entrySpecies + '   Current stock: ' + this.entryTotal;
      },
      isLicenceRequired: function() {
        return (this.returns.sheet_activity_list[this.entryActivity]['licence'] === 'true');
      },
      isPayable: function() {
        return (this.returns.sheet_activity_list[this.entryActivity]['pay'] === 'true');
      },
    },
    methods:{
      isOutStock: function(activity) {
        return 'outward' in this.returns.sheet_activity_list[activity] ? true : false
      },
      isInStock: function(activity) {
        return 'inward' in this.returns.sheet_activity_list[activity] ? true : false
      },
      isStock: function(activity) {
        return 'initial' in this.returns.sheet_activity_list[activity] ? true : false
      },
      addToStock: function(value) {
        this.entryTotal = this.currentStock !== '' ? parseInt(this.currentStock) : 0
        if (this.isInStock(this.entryActivity)) {
            this.entryTotal = parseInt(this.entryTotal) + parseInt(value) - parseInt(this.initialQty)
        };
        if (this.isStock(this.entryActivity)) {
            this.entryTotal = parseInt(value)
        };
        if (this.isOutStock(this.entryActivity)) {
            this.entryTotal = parseInt(this.entryTotal) - parseInt(value) + parseInt(this.initialQty)
        };
        if (this.isLicenceRequired || this.entryActivity === '0') { // notify required before total update.
            this.entryTotal = parseInt(this.currentStock)
        };
      },
      update:function () {
        const self = this;

        if (self.isAddEntry) {

          let _currentDateTime = new Date();
          self.entryDateTime = Date.parse(new Date());
          let newRowId = (self.row_of_data.data().count()) + '';

          var _data = { rowId: newRowId,
                        date: self.entryDateTime,
                        activity: self.entryActivity,
                        qty: self.entryQty,
                        total: self.entryTotal,
                        comment: self.entryComment,
                        licence: self.entryLicence,
                        transfer: self.entryTransfer,
                      };

          if (self.isLicenceRequired) { // licence only required for transfers.

              self.validateTransfer(_data)

          } else {

              self.row_of_data.row.add(_data).node().id = newRowId;
              self.row_of_data.draw();
              self.species_cache[self.returns.sheet_species] = self.return_table.data();
              self.close();
          }

        };

        if (self.isChangeEntry) {

          var _data = self.row_of_data.data()
          _data.activity = self.entryActivity;
          _data.qty = self.entryQty;
          _data.total = self.entryTotal;
          _data.licence = self.entryLicence;
          _data.comment = self.entryComment;
          _data.transfer = self.entryTransfer;

          if (self.isLicenceRequired) { // licence only required for transfers.

              self.validateTransfer(_data);

          } else {

              self.adjustTotals()
              self.row_of_data.invalidate().draw()
              self.species_cache[self.returns.sheet_species] = self.return_table.data();
              self.close()

          }

        };

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
      validateTransfer: function(row_data) {
        const self = this;
        self.form=document.forms.external_returns_form;
        self.errors = false;
        var is_valid = false;
        var data = new FormData(self.form);
        row_data['species_id'] = self.returns.sheet_species;
        row_data['transfer'] = 'Notified';
        data.append('transfer', JSON.stringify(row_data))
        self.$http.post(helpers.add_endpoint_json(api_endpoints.returns,self.returns.id+'/sheet_check_transfer'),data,{
                      emulateJSON:true,
                    }).then((response)=>{

                        if (self.isAddEntry) {

                            self.row_of_data.row.add(row_data).node().id = row_data.rowId;
                            self.row_of_data.draw();
                            self.species_cache[self.returns.sheet_species] = self.return_table.data();

                        } else {  // Changing records only

                            self.row_of_data.data().activity = self.entryActivity;
                            self.row_of_data.data().qty = self.entryQty;
                            self.row_of_data.data().total = self.entryTotal;
                            self.row_of_data.data().licence = self.entryLicence;
                            self.row_of_data.data().comment = self.entryComment;
                            self.row_of_data.data().transfer = self.entryTransfer;
                            self.row_of_data.invalidate().draw()
                            self.species_cache[self.returns.sheet_species] = self.return_table.data();
                        }

                        let transfer = {}  //{speciesID: {this.entryDateTime: row_data},}
                        if (self.returns.sheet_species in self.species_transfer){
                            transfer = self.species_transfer[self.returns.sheet_species]
                        }
                        transfer[self.entryDateTime] = row_data;
                        self.species_transfer[self.returns.sheet_species] = transfer
                        self.close()

                    },(error)=>{
                        console.log(error)
                        self.errors = true;
                        //self.errorString = helpers.apiVueResourceError('Licence is not Valid.');
                        self.errorString = 'Error with Validation'
        });
        return true;
      },
      cancel: function() {
        const self = this;
        self.errors = false;
        self.close()
      },
      adjustTotals: function() { // update total value on subsequent rows.
        const self = this;
        if (parseInt(self.entryQty) === parseInt(self.initialQty)) { // no change to quantity amount.
          return true;
        }
        var rows = self.species_cache[self.returns.sheet_species];
        for (let i=0; i<rows.length; i++) {
          if (parseInt(rows[i].date)>parseInt(self.entryDateTime)){ // activity is after selected row.

              if (this.isStock(self.entryActivity)) { // Initial Stock entries aggregate from Current Stock.
                  rows[i].total = parseInt(rows[i].total) + (parseInt(self.entryQty) - parseInt(self.currentStock));
              } else {
                  rows[i].total = parseInt(rows[i].total) + (parseInt(self.entryQty) - parseInt(self.initialQty))
              }
          }
        }
        self.species_cache[self.returns.sheet_species] = rows;
        self.row_of_data.clear().draw();
        self.row_of_data.rows.add(self.species_cache[self.returns.sheet_species]);
        self.row_of_data.draw();
      },
      close: function() {
        const self = this;
        if (!self.errors) {
          self.isChangeEntry = false;
          self.isAddEntry = false;
          self.isModalOpen = false;
        }
      },
      addFormValidations: function() {
        let vm = this;
        vm.validation_form = $(vm.form).validate({
                rules: {
                    reason: "required"

                },
                messages: {
                    reason: "field is required",

                },
                showErrors: function(errorMap, errorList) {
                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);
                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });
                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");
                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
       },
    },
    mounted: function() {
      let vm = this;
      vm.form = document.forms.sheetEntryForm;
      vm.addFormValidations();
    }
}
</script>
