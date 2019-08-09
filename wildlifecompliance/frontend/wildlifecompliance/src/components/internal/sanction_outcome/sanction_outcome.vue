<template lang="html">
    <div class="container">
        <div class="row">
            <div class="col-md-3">
                <h3>Sanction Outcome: {{ sanction_outcome.lodgement_number }}</h3>
            </div>
        </div>
    </div>
</template>

<script>
import Vue from "vue";
import datatable from '@vue-utils/datatable.vue'
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import 'bootstrap/dist/css/bootstrap.css';
import SanctionOutcome from '../sanction_outcome/sanction_outcome_modal';
import filefield from '@/components/common/compliance_file.vue';

export default {
    name: 'SanctionOutcomeTableDash',
    data() {
        let vm = this;
        return {
            sanction_outcome: {
                lodgement_number:'',
                type: "",
                region_id: null,
                district_id: null,
                identifier: "",
                current_offence: {}, // Store an offence to be saved as an attribute of the sanction outcome
                // The offenders and the alleged_offences under this offence object are used
                // to construct a dropdown list for the offenders and the alleged offences datatable
                current_offender: {}, // Store an offender to be saved as an attribute of the sanction outcome
                issued_on_paper: false,
                paper_id: "",
                description: "",
                date_of_issue: null,
                time_of_issue: null,

                remediation_actions: []
            },
        }
    }
}
</script>

<style>

</style>