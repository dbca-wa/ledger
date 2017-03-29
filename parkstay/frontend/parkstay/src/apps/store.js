import Vuex from 'vuex'
import Vue from 'vue'

Vue.use(Vuex)
var store = new Vuex.Store({
    state: {
        alert:{
            visible:false,
            type:"danger",
            message: ""
        }
    },
    mutations: {
        SETALERT(state, a) {
            state.alert = a;
        },
    },
    actions: {
        updateAlert(context,payload) {
            context.commit('SETALERT',payload);
        }
    },
    getters:{
        showAlert: state => {
            return state.alert.visible;
        },
        alertType: state => {
            return state.alert.type;
        },
        alertMessage: (state) =>  {
            return state.alert.message;
        }
    }
});

export default store;
