<template lang="html">
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
                                    <div v-for="org in profile.disturbance_organisations" class="radio">
                                        <label>
                                          <input type="radio" name="behalf_of_org" v-model="behalf_of"  :value="org.id"> On behalf of {{org.name}}
                                        </label>
                                    </div>
                                    <div class="radio">
                                        <label class="radio-inline">
                                          <input type="radio" name="behalf_of_org" v-model="behalf_of"  value="other" > On behalf of an organisation (as an authorised agent)
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div v-if="behalf_of == 'other'" class="col-sm-12">
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label">Organisation</label>
                                        <input type="text" class="form-control" name="first_name" placeholder="" v-model="agent.organisation">
                                    </div>
                                    <div class="form-group col-sm-1"></div>
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >ABN / ACN</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.abn">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Organisation contact given name(s)</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.given_names">
                                    </div>
                                    <div class="form-group col-sm-1"></div>
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Orgnisation contact surname</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.surname">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Organisation contact email address</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.email">
                                    </div>
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <button :disabled="behalf_of == 'other' || behalf_of == ''" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
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
        "proposal": null,
        agent: {},
        behalf_of: '',
        profile: {
            disturbance_organisations: []
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
        if (vm.behalf_of != '' || vm.behalf_of != 'other'){
            return vm.profile.disturbance_organisations.find(org => parseInt(org.id) === parseInt(vm.behalf_of)).name;
        }
        return '';
    }
  },
  methods: {
    submit: function() {
        let vm = this;
        swal({
            title: "Create Proposal",
            text: "Are you sure you want to create a proposal on behalf of "+vm.org+" ?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        }).then(() => {
            vm.createProposal();
        },(error) => {
        });
    },
    createProposal:function () {
        let vm = this;
        vm.$http.post('/api/proposal.json',{
            behalf_of: vm.behalf_of
        }).then(res => {
              vm.proposal = res.body;
              vm.$router.push({
                  name:"draft_proposal",
                  params:{proposal_id:vm.proposal.id}
              });
          },
          err => {
            console.log(err);
          });
    }
  },
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_proposal;
  },
  beforeRouteEnter: function(to, from, next) {
    let initialisers = [
        utils.fetchProfile(),
        //utils.fetchProposal(to.params.proposal_id)
    ]
    next(vm => {
        Promise.all(initialisers).then(data => {
            vm.profile = data[0];
            //vm.proposal = data[1];
        })
    })
  }
}
</script>

<style lang="css">
</style>
