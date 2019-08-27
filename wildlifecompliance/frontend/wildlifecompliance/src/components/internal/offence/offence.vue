<template lang="html">
    <div class="container">
        <div class="row">
            <div class="col-md-3">
                <h3>Offence: {{ displayLodgementNumber }}</h3>
            </div>
        </div>
    </div>
</template>

<script>
import Vue from "vue";
import FormSection from "@/components/forms/section_toggle.vue";
import datatable from '@vue-utils/datatable.vue'
import utils from "@/components/external/utils";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import CommsLogs from "@common-components/comms_logs.vue";
import filefield from '@/components/common/compliance_file.vue';
import OffenceWorkflow from './offence_workflow';
import 'bootstrap/dist/css/bootstrap.css';

export default {
    name: 'ViewOffence',
    data() {
        let vm = this;
        vm.STATUS_DRAFT = 'draft';

        return {
            workflow_type :'',
            workflowBindId :'',
            soTab: 'soTab' + this._uid,
            deTab: 'deTab' + this._uid,
            reTab: 'reTab' + this._uid,
            comms_url: helpers.add_endpoint_json(
                api_endpoints.offence,
                this.$route.params.offence_id + "/comms_log"
            ),
            comms_add_url: helpers.add_endpoint_json(
                api_endpoints.offence,
                this.$route.params.offence_id + "/add_comms_log"
            ),
            logs_url: helpers.add_endpoint_json(
                api_endpoints.offence,
                this.$route.params.offence_id + "/action_log"
            ),
        }
    },
    components: {
        FormSection,
        OffenceWorkflow,
        CommsLogs,
    },
    created: async function() {
        if (this.$route.params.offence_id) {
            await this.loadOffence({ offence_id: this.$route.params.offence_id });
        }
    },
    mounted: function() {
        console.log('mounted');
    },
    computed: {
        ...mapGetters('offenceStore', {
            offence: "offence",
        }),
        displayLodgementNumber: function() {
            let ret = '';
            if (this.offence){
                ret = this.offence.lodgement_number;
            }
            return ret;
        },
    },
    methods: {
        ...mapActions('offenceStore', {
            loadOffence: 'loadOffence',
        }),
    }
}
</script>

<style>

</style>
