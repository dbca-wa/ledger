import 'es6-promise/auto';
import Vue from 'vue';
import Vuex from 'vuex';
import {
	applicationStore
} from './modules/application';
import {
	userStore
} from './modules/user';
import {
	rendererStore
} from './modules/renderer';
import {
	returnsStore
} from './modules/returns';
import {
	returnsRendererStore
} from './modules/returns_renderer';
import {
	callemailStore
} from './modules/call_email';
import {
	offenceStore
} from './modules/offence';
import {
	inspectionStore
} from './modules/inspection';

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
		callemailStore: callemailStore,
		offenceStore: offenceStore,
		inspectionStore: inspectionStore,
	}
});