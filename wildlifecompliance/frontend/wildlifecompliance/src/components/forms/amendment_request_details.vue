<template lang="html">
    <div v-if="isApplicationLoaded && !application_readonly && isVisible">
        <div v-if="visibleRequests.length" class="row" style="color:red;">
            <div class="col-lg-12 pull-right">
                <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title" style="color:red;">An amendment has been requested for this Application
                        <a class="panelClicker" :href="'#pBody'" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="'pBody'">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                    </div>
                    <div class="panel-body collapse in" :id="'pBody'">
                    <div v-for="a in visibleRequests">
                        <p>Activity: {{a.licence_activity.name}}</p>
                        <p>Reason: {{a.reason.name}}</p>
                        <p>Details: <p v-for="t in splitText(a.text)">{{t}}</p></p>  
                    </div>
                </div>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
import Vue from 'vue'
import { mapActions, mapGetters } from 'vuex'
import { splitText } from "@/utils/helpers.js";

export default {
  name:'amendment-request-details',
  data: function() {
    return {
    }
  },
  props:{
      activity_id: {
          type: Number,
          required: true
      }
  },
  computed: {
    ...mapGetters([
        'application_readonly',
        'amendment_requests',
        'selected_activity_tab_id',
        'isApplicationLoaded',
    ]),
    isVisible: function() {
        return this.activity_id == this.selected_activity_tab_id;
    },
    visibleRequests: function() {
        return this.amendment_requests.filter(request => request.licence_activity.id == this.activity_id);
    }
  },
  methods: {
    splitText: splitText,
  },
}
</script>
