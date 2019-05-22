import Vue from 'vue';
import {
    UPDATE_RETURNS_TABS,
    UPDATE_RETURNS_SPECIES,
    UPDATE_SELECTED_TAB_ID,
    UPDATE_VISIBLE_COMPONENT,
} from '@/store/mutation-types';

export const returnsRendererStore = {
    state: {
        tabs: [],
        visible_components: [],
        selected_returns_tab_id: 0,
        species: {},
    },
    getters: {
        returns_tabs: state => state.tabs,
        selected_returns_tab_id: state => state.selected_returns_tab_id,
        isReturnComponentVisible: (state) => (key) => {
            return state.visible_components[key] ? true : false;
        },
        species_list: state => state.species,
    },
    mutations: {
        [UPDATE_RETURNS_TABS] (state, tabs) {
            Vue.set(state, 'tabs', tabs);
        },
        [UPDATE_SELECTED_TAB_ID] (state, tab_id) {
            state.selected_returns_tab_id = tab_id;
        },
        [UPDATE_VISIBLE_COMPONENT] (state, { key, value }) {
            Vue.set(state.visible_components, key, value);
        },
        [UPDATE_RETURNS_SPECIES] (state, species) {
            Vue.set(state, 'species', species);
        },
    },
    actions: {
        setReturnsTabs({ commit }, { tabs }) {
            commit(UPDATE_RETURNS_TABS, tabs);
        },
        toggleVisibleComponent({ commit, getters }, { component_id, visible }) {
            commit(UPDATE_VISIBLE_COMPONENT,
                {key: component_id, value: visible});
        },
        setReturnsSpecies({ commit }, { species }) {
            console.log('settingReturnsSpecies')
            let fullSpeciesList = {'S000001': 'Western Grey Kangaroo', 'S000002': 'Western Red Kangaroo',
                               'S000003': 'Blue Banded Bee', 'S000004': 'Orange-Browed Resin Bee'}
            commit(UPDATE_RETURNS_SPECIES, fullSpeciesList);
        },
    }
}
