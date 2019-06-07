<template>
<form method="POST" name="external_returns_form" enctype="multipart/form-data">
<div class="container" id="externalReturn">
    <Returns v-if="isReturnsLoaded" >
        <div class='col-md-1'/>
        <div class='col-md-8' >

            <ReturnSheet v-if="returns.format==='sheet'"></ReturnSheet>
            <ReturnQuestion v-if="returns.format==='question'"></ReturnQuestion>
            <ReturnData v-if="returns.format==='data'"></ReturnData>

            <!-- End template for Return Tab -->

            <div class="row" style="margin-bottom:50px;">
                <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                    <div class="navbar-inner">
                        <div class="container">
                            <p class="pull-right" style="margin-top:5px;">
                                <button style="width:150px;" class="btn btn-primary btn-md" name="save_exit">Save and Exit</button>
                                <button style="width:150px;" class="btn btn-primary btn-md" @click.prevent="save()" name="save_continue">Save and Continue</button>
                                <button style="width:150px;" class="btn btn-primary btn-md" name="draft">Submit</button>
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
    let vm = this;
    return {
      pdBody: 'pdBody' + vm._uid,
    }
  },
  components: {
    Returns,
    ReturnSheet,
    ReturnQuestion,
    ReturnData,
  },
  computed: {
    ...mapGetters([
        'isReturnsLoaded',
        'returns',
        'species_list',
        'species_cache',
        'species_transfer',
    ]),
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
      this.form=document.forms.external_returns_form;
      var data = new FormData(this.form);

      // cache only used in Returns sheets
      for (const speciesID in this.species_cache) {
        let speciesJSON = []
        for (let i=0;i<this.species_cache[speciesID].length;i++){
          speciesJSON[i] = JSON.stringify(this.species_cache[speciesID][i])
        }
        data.append(speciesID, speciesJSON)
      };
      this.$http.post(helpers.add_endpoint_json(api_endpoints.returns,this.returns.id+'/save'),data,{
                      emulateJSON:true,
                    }).then((response)=>{
                       let species_id = this.returns.sheet_species;
                       this.setReturns(response.body);
                       this.returns.sheet_species = species_id;
                       swal('Save',
                            'Return Details Saved',
                            'success'
                       );
                    },(error)=>{
                        console.log(error);
      });

    },

    submit: function(e) {  // TODO:
      this.form=document.forms.external_returns_form;
      var data = new FormData(this.form);
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
