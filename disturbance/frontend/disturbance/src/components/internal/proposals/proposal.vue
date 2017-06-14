<template lang="html">
    <div v-if="proposal" class="container" id="internalProposal">
            <div class="row">
        <h3>Proposal: {{ proposal.id }}</h3>
        <div class="col-md-3">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Logs
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Communications</strong><br/>
                                <a ref="showCommsBtn" class="actionBtn">Show</a>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Actions</strong><br/>
                                <a tabindex="2" ref="showActionBtn" class="actionBtn">Show</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                       Submission 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Submitted by</strong><br/>
                                {{ proposal.submitter }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ proposal.lodgement_date | formatDate}}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <tr>
                                        <th>Lodgment</th>
                                        <th>Date</th>
                                        <th>Action</th>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Workflow 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ proposal.processing_status }}
                            </div>
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Referrals</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-control">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select @change="assignTo" :disabled="isFinalised" v-if="!isLoading" class="form-control" v-model="proposal.assigned_officer">
                                        <option value="null"></option>
                                        <option v-for="member in members" :value="member.id">{{member.name}}</option>
                                    </select>
                                    <a v-if="!isFinalised" @click.prevent="assignMyself()" class="actionBtn pull-right">Send</a>
                                </div>
                                <a v-if="!isFinalised" @click.prevent="" class="actionBtn top-buffer-s">Show Referrals</a>
                            </div>
                            <div class="col-sm-12">
                                <div class="separator"></div>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-control">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select @change="assignTo" :disabled="isFinalised" v-if="!isLoading" class="form-control" v-model="proposal.assigned_officer">
                                        <option value="null">Unassigned</option>
                                        <option v-for="member in members" :value="member.id">{{member.name}}</option>
                                    </select>
                                    <a v-if="!isFinalised" @click.prevent="assignMyself()" class="actionBtn pull-right">Assign to me</a>
                                </div>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <div class="row">
                                    <div class="col-sm-12">
                                        <strong>Action</strong><br/>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <button style="width:80%;" class="btn btn-primary" v-if="!isFinalised" @click.prevent="">Enter Requirements</button><br/>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <button style="width:80%;" class="btn btn-primary top-buffer-s" v-if="!isFinalised" @click.prevent="">Request Ammendment</button><br/>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <button style="width:80%;" class="btn btn-primary top-buffer-s" v-if="!isFinalised" @click.prevent="">Decline</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3>Level of Approval</h3>
                            </div>
                            <div class="panel-body panel-collapse">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3>Applicant</h3> 
                            </div>
                            <div class="panel-body panel-collapse">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3>Address Details</h3> 
                            </div>
                            <div class="panel-body panel-collapse">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3>Contact Details</h3>
                            </div>
                            <div class="panel-body panel-collapse">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3>Proposal</h3>
                            </div>
                            <div class="panel-body panel-collapse">
                                <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">
                                    <Proposal form_width="col-md-12" :withSectionsSelector="false" v-if="proposal" :proposal="proposal">
                                        <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                                        <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
                                        <input type='hidden' name="proposal_id" :value="1" />
                                        <div class="row" style="margin-bottom:20px;">
                                          <div class="col-lg-12 pull-right">
                                                <input type="submit" class="btn btn-primary" value="Save and Exit"/>
                                                <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                                                <router-link :to="{name:'apply_proposal',params: { proposal_id: proposal.id }}" class="btn btn-primary">Submit</router-link>
                                          </div>
                                        </div>
                                    </Proposal>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </div>
    </div>
</template>
<script>
import Proposal from '../../form.vue'
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'InternalProposal',
  data: function() {
    return {
      "proposal": null,
      "loading": [],
      form: null,
      members: [],
    }
  },
  components: {
    Proposal
  },
  filters: {
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY HH:mm:ss');
    }
  },
  computed: {
    isLoading: function() {
      return this.loading.length > 0
    },
    csrf_token: function() {
      return helpers.getCookie('csrftoken')
    },
    proposal_form_url: function() {
      return (this.proposal) ? `/api/proposal/${this.proposal.id}/draft.json` : '';
    },
    isFinalised: function(){
        return this.proposal.processing_status == 'Declined' || this.proposal.status == 'Approved';
    }
  },
  methods: {
    save: function(e) {
      let vm = this;
      let formData = new FormData(vm.form);
      vm.$http.post(vm.proposal_form_url,formData).then(res=>{
          swal(
            'Saved',
            'Your proposal has been saved',
            'success'
          )
      },err=>{
      });
    },
    assignTo: function(){
        let vm = this;
        if ( vm.proposal.assigned_officer != 'null'){
            let data = {'user_id': vm.proposal.assigned_officer};
            vm.$http.post(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.proposal.id+'/assign_to')),JSON.stringify(data),{
                emulateJSON:true
            }).then((response) => {
                console.log(response);
                vm.proposal = response.body;
            }, (error) => {
                console.log(error);
            });
            console.log('there');
        }
        else{
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,(vm.proposal.id+'/unassign')))
            .then((response) => {
                console.log(response);
                vm.proposal = response.body;
            }, (error) => {
                console.log(error);
            });
        }
    },
    fetchProposalGroupMembers: function(){
        let vm = this;
        vm.loading.push('Loading Proposal Group Members');
        vm.$http.get(api_endpoints.organisation_access_group_members).then((response) => {
            vm.members = response.body
            vm.loading.splice('Loading Proposal Group Members',1);
        },(error) => {
            console.log(error);
            vm.loading.splice('Loading Proposal Group Members',1);
        })
    },
  },
  mounted: function() {
    let vm = this;
    vm.fetchProposalGroupMembers();
    vm.form = document.forms.new_proposal;
  },
  beforeRouteEnter: function(to, from, next) {
      Vue.http.get(`/api/proposal/${to.params.proposal_id}.json`).then(res => {
          next(vm => {
            vm.proposal = res.body;
          });
        },
        err => {
          console.log(err);
        });
  },
  beforeRouteUpdate: function(to, from, next) {
      Vue.http.get(`/api/proposal/${to.params.proposal_id}.json`).then(res => {
          next(vm => {
            vm.proposal = res.body;
          });
        },
        err => {
          console.log(err);
        });
  }
}
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}
</style>
