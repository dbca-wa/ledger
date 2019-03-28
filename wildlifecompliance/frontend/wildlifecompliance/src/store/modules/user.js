export const userStore = {
    state: {
    },
    getters: {
        hasRole: (state, getters, rootState, rootGetters) => (role, activity_id) => {
            return rootGetters.application.user_roles.find(
                role_record => role_record.role == role && (!activity_id || activity_id == role_record.activity_id)
            );
        },
        visibleConditionsFor: (state, getters, rootState, rootGetters) => (for_role, processing_status, tab_id) => {
            return rootGetters.licence_type_data.activity.filter(activity =>
                activity.name && activity.processing_status.id == processing_status && getters.hasRole(for_role, activity.id) &&
                (!tab_id || tab_id == activity.id)
            );
        },
        licenceActivities: (state, getters, rootState, rootGetters) => (activity_status, for_user_role) => {
            return rootGetters.licence_type_data.activity.filter(
                activity => (activity_status.constructor === Array ? activity_status : [activity_status]).includes(activity.processing_status.id)
                    && activity.name && getters.hasRole(for_user_role, activity.id)
            )
        },
    },
}
