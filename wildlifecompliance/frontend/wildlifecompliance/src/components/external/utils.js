import Vue from 'vue'
import api from './api'
import {helpers} from '@/utils/hooks' 

export default {
    fetchProfile: function (){
        return new Promise ((resolve,reject) => {
            Vue.http.get(api.profile).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });

    },
    fetchApplication: function(id){
        return new Promise ((resolve,reject) => {
            Vue.http.get(helpers.add_endpoint_json(api.applications,id)).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    },
    fetchCountries: function (){
        return new Promise ((resolve,reject) => {
            Vue.http.get(api.countries).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });

    },
    fetchOrganisations: function(id){
        return new Promise ((resolve,reject) => {
            Vue.http.get(api.organisations).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    },
    fetchOrganisationPermissions: function(id){
        return new Promise ((resolve,reject) => {
            Vue.http.get(helpers.add_endpoint_json(api.my_organisations,id)).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    },
    fetchLicenceClasses: function(){
        return new Promise ((resolve,reject) => {
            Vue.http.get(api.licences_class).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    },
    fetchLicenceCurrentPurposes: function(){
        return new Promise ((resolve,reject) => {
            Vue.http.get(api.licence_current_purposes).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    },
    fetchOrganisation: function(id){
        return new Promise ((resolve,reject) => {
            Vue.http.get(helpers.add_endpoint_json(api.organisations,id)).then((response) => {
                resolve(response.body);
                console.log(response.body)
            },
            (error) => {
                reject(error);
            });
        });
    },
}
