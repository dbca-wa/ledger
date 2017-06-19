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
                <div v-show="false" class="col-md-12">
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
                                  <form class="form-horizontal">
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Name</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantName" placeholder="" v-model="proposal.applicant.name">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >ABN/ACN</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="applicantABN" placeholder="" v-model="proposal.applicant.abn">
                                        </div>
                                      </div>
                                  </form>
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
                                  <form class="form-horizontal">
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Street</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="street" placeholder="" v-model="proposal.applicant.address.line1">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                        <div class="col-sm-6">
                                            <input disabled type="text" class="form-control" name="surburb" placeholder="" v-model="proposal.applicant.address.locality">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">State</label>
                                        <div class="col-sm-2">
                                            <input disabled type="text" class="form-control" name="country" placeholder="" v-model="proposal.applicant.address.state">
                                        </div>
                                        <label for="" class="col-sm-2 control-label">Postcode</label>
                                        <div class="col-sm-2">
                                            <input disabled type="text" class="form-control" name="postcode" placeholder="" v-model="proposal.applicant.address.postcode">
                                        </div>
                                      </div>
                                      <div class="form-group">
                                        <label for="" class="col-sm-3 control-label" >Country</label>
                                        <div class="col-sm-4">
                                            <input disabled type="text" class="form-control" name="country" v-model="proposal.applicant.address.country"/>
                                        </div>
                                      </div>
                                   </form>
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
                                <div v-if="contactsURL != '' && contactsURL != 'undefined'">
                                <datatable ref="contacts_datatable" id="organisation_contacts_datatable" :dtOptions="contacts_options" :dtHeaders="contacts_headers"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
                    <div class="row">
                        <form :action="proposal_form_url" method="post" name="new_proposal" enctype="multipart/form-data">
                            <Proposal form_width="inherit" :withSectionsSelector="false" v-if="proposal" :proposal="proposal">
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
</template>
<script>
import Proposal from '../../form.vue'
import Vue from 'vue'
import datatable from '@vue-utils/datatable.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'InternalProposal',
  data: function() {
    let vm = this;
    return {
        "proposal": null,
        "loading": [],
        form: null,
        members: [],
        contacts_headers:["Name","Phone","Mobile","Fax","Email"],
        contacts_options:{
            language: {
                processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
            },
            responsive: true,
            ajax: {
                "url": vm.contactsURL,
                "dataSrc": ''
            },
            columns: [
                {
                    mRender:function (data,type,full) {
                        return full.first_name + " " + full.last_name;
                    }
                },
                {data:'phone_number'},
                {data:'mobile_number'},
                {data:'fax_number'},
                {data:'email'},
              ],
              processing: true
        }
    }
  },
  components: {
    Proposal,
    datatable
  },
  filters: {
    formatDate: function(data){
        return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
    }
  },
  watch: {
    contactsURL: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.$refs.contacts_datatable.vmDataTable.ajax.url(this.contactsURL);
            vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
        })
    }
  },
  computed: {
    contactsURL: function(){
        return this.proposal!= null ? helpers.add_endpoint_json(api_endpoints.organisations,this.proposal.applicant.id+'/contacts') : '';
    },
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
      Vue.http.get(`/api/proposal/${to.params.proposal_id}/internal_proposal.json`).then(res => {
          next(vm => {
            vm.proposal = res.body;
            vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
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
            vm.proposal.applicant.address = vm.proposal.applicant.address != null ? vm.proposal.applicant.address : {};
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
