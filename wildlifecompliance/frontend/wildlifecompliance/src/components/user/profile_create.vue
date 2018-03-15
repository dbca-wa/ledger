<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Create Profile
                        <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div class="panel-body collapse in" :id="pBody">
                      <form class="form-horizontal" name="personal_form" method="post">
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
                          <div class="form-group">
                            <div class="col-sm-12">
                                <button v-if="!updatingPersonal" class="pull-right btn btn-primary" @click.prevent="updatePersonal()">Update</button>
                                <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Updating</button>
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
export default {
    name: 'CreateProfile',
    data () {
        let vm = this;
        return {
            pBody: 'pBody'+vm._uid,
            profile: {
                postal_address: {}
            },
            countries: [],
            loading: [],
            updatingPersonal: false,
            updatingAddress: false,
            role:null,
        }
    },
    watch: {
    },
    computed: {
    },
    methods: {
        updatePersonal: function() {
            let vm = this;
            vm.updatingPersonal = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.my_profiles,('/create_profile')),JSON.stringify(vm.profile),{
                emulateJSON:true
            }).then((response) => {
                console.log(response);
                vm.updatingPersonal = false;
                vm.profile = response.body;
                if (vm.profile.postal_address == null){ vm.profile.postal_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingPersonal = false;
            });
        },
        updateAddress: function() {
            let vm = this;
            vm.updatingAddress = true;
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.users,(vm.profile.id+'/update_address')),JSON.stringify(vm.profile.residential_address),{
                emulateJSON:true
            }).then((response) => {
                console.log(response);
                vm.updatingAddress = false;
                vm.profile = response.body;
                if (vm.profile.residential_address == null){ vm.profile.residential_address = {}; }
            }, (error) => {
                console.log(error);
                vm.updatingAddress = false;
            });
        },
        toggleSection: function (e) {
            let el = e.target;
            let chev = null;
            console.log(el);
            $(el).on('click', function (event) {
                chev = $(this);
                console.log(chev);
                $(chev).toggleClass('glyphicon-chevron-down glyphicon-chevron-up');
            })
        },
        fetchCountries:function (){
            let vm =this;
            vm.loading.push('fetching countries');
            vm.$http.get(api_endpoints.countries).then((response)=>{
                vm.countries = response.body;
                vm.loading.splice('fetching countries',1);
            },(response)=>{
                console.log(response);
                vm.loading.splice('fetching countries',1);
            });
        },
    },
    beforeRouteEnter: function(to,from,next){
    },
    mounted: function(){
        this.fetchCountries();
        this.personal_form = document.forms.personal_form;
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
            },100);
        }); 
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
</style>

