<template lang="html">
    <div class="container" v-if="application">
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">New Application for
                            <span v-if="selected_apply_org_id">{{ selected_apply_org_id_details.name }} ({{ selected_apply_org_id_details.abn }})</span>
                            <span v-if="selected_apply_proxy_id">{{ selected_apply_proxy_id_details.first_name }} {{ selected_apply_proxy_id_details.last_name }} ({{ selected_apply_proxy_id_details.email }})</span>
                            <span v-if="!selected_apply_org_id && !selected_apply_proxy_id">yourself</span>
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
import { mapActions, mapGetters } from 'vuex'
import utils from './utils'
import internal_utils from '@/components/internal/utils'
export default {
  data: function() {
    let vm = this;
    return {
        "application": null,
        agent: {},
        selected_apply_org_id_details : {},
        selected_apply_proxy_id_details: {},
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
    ...mapGetters([
        'selected_apply_org_id',
        'selected_apply_proxy_id',
        'application_workflow_state',
    ]),
    isLoading: function() {
      return this.loading.length > 0
    },
  },
  methods: {
    ...mapActions([
        'setApplyLicenceSelect',
    ]),
    submit: function() {
        this.setApplyLicenceSelect({licence_select: this.licence_select});
        this.$router.push({
            name: "apply_application_licence",
        });
    },
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_application;
  },
  beforeRouteEnter: function(to, from, next) {
    next(vm => {
        // Sends the user back to the first application workflow screen if workflow state
        // was interrupted (e.g. lost from page refresh)
        if(!vm.application_workflow_state) {
            return vm.$router.push({
                name: "apply_application_organisation",
            });
        }
        const initialisers = [
            utils.fetchCurrentUser(),
            utils.fetchCurrentActiveLicenceApplication({
                    "proxy_id": vm.selected_apply_proxy_id,
                    "organisation_id": vm.selected_apply_org_id,
                }),
            vm.selected_apply_org_id ? utils.fetchOrganisation(vm.selected_apply_org_id) : '',
            vm.selected_apply_proxy_id ? internal_utils.fetchUser(vm.selected_apply_proxy_id) : '',
        ]
        Promise.all(initialisers).then(data => {
            vm.current_user = data[0];
            if(data[1].application == null) {
                vm.setApplyLicenceSelect({licence_select: 'new_licence'});
                // use $router.replace here because we want the back button to return to
                // apply_application_organisation if used on the apply_application_licence screen in this case
                return vm.$router.replace({
                    name: "apply_application_licence",
                });
            }
            vm.application = data[1].application;
            vm.selected_apply_org_id_details = data[2];
            vm.selected_apply_proxy_id_details = data[3];
        })
    })
  }
}
</script>

<style lang="css">
</style>
