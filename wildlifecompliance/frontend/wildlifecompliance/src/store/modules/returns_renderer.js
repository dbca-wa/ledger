import Vue from 'vue';
import {
    UPDATE_RETURNS_TRANSFER_SPECIES,
    UPDATE_RETURNS_TABS,
    UPDATE_RETURNS_SELECTED_SPECIES,
    UPDATE_RETURNS_SPECIES,
    UPDATE_RETURNS_EXTERNAL,
    UPDATE_SELECTED_TAB_ID,
} from '@/store/mutation-types';

export const returnsRendererStore = {
    state: {
        tabs: [],
        external_user: false,
        selected_returns_tab_id: 0,
        species: {},
        selected_species: {},
        transfer_species: {},
    },
    getters: {
        returns_tabs: state => state.tabs,
        selected_returns_tab_id: state => state.selected_returns_tab_id,
        species_list: state => state.species,
        returns_access: state => state.access,
        species_cache: state => state.selected_species,
        is_external: state => state.external_user,
        species_transfer: state => state.transfer_species,
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
        [UPDATE_RETURNS_EXTERNAL] (state, external) {
            Vue.set(state, 'external_user', external);
        },
        [UPDATE_RETURNS_SELECTED_SPECIES] (state, selected_species) {
            Vue.set(state, 'selected_species', selected_species);
        },
        [UPDATE_RETURNS_TRANSFER_SPECIES] (state, transfer_species) {
            Vue.set(state, 'transfer_species', transfer_species);
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
        setReturnsExternal({ commit }, { external }) {
            commit(UPDATE_RETURNS_EXTERNAL, external);
        },
        setSpeciesCache({ commit }, { species_cache }) {
            commit(UPDATE_RETURNS_SELECTED_SPECIES, species_cache);
        },
        setSpeciesTransfer({ commit }, { species_transfer }) {
            commit(UPDATE_RETURNS_TRANSFER_SPECIES, species_transfer);
        },
    }
}
