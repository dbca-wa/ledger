<template>
<div class="container" id="internalReturn">
    <Returns v-if="isReturnsLoaded">
      <div class="col-md-1" />
      <div class="col-md-8">
      <template>
        <div class="panel panel-default">

                            <div class="col-sm-12">
                                <form class="form-horizontal" name="return_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Condition</label>
                                        <div class="col-sm-6">
                                            {{returns.condition}}
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Details</label>
                                        <div class="col-sm-6">
                                            <textarea disabled class="form-control" name="details" placeholder="" v-model="returns.text"></textarea>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Documents</label>
                                        <div class="col-sm-6">
                                            <div class="row" v-for="d in returns.documents">
                                                    <a :href="d[1]" target="_blank" class="control-label pull-left">{{d[0]}}</a>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>


        <template/>

        <div class="row" style="margin-bottom:50px;">
            <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                <div class="navbar-inner">
                    <div class="container">
                        <p class="pull-right" style="margin-top:5px;">
                             <button style="width:150px;" class="btn btn-primary btn-md" v-if="isWithCurator" >Save</button>
                        </p>
                    </div>
                </div>
            </div>
        </div>
      </div>
      </template>
      </div>
    </Returns>
</div>
</template>
<script>
//import $ from 'jquery'
import Returns from '../../returns_form.vue'
import { mapActions, mapGetters } from 'vuex'
import Vue from 'vue'
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-components/comms_logs.vue'
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'internal-returns',
  filters: {
    formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
    }
  },
  data() {
    let vm = this;
    return {
        // TODO: check if still required.
        assignTo: false,
        loading: [],
        isLoading: false,
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        members: [],

        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.returns,vm.$route.params.return_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.returns,vm.$route.params.return_id+'/comms_log'),
        comms_add_url: helpers.add_endpoint_json(api_endpoints.returns,vm.$route.params.return_id+'/add_comms_log'),

    }
  },
  components: {
    Returns,
    CommsLogs,
  },
  methods: {
    ...mapActions({
      load: 'loadReturns',
    }),
    ...mapActions([
        'setReturns',
        'setReturnsTab',
        'setReturnsAccess',
    ]),
    save: function(e) {
      console.log('ENTERED Save')
      let vm = this;
      let data = new FormData()
    },

  },
  computed: {
     ...mapGetters([
        'isReturnsLoaded',
        'returns',
    ]),
    isWithCurator: function() {
        return true;
    },
  },
  beforeRouteEnter: function(to, from, next){
    next(vm => {
       // FIXME: permission access from store.
       vm.setReturnsAccess( {'access': true } )

       vm.load({ url: `/api/returns/${to.params.return_id}.json` }).then(() => {
            console.log(vm.returns)

       });
    });
  },
}

</script>
