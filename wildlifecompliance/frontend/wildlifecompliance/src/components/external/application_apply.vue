<template lang="html">
    <div class="container" v-if="application">
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
                                <div class="row" v-if="behalf_of_org">
                                    <label class="col-sm-8">You have selected to apply on behalf of
                                        <span v-if="behalf_of_org">{{ behalf_of_org_details.name }} ({{ behalf_of_org_details.abn }}).</span>
                                    </label>
                                </div>
                                <div class="row">
                                    <label class="col-sm-4">Do you want to:</label>
                                </div>
                                <div class="radio">
                                    <label>
                                      <input type="radio" name="select_licence" v-model="licence_select" value="new_licence" > apply for a new licence?
                                    </label>
                                </div>
                                <div class="radio">
                                    <label>
                                      <input type="radio" name="select_licence" v-model="licence_select" value="new_activity"> apply for a new licensed activity on your licence?
                                    </label>
                                </div>
                                <div class="radio">
                                     <label>
                                      <input type="radio" name="select_licence" v-model="licence_select" value="amend_activity"> amend one or more licensed activities on your licence?
                                    </label>
                                </div>
                                <div class="radio">
                                    <label>
                                      <input type="radio" name="select_licence" v-model="licence_select" value="renew_activity"> renew one or more licensed activities on your licence?
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
        behalf_of_org : this.$route.params.org_select,
        behalf_of_org_details : {},
        behalf_of_proxy : this.$route.params.proxy_select,
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
  },
  methods: {
    submit: function() {
        this.$router.push({
            name: "apply_application_licence",
            params: {
                licence_select: this.licence_select,
                org_select: this.behalf_of_org
            }
        });
    },
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_application;
  },
  beforeRouteEnter: function(to, from, next) {
    next(vm => {
        const initialisers = [
            utils.fetchCurrentUser(),
            utils.fetchCurrentActiveLicenceApplication({
                    "proxy_id": vm.behalf_of_proxy,
                    "organisation_id": vm.behalf_of_org,
                }),
            vm.behalf_of_org ? utils.fetchOrganisation(vm.behalf_of_org) : '',
        ]
        Promise.all(initialisers).then(data => {
            vm.current_user = data[0];
            if(data[1].application == null) {
                return vm.$router.push({
                    name: "apply_application_licence",
                    params: {
                        licence_select: 'new_licence',
                        org_select: vm.behalf_of_org
                    }
                });
            }
            vm.application = data[1].application;
            vm.behalf_of_org_details = data[2];
        })
    })
  }
}
</script>

<style lang="css">
</style>
