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
                                        <input type="radio"  name="behalf_of_org" v-model="org_applicant" value=""> On behalf of yourself
                                        </label>
                                    </div>
                                    <div v-for="org in current_user.wildlifecompliance_organisations" class="radio">
                                        <label v-if ="!org.is_consultant">
                                          <input type="radio"  name="behalf_of_org" v-model="org_applicant"  :value="org.id"> On behalf of {{org.name}}
                                        </label>
                                        <label v-if ="org.is_consultant">
                                          <input  type="radio"  name="behalf_of_org" v-model="org_applicant"  :value="org.id" > On behalf of {{org.name}} (as a Consultant)
                                        </label>
                                    </div>
                            </div>
                           
                            <div class="col-sm-12">
                                <button :disabled="org_applicant === null" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
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
import { mapActions, mapGetters } from 'vuex'
import utils from './utils'
export default {
  data: function() {
    let vm = this;
    return {
        "application": null,
        agent: {},
        org_applicant: null,
        organisations:null,

        current_user: {
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
        if (vm.org_applicant && !isNaN(vm.org_applicant)) {
            return vm.current_user.wildlifecompliance_organisations.find(org => parseInt(org.id) === parseInt(vm.org_applicant)).name;
        }
        return '';
    }
  },
  methods: {
    ...mapActions([
        'setApplyOrgId',
        'setApplicationWorkflowState',
    ]),
    submit: function() {
        let vm = this;
        vm.setApplyOrgId({id: vm.org_applicant});
        vm.setApplicationWorkflowState({bool: true});
        vm.$router.push({
            name:"apply_application",
        });
    },
    
    fetchOrgContact:function (){
            let vm =this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,'get_pending_requests')).then((response)=>{
                vm.orgRequest_pending = response.body;
                vm.loading.splice('fetching pending organisation requests',1);
            },(response)=>{
                vm.loading.splice('fetching pending organisation requests',1);
            });
        },
  },
   
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_application;
  },
  beforeRouteEnter:function(to,from,next){
        let initialisers = [
            utils.fetchCurrentUser(),
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.current_user = data[0];
            });
        });
    },
}
</script>

<style lang="css">
</style>
