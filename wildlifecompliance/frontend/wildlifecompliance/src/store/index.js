import 'es6-promise/auto'
import Vue from 'vue'
import Vuex from 'vuex'
import { applicationStore } from './modules/application'
import { userStore } from './modules/user'

Vue.use(Vuex);

export default new Vuex.Store({
	state: {},
	mutations: {},
	getters: {},
	modules: {
		appStore: applicationStore,
		userStore: userStore
	}
})
