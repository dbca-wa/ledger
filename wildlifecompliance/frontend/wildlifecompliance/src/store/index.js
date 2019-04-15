import 'es6-promise/auto';
import Vue from 'vue';
import Vuex from 'vuex';
import { applicationStore } from './modules/application';
import { userStore } from './modules/user';
import { rendererStore } from './modules/renderer';
import { returnsStore } from './modules/returns';
import { returnsRendererStore } from './modules/returns_renderer';

Vue.use(Vuex);

export default new Vuex.Store({
	state: {},
	mutations: {},
	getters: {},
	modules: {
		appStore: applicationStore,
		userStore: userStore,
		rendererStore: rendererStore,
    returnsStore: returnsStore,
    returnsRendererStore: returnsRendererStore,
	}
})
