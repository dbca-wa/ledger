import Vue from 'vue';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
import moment from 'moment';

export const complianceRendererStore = {
    namespaced: true,
    state: {
    },
    getters: {
    },
    mutations: {
    },
    actions: {
        async createDocumentActionUrl({dispatch, rootState}) {
            let callEmail = await rootState.callemailStore.call_email;
            let inspection = await rootState.inspectionStore.inspection;
            if (callEmail && callEmail.id) {
                  return helpers.add_endpoint_join(
                      api_endpoints.call_email,
                      callEmail.id + "/process_document/"
                      )

            } else if (inspection && inspection.id) {
                return helpers.add_endpoint_join(
                api_endpoints.inspection,
                inspection.id + "/process_inspection_report_document/"
                )
            }
            console.log("missed");
        },
    },
};
