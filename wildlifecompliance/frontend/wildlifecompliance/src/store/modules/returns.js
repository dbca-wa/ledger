import Vue from 'vue';


export const returnsStore = {
    state: {
        returns: {},
    },
    getters: {
        return_id: state => state.returns.id,
        returns: state => state.returns,
        isReturnsLoaded: state => Object.keys(state.returns).length && state.returns.table != null,
    },
    mutations: {
        ['UPDATE_RETURNS'] (state, returns) {
            Vue.set(state, 'returns', {...returns});
        },
    },
    actions: {
        loadReturns({ dispatch, commit }, { url }) {
            return new Promise((resolve, reject) => {
                Vue.http.get(url).then(res => {
                    dispatch('setReturns', res.body);
                    resolve();
                },
                err => {
                    console.log(err);
                    reject();
                });
            })
        },
        setReturns({ dispatch, commit }, returns) {
            commit('UPDATE_RETURNS', returns);
        },
    }
}
