<template>
<form method="POST" name="external_returns_form" enctype="multipart/form-data">
<div class="container" id="externalReturn">
    <Returns v-if="isReturnsLoaded" >
        <div class='col-md-3'/>
        <div class='col-md-9' >

            <ReturnSheet v-if="returns.lodgement_date==null && returns.format==='sheet'"></ReturnSheet>
            <ReturnQuestion v-if="returns.lodgement_date==null && returns.format==='question'"></ReturnQuestion>
            <ReturnData v-if="returns.lodgement_date==null && returns.format==='data'"></ReturnData>
            <ReturnSubmit v-if="returns.lodgement_date!=null"></ReturnSubmit>

            <!-- End template for Return Tab -->

            <div class="row" style="margin-bottom:50px;">
                <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                    <div class="navbar-inner">
                        <div class="container">
                            <p class="pull-right" style="margin-top:5px;">
                                <button style="width:150px;" class="btn btn-primary btn-md" name="save_exit">Save and Exit</button>
                                <button style="width:150px;" class="btn btn-primary btn-md" @click.prevent="save()" name="save_continue">Save and Continue</button>
                                <button style="width:150px;" class="btn btn-primary btn-md" v-if="isSubmittable" @click.prevent="submit()" name="submit">Submit</button>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </Returns>
</div>
</form>
</template>

<script>
import Vue from 'vue'
import Returns from '../../returns_form.vue'
import ReturnSheet from './enter_return_sheet.vue'
import ReturnQuestion from './enter_return_question.vue'
import ReturnData from './enter_return.vue'
import ReturnSubmit from './return_submit.vue'
import { mapActions, mapGetters } from 'vuex'
import CommsLogs from '@common-components/comms_logs.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'externalReturn',
  data() {
    return {
      pdBody: 'pdBody' + self._uid,
    }
  },
  components: {
    Returns,
    ReturnSheet,
    ReturnQuestion,
    ReturnData,
    ReturnSubmit,
  },
  computed: {
    ...mapGetters([
        'isReturnsLoaded',
        'returns',
        'species_list',
        'species_cache',
        'species_transfer',
    ]),
    isSubmittable() {
      return this.returns.format !== 'sheet' && this.returns.lodgement_date == null
    },
    requiresCheckout: function() {
      return this.returns.return_fee > 0 && [
        'draft', 'awaiting_payment'
      ]
    },
  },
  methods: {
    ...mapActions({
      load: 'loadReturns',
    }),
    ...mapActions([
        'setReturns',
        'setReturnsExternal',
    ]),
    save: function(e) {
      const self = this;
      self.form=document.forms.external_returns_form;
      var data = new FormData(self.form);
      // cache only used in Returns sheets
      for (const speciesID in self.species_cache) { // Running Sheet Cache
        let speciesJSON = []
        for (let i=0;i<self.species_cache[speciesID].length;i++){
          speciesJSON[i] = JSON.stringify(self.species_cache[speciesID][i])
        }
        data.append(speciesID, speciesJSON)
      };
      var speciesJSON = []
      let cnt = 0;
      for (const speciesID in self.species_transfer) { // Running Sheet Transfers
        Object.keys(self.species_transfer[speciesID]).forEach(function(key) {
          speciesJSON[cnt] = JSON.stringify(self.species_transfer[speciesID][key])
          cnt++;
        });
        data.append('transfer', speciesJSON)
      }
      self.$http.post(helpers.add_endpoint_json(api_endpoints.returns,self.returns.id+'/save'),data,{
                      emulateJSON:true,
                    }).then((response)=>{
                       let species_id = self.returns.sheet_species;
                       self.setReturns(response.body);
                       self.returns.sheet_species = species_id;
                       swal('Save',
                            'Return Details Saved',
                            'success'
                       );
                    },(error)=>{
                        console.log(error);
      });

    },
    submit: function(e) {
      const self = this;
      self.form=document.forms.external_returns_form;
      self.$http.post(helpers.add_endpoint_json(api_endpoints.returns,self.returns.id+'/submit'),{
                      emulateJSON:true,
                    }).then((response)=>{
                       let species_id = self.returns.sheet_species;
                       self.setReturns(response.body);
                       self.returns.sheet_species = species_id;
                       swal('Save',
                            'Return Submitted',
                            'success'
                       );
                    },(error)=>{
                        console.log(error);
      });

    }
  },
  beforeRouteEnter: function(to, from, next) {
     next(vm => {
       vm.load({ url: `/api/returns/${to.params.return_id}.json` });
       vm.setReturnsExternal({'external': true});
     });  // User and Return Store loaded.
  },
}
</script>
