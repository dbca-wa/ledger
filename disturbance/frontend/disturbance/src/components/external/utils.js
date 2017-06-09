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
    fetchProposal: function(id){
        return new Promise ((resolve,reject) => {
            Vue.http.get(helpers.add_endpoint_json(api.proposals,id)).then((response) => {
                resolve(response.body);
            },
            (error) => {
                reject(error);
            });
        });
    }
}
