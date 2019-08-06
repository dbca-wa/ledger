<template>
<form method="POST" name="internal_returns_form" enctype="multipart/form-data">
<div class="container" id="internalReturn">
    <Returns v-if="isReturnsLoaded">
        <div class="col-md-3" />
        <div class="col-md-9">

        <template>
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Condition Details
                    <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                        <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                    </a>
                </h3>
            </div>
            <div class="panel-body panel-collapse in" :id="pdBody">
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
            </div>
        </div>
        </template>

        <div class="row" style="margin-bottom:50px;">
            <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                <div class="navbar-inner">
                    <div class="container">
                        <p class="pull-right" style="margin-top:5px;">
                            <button style="width:150px;" class="btn btn-primary btn-md" v-if="false" >Save</button>
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <ReturnSheet v-if="returns.format==='sheet'"></ReturnSheet>
        <ReturnQuestion v-if="returns.format==='question'"></ReturnQuestion>
        <ReturnData v-if="returns.format==='data'"></ReturnData>

        </div>
    </Returns>
</div>
</form>
</template>

<script>
import Vue from 'vue'
import { mapActions, mapGetters } from 'vuex'
import Returns from '../../returns_form.vue'
import ReturnQuestion from '../../external/returns/enter_return_question.vue'
import ReturnSheet from '../../external/returns/enter_return_sheet.vue'
import ReturnData from '../../external/returns/enter_return.vue'
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
        pdBody: 'pdBody' + vm._uid,

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
    ReturnQuestion,
    ReturnSheet,
    ReturnData,
  },
  methods: {
    ...mapActions({
      load: 'loadReturns',
    }),
    ...mapActions([
        'setReturns',
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
        'is_external',
    ]),
    isWithCurator: function() {
        return true;
    },
  },
  beforeRouteEnter: function(to, from, next){
     next(vm => {
       vm.load({ url: `/api/returns/${to.params.return_id}.json` });
     });  // Return Store loaded.
  },
}

</script>
