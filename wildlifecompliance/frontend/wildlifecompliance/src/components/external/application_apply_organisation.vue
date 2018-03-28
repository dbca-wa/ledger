<template lang="html" >
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Apply on behalf of
                            <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body collapse in" :id="pBody">
                        <form class="form-horizontal" name="personal_form" method="post">
                            <div class="col-sm-12">
                                <div class="form-group">
                                    <div class="radio">
                                        <label>
                                        <input type="radio"  name="behalf_of_org" v-model="behalf_of"  value="other"> On behalf of yourself
                                        </label>
                                    </div>
                                    <div v-for="org in profile.wildlifecompliance_organisations" class="radio">
                                        <label v-if ="!org.is_consultant">
                                          <input type="radio"  name="behalf_of_org" v-model="behalf_of"  :value="org.id"> On behalf of {{org.name}}
                                        </label>
                                        <label v-if ="org.is_consultant">
                                          <input  type="radio"  name="behalf_of_org" v-model="behalf_of"  :value="org.id" > On behalf of {{org.name}} (as a Consultant)
                                        </label>
                                    </div>
                                    
                                </div>
                            </div>
                           
                            <div class="col-sm-12">
                                <button :disabled="behalf_of == ''" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
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
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
import utils from './utils'
export default {
  data: function() {
    let vm = this;
    return {
        licence_select : this.$route.params.licence_select,
        "application": null,
        agent: {},
        behalf_of: '',
        organisations:null,

        profile: {
            wildlifecompliance_organisations: []
        },
        "loading": [],
        form: null,
        pBody: 'pBody' + vm._uid,
    }
  },
  components: {
  },
  computed: {
    isLoading: function() {
      return this.loading.length > 0
    },
    org: function() {
        let vm = this;
        console.log('from org function',vm.behalf_of)
        if (vm.behalf_of != '' || vm.behalf_of != 'other'){
            return vm.profile.wildlifecompliance_organisations.find(org => parseInt(org.id) === parseInt(vm.behalf_of)).name;
        }
        return '';
        
        
    }
  },
  methods: {
    submit: function() {
        let vm = this;
         vm.$router.push({
                      name:"apply_application_licence",
                      params:{licence_select:vm.licence_select,
                               org_select:vm.behalf_of }
                  });
        console.log('from apply organisation',vm.licence_select);
        console.log('from apply organisation',vm.behalf_of);
        console.log('From organisation submit',vm.behalf_of)
    },
    
    fetchOrgContact:function (){
            let vm =this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,'get_pending_requests')).then((response)=>{
                vm.orgRequest_pending = response.body;
                vm.loading.splice('fetching pending organisation requests ',1);
            },(response)=>{
                console.log(response);
                vm.loading.splice('fetching pending organisation requests',1);
            });
        },
  },
   
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_application;
    console.log(vm.licence_select);

  },
  beforeRouteEnter:function(to,from,next){
        let initialisers = [
            utils.fetchProfile(),
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.profile = data[0];
            });
        });
    },
}
</script>

<style lang="css">
</style>
