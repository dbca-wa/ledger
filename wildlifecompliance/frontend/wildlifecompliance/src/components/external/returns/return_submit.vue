<template>
    <div class="panel panel-default">
        <div class="panel-heading" v-show="false">
            <h3 class="panel-title">Return
                <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                    <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
            </h3>
        </div>
        <div class="panel-body panel-collapse in" :id="pdBody">
            <div v-if="isReturnsLoaded" class="col-sm-offset-3 col-sm-6 borderDecoration">
                <strong>Your Return has been submitted successfully.</strong>
                <br/>
                <table>
                    <tr>
                        <td><strong>Reference number:&nbsp;</strong></td>
                        <td><strong>{{returns.lodgement_number}}</strong></td>
                    </tr>
                    <tr>
                        <td><strong>Lodgement date:</strong></td>
                        <td><strong> {{returns.lodgement_date|formatDate}}</strong></td>
                    </tr>
                    <tr>
                        <td><strong>Invoice:</strong></td>
                        <td>PDF</td>
                    </tr>
                </table>
                <a href="/" style="margin-top:15px;" class="btn btn-primary">Back to dashboard</a>
            </div>
            <div v-else class="col-sm-offset-3 col-sm-6 borderDecoration">
                <strong>Sorry it looks like there isn't any details currently in your session.</strong>
                <br /><a href="/" style="margin-top:15px;" class="btn btn-primary">Back to dashboard</a>
            </div>
        </div>
        <input type='hidden' name="table_name" :value="returns.table[0].name" />
    </div>
</template>

<script>
import Vue from 'vue'
import { mapActions, mapGetters } from 'vuex'
import CommsLogs from '@common-components/comms_logs.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'externalReturnQuestion',
  data() {
    let vm = this;
    return {
      pdBody: 'pdBody' + vm._uid,
    }
  },
  computed: {
    ...mapGetters([
        'isReturnsLoaded',
        'returns',
    ]),
  },
  methods: {
    ...mapActions({
      load: 'loadReturns',
    }),
    ...mapActions([
        'setReturns',
    ]),
  },
  filters:{
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY'): '';
        }
  },
}
</script>
