<template lang="html">
    <div>
        <div class="col-md-3">
            <h3>{{ displayable_number }}</h3>
            <div v-if="!is_external">
                <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
                <div class="row">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                          Submission
                        </div>
                        <div class="panel-body panel-collapse">
                            <div class="row">
                                <div class="col-sm-12">
                                    <strong>Submitted by</strong><br/>
                                    {{ returns.submitter.first_name}} {{ returns.submitter.last_name}}
                                </div>
                                <div class="col-sm-12 top-buffer-s">
                                    <strong>Lodged on</strong><br/>
                                    {{ returns.lodgement_date | formatDate}}
                                </div>
                                <div class="col-sm-12 top-buffer-s">
                                    <table class="table small-table">
                                    <tr>
                                        <th>Lodgement</th>
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
                        <div class="panel-heading">Workflow</div>
                        <div class="panel-body panel-collapse">
                            <div class="row">
                                <div class="col-sm-12">
                                    <strong>Status</strong><br/>
                                    {{ returns.processing_status }}
                                </div>
                                <div class="col-sm-12 top-buffer-s">
                                    <strong>Currently assigned to</strong><br/>
                                    <div class="form-group">
                                        <select v-show="isLoading" class="form-control">
                                            <option value="">Loading...</option>
                                        </select>
                                        <select @change="assignTo"  v-if="!isLoading" class="form-control">
                                            <option value="null">Unassigned</option>
                                        <!-- <option v-for="member in returns.return_curators" :value="member.id">{{member.first_name}} {{member.last_name}}</option> -->
                                        </select>
                                        <!-- <a v-if="!canViewonly" @click.prevent="assignMyself()" class="actionBtn pull-right">Assign to me</a> -->
                                    </div>
                                </div>
                                <div class="col-sm-12 top-buffer-s">
                                    <strong>Action</strong><br/><br/>
                                    <button style="width:255px;" class="btn btn-primary btn-md" @click.prevent="acceptReturn()">Accept</button><br/><br/>
                                    <button style="width:255px;" class="btn btn-primary btn-md" @click.prevent="amendmentRequest()">Request Amendment</button>
                                    <br/><br/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tabs Layout -->
        <div class="col-md-9" >
            <div id="tabs" v-show="displayable_tabs">
                <ul class="nav nav-tabs" id="tabs-section" data-tabs="tabs" >
                    <li class="active"><a id="0">1. Return</a></li>
                    <li v-if="returns.has_payment" ><a id="1">2. Confirmation</a></li>
                </ul>
            </div>
            {{ this.$slots.default }}
        </div>

        <AmendmentRequest ref="amendment_request" ></AmendmentRequest>

    </div>
</template>


<script>
import Vue from 'vue';
import AmendmentRequest from '../internal/returns/amendment_request.vue';
import { mapActions, mapGetters } from 'vuex';
import CommsLogs from '@common-components/comms_logs.vue'
import '@/scss/forms/form.scss';
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'returns-renderer-form',
  props: {
      level:{
            type: String,
            required: true,
            validator:function(val) {
                let options = ['internal','external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
  },
  components: {
    CommsLogs,
    AmendmentRequest,
  },
  filters: {
    formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
    }
  },
  data: function() {
    return {
        returns_tab_id: 0,

        assignTo: false,
        loading: [],
        isLoading: false,

        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.returns,this.$route.params.return_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.returns,this.$route.params.return_id+'/comms_log'),
        comms_add_url: helpers.add_endpoint_json(api_endpoints.returns,this.$route.params.return_id+'/add_comms_log'),
    }
  },
  props:{
    form_width: {
        type: String,
        default: 'col-md-9'
    },
  },
  computed: {
    ...mapGetters([
      'returns',
      'returns_tabs',
      'selected_returns_tab_id',
      'species_list',
      'is_external',
      'current_user',
    ]),
    is_submitted: function() {
      return this.returns.lodgement_date != null ? true : false;
    },
    displayable_number: function() {
      if (this.is_external && this.returns.lodgement_date != null) {
          return '\u00A0'
      }
      return 'Return: ' + this.returns.lodgement_number
    },
    displayable_tabs: function() {
      if (this.is_external && this.returns.lodgement_date != null) {
          return false
      }
      return true
    }
  },
  methods: {
    ...mapActions([
      'setReturnsTabs',
      'setReturnsSpecies',
      'setReturnsExternal',
      'setReturns',
      'loadCurrentUser',
    ]),
    selectReturnsTab: function(component) {
        this.returns_tab_id = component.id;
        this.setReturnsTab({id: component.id, name: component.label});
    },
    amendmentRequest: function(){
      let vm = this;

      vm.$refs.amendment_request.amendment.text = '';
      vm.$refs.amendment_request.isModalOpen = true;
    },
    canAssignToOfficer: function(){
      if(!this.userHasRole('licensing_officer')) {
        return false;
      }
      return this.returns && this.returns.processing_status.id == 'with_curator'
    },
    userIsAssignedOfficer: function(){
      return this.current_user.id == this.returns.assigned_to;
    },
  },
  created: function() {
    this.loadCurrentUser({ url: `/api/my_user_details` });
    if (this.returns.format != 'sheet') { // Return Running Sheet checks 'internal' for read-only.
      var headers = this.returns.table[0]['headers']
      for(let i = 0; i<headers.length; i++) {
        headers[i]['readonly'] = !this.is_external
      }
      this.setReturns(this.returns);
    }
    // TODO: Species list can be rendered here for internal/external Returns.
    // this.setReturnsSpecies({});
  },
}
</script>
