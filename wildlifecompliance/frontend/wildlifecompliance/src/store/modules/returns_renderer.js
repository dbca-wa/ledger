import Vue from 'vue';
import {
    UPDATE_RETURNS_TABS,
    UPDATE_RETURNS_SPECIES,
    UPDATE_SELECTED_TAB_ID,
} from '@/store/mutation-types';

export const returnsRendererStore = {
    state: {
        tabs: [],
        access: false,
        selected_returns_tab_id: 0,
        species: {},
    },
    getters: {
        returns_tabs: state => state.tabs,
        selected_returns_tab_id: state => state.selected_returns_tab_id,
        species_list: state => state.species,
        returns_access: state => state.access,

        isInternal: (state, getters) => {
            return getters.returns_access;
        },
        isExternal: (state, getters) => {
            return !getters.returns_access;
        },
    },
    mutations: {
        [UPDATE_RETURNS_TABS] (state, tabs) {
            Vue.set(state, 'tabs', tabs);
        },
        [UPDATE_SELECTED_TAB_ID] (state, tab_id) {
            state.selected_returns_tab_id = tab_id;
        },
        [UPDATE_RETURNS_SPECIES] (state, species) {
            Vue.set(state, 'species', species);
        },
        ['UPDATE_RETURNS_ACCESS'] (state, access) {
            Vue.set(state, 'access', access);
        },
    },
    actions: {
        setReturnsTabs({ commit }, { tabs }) {
            commit(UPDATE_RETURNS_TABS, tabs);
        },
        setReturnsSpecies({ commit }, { species }) {
            console.log('settingReturnsSpecies')
            let fullSpeciesList = {'S000001': 'Western Grey Kangaroo', 'S000002': 'Western Red Kangaroo',
                               'S000003': 'Blue Banded Bee', 'S000004': 'Orange-Browed Resin Bee'}
            commit(UPDATE_RETURNS_SPECIES, fullSpeciesList);
        },
        // FIXME: returns permissions.
        setReturnsAccess({ commit }, { access }) {
            commit('UPDATE_RETURNS_ACCESS', access);
        },
    }
}
