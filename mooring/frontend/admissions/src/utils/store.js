import Vuex from 'vuex'
import Vue from 'vue'

Vue.use(Vuex)
import {
    $,
    api_endpoints
} from '../hooks'
var store = new Vuex.Store({
    state: {
        alert:{
            visible:false,
            type:"danger",
            message: ""
        },
        regions:[],
        parks:[],
        districts:[],
        mooring_groups: [],
        campgrounds:[],
        campsite_classes:[],
        show_loader: false,
        app_loader_text: ''
    },
    mutations: {
        SETALERT(state, a) {
            state.alert = a;
        },
        SETREGIONS(state, regions) {
            state.regions = regions;
        },
        SETPARKS(state, parks) {
            state.parks = parks;
        },
        SETDISTRICTS(state, districts) {
            state.districts = districts;
        },
        SETCAMPGROUNDS(state,campgrounds){
            state.campgrounds = campgrounds;
        },
        SETCAMPSITECLASSES(state,campsite_classes){
            state.campsite_classes = campsite_classes;
        },
        SET_LOADER_STATE(state,val){
            state.show_loader = val;
            !val ? state.app_loader_text = '': '';
        },
        SET_LOADER_TEXT(state,val){
            state.app_loader_text = val;
        },
        SETMOORINGGROUP(state, mooring_groups) {
            state.mooring_groups = mooring_groups;
        },

    },
    actions: {
        updateAlert(context,payload) {
            context.commit('SETALERT',payload);
        },
        fetchRegions(context) {
            $.get(api_endpoints.regions,function(data){
                context.commit('SETREGIONS',data);
            });
        },
        fetchParks(context) {
            $.get(api_endpoints.parks,function(data){
                context.commit('SETPARKS',data);
            });
        },
        fetchMooringGroups(context) {
            $.get(api_endpoints.mooring_groups,function(data){
                context.commit('SETMOORINGGROUP',data);
            });
        },
        fetchDistricts(context) {
            $.get(api_endpoints.districts,function(data){
                context.commit('SETDISTRICTS',data);
            });
        },
        fetchCampgrounds(context){
            return new Promise((resolve,reject) => {
                Vue.http.get(api_endpoints.campgrounds).then((response) => {
                    context.commit('SETCAMPGROUNDS',response.body);
                    resolve(response.body);
                }, (error) => {
                    reject(error);
                });
            });
        },
        fetchCampsiteClasses(context){
            $.get(api_endpoints.campsite_classes,function(data){
                context.commit('SETCAMPSITECLASSES',data);
            });
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
        },
        regions: state => {
            return state.regions;
        },
        parks: state => {
            return state.parks;
        },
        districts: state => {
            return state.districts;
        },
        campgrounds: state => {
            return state.campgrounds;
        },
        campsite_classes: state => {
            return state.campsite_classes;
        },
        app_loader_state: (state) => {
            return state.show_loader;
        },
        app_loader_text: (state) => {
            return state.app_loader_text;
        }
    }
});

export default store;
