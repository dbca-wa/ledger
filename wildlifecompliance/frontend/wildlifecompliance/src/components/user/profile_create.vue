<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Create Profile
                    </h3>
                  </div>
                    <div class="panel-body collapse in" :id="pBody">
                      <form class="form-horizontal" name="profile_form" method="post">
                          <div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Profile Name</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="name" placeholder="" v-model="profile.name">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Email</label>
                            <div class="col-sm-6">
                                <input type="email" class="form-control" name="email" placeholder="" v-model="profile.email">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Institution</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="institution" placeholder="" v-model="profile.institution">
                            </div>
                          </div>
                          </div>
                          <div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Line 1</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="line1" placeholder="" v-model="profile.postal_address.line1">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Line 2</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="line2" placeholder="" v-model="profile.postal_address.line2">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Line 3</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="line3" placeholder="" v-model="profile.postal_address.line3">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Suburb/Town (Locality)</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="locality" placeholder="" v-model="profile.postal_address.locality">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >State</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="state" placeholder="" v-model="profile.postal_address.state">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Country</label>
                            <div class="col-sm-4">
                                <select class="form-control" name="country" placeholder="" v-model="profile.postal_address.country">
                                    <option v-for="c in countries" :value="c.alpha2Code">{{ c.name }}</option>
                                </select>
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Postcode</label>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="postcode" placeholder="" v-model="profile.postal_address.postcode">
                            </div>
                          </div>
                          </div>
                          <div class="form-group">
                            <div class="col-sm-12">
                                <button v-if="!creatingProfile" class="pull-right btn btn-primary" @click.prevent="createProfile()">Create</button>
                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Creating</button>
                            </div>
                          </div>
                       </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
import Vue from 'vue'
import $ from 'jquery'
import { api_endpoints, helpers } from '@/utils/hooks'
import utils from '@/components/internal/utils'
export default {
    name: 'CreateProfile',
    data () {
        let vm = this;
        return {
            pBody: 'pBody'+vm._uid,
            current_user:{},
            profile: {
                postal_address: {}
            },
            countries: [],
            loading: [],
            creatingProfile: false,
            role:null,
        }
    },
    watch: {
    },
    computed: {
    },
    methods: {
        createProfile: function() {
            let vm = this;
            vm.creatingProfile = true;
            vm.profile.user = vm.current_user.id;
            vm.profile.auth_identity = true;
            let params = '?email=' + encodeURIComponent(vm.profile.email) + '&exclude_user=' + vm.current_user.id;
            vm.$http.get(helpers.add_endpoint_join(api_endpoints.emailidentities,params),JSON.stringify(vm.profile),{
                    emulateJSON:true
                }).then((response) => {
                    console.log(response);
                    if (response.body.length > 0) {
                        vm.creatingProfile = false;
                        swal({
                            title: 'Create Profile',
                            html: 'This email address is already associated with an existing account or profile.',
                            type: 'error'
                        })
                        return;
                    }
                    vm.$http.post(api_endpoints.my_profiles + '/',JSON.stringify(vm.profile),{
                        emulateJSON:true
                    }).then((response) => {
                        vm.creatingProfile = false;
                        vm.profile = response.body;
                        if (vm.profile.postal_address == null){ vm.profile.postal_address = {}; }
                        swal({
                            title: 'Create Profile',
                            html: 'Your profile has been successfully created.<br/><br/>' + vm.profile.name + '<br/>' + vm.profile.email,
                            type: 'success',
                            onClose: vm.$router.push('/profiles')
                        })
                    }, (error) => {
                        vm.creatingProfile = false;
                        let error_msg = '<br/>';
                        for (var key in error.body) {
                            if (key === 'postal_address'){
                                for (var pkey in error.body[key]) {
                                    error_msg += pkey + ': ' + error.body[key][pkey] + '<br/>';
                                }
                            } else {
                                error_msg += key + ': ' + error.body[key] + '<br/>';
                            }
                        }
                        swal({
                            title: 'Create Profile',
                            html: 'There was an error creating the profile.<br/>' + error_msg,
                            type: 'error'
                        })
                    });
                }, (error) => {
                    vm.creatingProfile = false;
                    swal({
                        title: 'Create Profile',
                        html: 'There was an error creating the profile.',
                        type: 'error'
                    })
                });
        },
    },
    beforeRouteEnter: function(to, from, next){
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchCurrentUser(),
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.countries = data[0];
                vm.current_user = data[1];
            });
        });
    }
}
</script>
