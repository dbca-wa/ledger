import Vue from 'vue'

import {
    $,
    awesomplete,
    Moment,
    api_endpoints,
    validate,
    formValidate,
    helpers,
    store
} from "../../hooks.js";
export default {
    fetchBooking(id){
        return new Promise((resolve,reject) => {
            Vue.http.get(api_endpoints.booking(id)).then((response) => {
                resolve(response);
            }, (error) => {
                reject(error);
            });
        });
    }
}
