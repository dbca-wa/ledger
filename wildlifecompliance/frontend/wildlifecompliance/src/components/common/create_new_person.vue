<template lang="html">
    <div :id="elementId">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Personal Details
                        <a class="panelClicker" :href="'#'+pdBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pdBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pdBody">
                    <div v-if="objectAlert" class="alert alert-danger">
                        <p>test alert</p>
                    </div>
                    <form class="form-horizontal" name="personal_form" method="post">
                        <div class="form-group" v-bind:class="{ 'has-error': errorGivenName }">
                            <label for="" class="col-sm-3 control-label">Given Name(s)</label>
                            <div class="col-sm-6">
                                <div v-if="email_user">
                                    <input type="text" class="form-control" name="first_name" placeholder="" v-model="email_user.first_name" v-bind:key="email_user.id">
                                </div>
                            </div>
                        </div>
                        <div class="form-group" v-bind:class="{ 'has-error': errorLastName }">
                            <label for="" class="col-sm-3 control-label">Last Name</label>
                            <div class="col-sm-6">
                                <div v-if="email_user">
                                    <input type="text" class="form-control" name="last_name" placeholder="" v-model="email_user.last_name" v-bind:key="email_user.id">
                                </div>
                            </div>
                        </div>
                        <div class="form-group" v-bind:class="{ 'has-error': errorDob }">
                            <label for="" class="col-sm-3 control-label" >Date of Birth</label>
                            <div class="col-sm-6">
                                <div v-if="email_user">
                                    <input type="date" class="form-control" name="dob" placeholder="" v-model="email_user.dob" v-bind:key="email_user.id">
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                <h3 class="panel-title">Address Details
                                    <a class="panelClicker" :href="'#'+adBody" data-toggle="collapse" expanded="false"  data-parent="#userInfo" :aria-controls="adBody">
                                        <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                    </a>
                                </h3>
                                </div>
                                <div v-if="loading.length == 0" class="panel-body collapse in" :id="adBody">
                                    <form class="form-horizontal" action="index.html" method="post">
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Street</label>
                                        <div class="col-sm-6">
                                            <div v-if="email_user"><div v-if="email_user.residential_address">
                                                <input type="text" class="form-control" name="street" placeholder="" v-model="email_user.residential_address.line1" v-bind:key="email_user.residential_address.id">
                                            </div></div>
                                        </div>
                                        </div>
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                        <div class="col-sm-6">
                                            <div v-if="email_user"><div v-if="email_user.residential_address">
                                                <input type="text" class="form-control" name="surburb" placeholder="" v-model="email_user.residential_address.locality" v-bind:key="email_user.residential_address.id">
                                            </div></div>
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">State</label>
                                        <div class="col-sm-2">
                                            <div v-if="email_user"><div v-if="email_user.residential_address">
                                                <input type="text" class="form-control" name="country" placeholder="" v-model="email_user.residential_address.state" v-bind:key="email_user.residential_address.id">
                                            </div></div>
                                        </div>
                                        <label for="" class="col-sm-2 control-label">Postcode</label>
                                        <div class="col-sm-2">
                                            <div v-if="email_user"><div v-if="email_user.residential_address">
                                                <input type="text" class="form-control" name="postcode" placeholder="" v-model="email_user.residential_address.postcode" v-bind:key="email_user.residential_address.id">
                                            </div></div>
                                        </div>
                                        </div>
                                        <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Country</label>
                                        <div class="col-sm-4">
                                            <div v-if="email_user"><div v-if="email_user.residential_address">
                                                <select class="form-control" name="country" v-model="email_user.residential_address.country" v-bind:key="email_user.residential_address.id">
                                                    <option v-for="c in countries" :value="c.alpha2Code">{{ c.name }}</option>
                                                </select>
                                            </div></div>
                                        </div>
                                        </div>
                                        <!-- <div class="form-group">
                                        <div class="col-sm-12">
                                            <button v-if="!updatingAddress" class="pull-right btn btn-primary" @click.prevent="updateAddress()">Update</button>
                                            <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
                                        </div>
                                        </div>  -->
                                    </form>
                                </div>
                            </div>



        </div>
    </div>
</template>

<script>
import $ from "jquery";
import { api_endpoints, helpers } from '@/utils/hooks'
import utils from '../internal/utils'
import "bootstrap/dist/css/bootstrap.css";

export default {
    name: "create-new-person",

    data: function(){
        let vm = this;

        return {
            mainElement: null,
            slideDownDuration: 500,
            slideUpDuration: 500,

            pdBody: 'pdBody'+vm._uid,
            adBody: 'adBody'+vm._uid,
            errorGivenName: false,
            errorLastName: false,
            errorDob: false,
            objectAlert: false,
            loading: [],
            countries: [],

            email_user : {
                first_name: '',
                last_name: '',
                dob: null,
                residential_address: {
                    line1: '',
                    locality: '',
                    state: 'WA',
                    postcode: '',
                    country: 'AU'
                },
                phone_number: '',
                mobile_number: '',
                email: '',
            }
        }
    },
    props: {
        elementId: {
            type: String,
            required: true,
        },
        display: {
            type: Boolean,
            required: true,
            default: false,
        }
    },
    watch: {
        display: {
            handler: function() {
                this.showHideElement();
            }
        }
    },
    methods: {
        loadCountries: function(){
            let vm = this;
            let initialisers = [
                utils.fetchCountries()
            ]
            Promise.all(initialisers).then(data => {
                vm.countries = data[0];
            });
        },
        saveData: function() {

        },
        showHideElement: function() {
            if(this.display) {
                this.mainElement.slideDown(this.slideDownDuration);
            } else {
                this.mainElement.slideUp(this.slideUpDuration);
            }
        }
    },
    mounted: function() {
        let vm = this;
        console.log('mounted');
        let elem = document.getElementById(vm.elementId);
        vm.mainElement = $(elem);
        vm.$nextTick(()=>{
            vm.showHideElement();
            vm.loadCountries();
        })
    }
}
</script>

<style>

</style>