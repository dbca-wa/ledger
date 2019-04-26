<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">New Application
                            <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body collapse in" :id="pBody">
                        <form class="form-horizontal" name="orgForm" method="post">
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Do you want to:</label>
                                </div>
                                <div class="radio">
                                    <label>
                                      <input type="radio" name="select_licence" v-model="licence_select" value="New_licence" > apply for a new licence?
                                    </label>
                                </div>
                                <div class="radio">
                                    <label>
                                      <input type="radio" name="select_licence" v-model="licence_select" value="New_activity"> apply for a new licensed activity on your licence?
                                    </label>
                                </div>
                                <div class="radio">
                                     <label>
                                      <input type="radio" name="select_licence" v-model="licence_select" value="Amend_activity"> amend one or more licensed activities on your licence?
                                    </label>
                                </div>
                                <div class="radio">
                                    <label>
                                      <input type="radio" name="select_licence" v-model="licence_select" value="Renew_activity"> renew one or more licensed activities on your licence?
                                    </label>
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <button  @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
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
        "application": null,
        agent: {},
        behalf_of: '',
        current_user: {
            wildlifecompliance_organisations: []
        },
        licence_select:null,
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
    hasOrgs: function() {
        return this.current_user.wildlifecompliance_organisations && this.current_user.wildlifecompliance_organisations.length > 0 ? true: false;
    },
    org: function() {
        let vm = this;
        if (vm.behalf_of != '' || vm.behalf_of != 'other'){
            return vm.current_user.wildlifecompliance_organisations.find(org => parseInt(org.id) === parseInt(vm.behalf_of)).name;
        }
        return '';
    }
  },
  methods: {
    submit: function() {
        let vm = this;
        vm.$router.push({
            name: "apply_application_organisation",
            params: { licence_select:vm.licence_select }
        });
    },
    createApplication:function () {
        let vm = this;
        vm.$http.post('/api/application.json',{
            behalf_of: vm.behalf_of
        }).then(res => {
              vm.application = res.body;
              
          },
          err => {
            console.log(err);
          });
    }
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_application;
  },
  beforeRouteEnter: function(to, from, next) {
    let initialisers = [
        utils.fetchCurrentUser(),
        //utils.fetchApplication(to.params.application_id)
    ]
    next(vm => {
        Promise.all(initialisers).then(data => {
            vm.current_user = data[0];
            //vm.application = data[1];
        })
    })
  }
}
</script>

<style lang="css">
</style>
