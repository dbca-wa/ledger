import Vue from 'vue';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
import moment from 'moment';

export const inspectionStore = {
    namespaced: true,
    state: {
        inspection: {
            
        },
        
    },
    getters: {
        inspection: state => state.inspection,
        
    },
    mutations: {
        updateInspection(state, inspection) {
            Vue.set(state, 'inspection', {
                ...inspection
            });
            if (state.inspection.planned_for_date) {
                state.inspection.planned_for_date = moment(state.inspection.planned_for_date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            let inspectionReportDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.inspection,
                state.inspection.id + "/process_inspection_report_document/"
                )
            Vue.set(state.inspection, 'inspectionReportDocumentUrl', inspectionReportDocumentUrl); 
            let rendererDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.inspection,
                state.inspection.id + "/process_renderer_document/"
                )
            Vue.set(state.inspection, 'rendererDocumentUrl', rendererDocumentUrl); 
            let commsLogsDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.inspection,
                state.inspection.id + "/create_modal_process_comms_log_document/"
                )
            Vue.set(state.inspection, 'commsLogsDocumentUrl', commsLogsDocumentUrl); 
        },
        updatePlannedForTime(state, time) {
            Vue.set(state.inspection, 'planned_for_time', time);
        },
        updatePartyInspected(state, data) {
            if (data.data_type === 'individual') {
                Vue.set(state.inspection, 'individual_inspected_id', data.id);
                if (state.inspection.organisation_inspected_id) {
                    state.inspection.organisation_inspected_id = null;
                }
            }
            if (data.data_type === 'organisation') {
                Vue.set(state.inspection, 'organisation_inspected_id', data.id);
                if (state.inspection.individual_inspected_id) {
                    state.inspection.individual_inspected_id = null;
                }
            }
        },
        
    },
    actions: {
        async loadInspection({ dispatch, commit }, { inspection_id }) {
            console.log("loadInspection");
            try {
                const returnedInspection = await Vue.http.get(
                    helpers.add_endpoint_json(
                        api_endpoints.inspection, 
                        inspection_id)
                    );

                /* Set Inspection object */
                //await dispatch("setInspection", returnedInspection.body);
                commit("updateInspection", returnedInspection.body);

            } catch (err) {
                console.log(err);
            }
        },
        async modifyInspectionTeam({ dispatch, state}, { user_id, action }) {
            console.log("modifyInspectionTeam");
            try {
                const returnedInspection = await Vue.http.post(
                    helpers.add_endpoint_join(
                        api_endpoints.inspection,
                        state.inspection.id + '/modify_inspection_team/',
                    ),
                    { user_id, action }
                    );

                /* Set Inspection object */
                await dispatch("setInspection", returnedInspection.body);

            } catch (err) {
                console.log(err);
            }
        },
        
        async saveInspection({ dispatch, state }, { route, crud, internal }) {
            console.log(crud)
            let inspectionId = null;
            let savedInspection = null;
            try {
                let fetchUrl = null;
                if (crud === 'create' || crud === 'duplicate') {
                    fetchUrl = api_endpoints.inspection;
                } else {
                    fetchUrl = helpers.add_endpoint_join(
                        api_endpoints.inspection, 
                        state.inspection.id + "/inspection_save/"
                        )
                }

                let payload = {};
                Object.assign(payload, state.inspection);
                if (payload.planned_for_date) {
                    payload.planned_for_date = moment(payload.planned_for_date, 'DD/MM/YYYY').format('YYYY-MM-DD');
                } else if (payload.planned_for_date === '') {
                    payload.planned_for_date = null;
                }
                if (crud == 'duplicate') {
                    payload.id = null;
                    payload.location_id = null;
                    if (payload.location) {
                        payload.location.id = null;
                    }
                }

                savedInspection = await Vue.http.post(fetchUrl, payload);
                await dispatch("setInspection", savedInspection.body);
                inspectionId = savedInspection.body.id;

            } catch (err) {
                console.log(err);
                if (internal) {
                    // return "There was an error saving the record";
                    return err;
                } else {
                    await swal("Error", "There was an error saving the record", "error");
                }
                return window.location.href = "/internal/inspection/";
            }
            if (crud === 'duplicate') {
                return window.location.href = "/internal/inspection/" + inspectionId;
            }
            else if (crud !== 'create') {
                if (!internal) {
                    await swal("Saved", "The record has been saved", "success");
                } else {
                    return savedInspection;
                }
            }
            if (route) {
                return window.location.href = "/internal/inspection/";
            } else {
                return inspectionId;
            }
        },
        
        setInspection({ commit, }, inspection) {
            commit("updateInspection", inspection);
        },
        setPlannedForTime({ commit }, time ) {
            commit("updatePlannedForTime", time);
        },
        setPartyInspected({ commit, }, data) {
            commit("updatePartyInspected", data);
        },
    },
};
