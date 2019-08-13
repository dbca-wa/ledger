<template>
    <div class="panel panel-default">
        <div class="panel-heading">
            <h3 class="panel-title">Return
                <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                    <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
            </h3>
        </div>
        <div class="panel-body panel-collapse in" :id="pdBody">
            <div class="col-sm-16">
                <div>
                    <div v-for="(item,index) in returns.table">
                        <renderer-block v-for="(question,key) in item.headers"
                              :component="question"
                              v-bind:key="`q_${key}`"
                        />
                    </div>
                </div>
                <!-- End of Question Return -->
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
}
</script>
