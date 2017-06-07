<template>
<div class="container" id="internalOrgAccess">
    <div class="row">
        <h3>Organisation Access Request {{ access.id }}</h3>
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
                                <a @click.prevent="" class="actionBtn">Show</a>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Actions</strong><br/>
                                <a @click.prevent="" class="actionBtn">Show</a>
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
                                {{ access.requester.full_name }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Lodged on</strong><br/>
                                {{ access.lodgement_date | formatDate}}
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
                                {{ access.status }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Currently assigned to</strong><br/>
                                <div class="form-group">
                                    <select v-show="isLoading" class="form-control">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select v-if="!isLoading" class="form-control" v-model="access.assigned_to">
                                        <option v-for="member in members" :value="member.id">{{member.name}}</option>
                                    </select>
                                    <a href="" @click.prevent="" class="pull-right">Assign to me</a>
                                </div>
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <strong>Action</strong><br/>
                                <button class="btn btn-primary" @click.prevent="">Accept</button><br/>
                                <button class="btn btn-primary top-buffer-s" @click.prevent="">Decline</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3>Organisation Access Request</h3> 
                    </div>
                    <div class="panel-body panel-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <form class="form-horizontal" name="access_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Organisation</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="name" placeholder="" v-model="access.name">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">ABN</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="abn" placeholder="" v-model="access.abn">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Letter</label>
                                        <div class="col-sm-6">
                                            <a target="_blank" :href="access.identification"><i class="fa fa-file-pdf-o"></i>&nbsp;Letter.PDF</a>
                                        </div>
                                    </div>   
                                    <div class="form-group" style="margin-top:50px;">
                                        <label for="" class="col-sm-3 control-label">Phone</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="phone" placeholder="" v-model="access.requester.phone_number">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Mobile</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="mobile" placeholder="" v-model="access.requester.mobile_number">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Email</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="email" placeholder="" v-model="access.requester.email">
                                        </div>
                                    </div>   
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
import $ from 'jquery'
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'OrganisationAccess',
  data() {
    let vm = this;
    return {
      loading: [],
      access: {
        requester: {}
      },
      members: [],
      // Filters
    }
  },
  watch: {},
  filters: {
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY');
    }
  },
  beforeRouteEnter: function(to, from, next){
    Vue.http.get(helpers.add_endpoint_json(api_endpoints.organisation_requests,to.params.access_id)).then((response) => {
        next(vm => {
            vm.access = response.body
        })
    },(error) => {
        console.log(error);
    })
  },
  components: {
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    }
  },
  methods: {
    fetchAccessGroupMembers: function(){
        let vm = this;
        vm.loading.push('Loading Access Group Members');
        vm.$http.get(api_endpoints.organisation_access_group_members).then((response) => {
            vm.members = response.body
            vm.loading.splice('Loading Access Group Members',1);
        },(error) => {
            console.log(error);
            vm.loading.splice('Loading Access Group Members',1);
        })

    },
    assignMyself: function(){
        //vm.$http
    }
  },
  mounted: function () {
    this.fetchAccessGroupMembers();
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
</style>
