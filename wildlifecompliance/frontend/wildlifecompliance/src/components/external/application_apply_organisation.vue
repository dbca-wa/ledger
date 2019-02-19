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
                                    <p><strong>Note: If you are applying for a Taking licence, it cannot be applied for on behalf of an organisation.</strong></p>
                                    <div class="radio">
                                        <label>
                                        <input type="radio"  name="behalf_of_org" v-model="yourself" value="yourself"> On behalf of yourself
                                        </label>
                                    </div>
                                    <div v-for="org in profile.wildlifecompliance_organisations" class="radio">
                                        <label v-if ="!org.is_consultant">
                                          <input type="radio"  name="behalf_of_org" v-model="org_applicant"  :value="org.id"> On behalf of {{org.name}}
                                        </label>
                                        <label v-if ="org.is_consultant">
                                          <input  type="radio"  name="behalf_of_org" v-model="org_applicant"  :value="org.id" > On behalf of {{org.name}} (as a Consultant)
                                        </label>
                                    </div>
                            </div>
                           
                            <div class="col-sm-12">
                                <button :disabled="org_applicant == '' && yourself == ''" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
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
        org_applicant: '',
        yourself: '',
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
        console.log('from org function',vm.org_applicant)
        if (vm.org_applicant != '' || vm.org_applicant != 'submitter'){
            return vm.profile.wildlifecompliance_organisations.find(org => parseInt(org.id) === parseInt(vm.org_applicant)).name;
        }
        return '';
        
        
    }
  },
  methods: {
    submit: function() {
        let vm = this;
        window.v_org_applicant = vm.org_applicant;
         vm.$router.push({
                      name:"apply_application_licence",
                      params:{
                        licence_select:vm.licence_select,
                        org_select:vm.org_applicant
                      }
                  });
        console.log('from organisation submit - licence_select: ',vm.licence_select);
        console.log('from organisation submit - org id: ',vm.org_applicant);
        console.log('From organisation submit - submitter id: ',vm.profile.id);
        console.log('org applicant - ', window.v_org_applicant);
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
