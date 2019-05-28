<template lang="html">
    <div>
        <div class="col-md-3" v-if="isExternal">
            <h3>Return: {{ returns.lodgement_number }}</h3>
            <div v-if="returns.format === 'sheet'">
                <label>Species on Return:</label>
                <div v-for="specie in returns.sheet_species_list">
                    <a class="change-species" :species_id="specie" :href="'/external/return/sheet/'+returns.id+'/'+specie"><h5>{{species_list[specie]}}</h5></a>
                </div>
            </div>
        </div>
        <div class="col-md-3" v-if="isInternal">
            <h3>Return: {{ returns.lodgement_number }}</h3>
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
            <div class="panel panel-default">
                <div class="panel-heading">Workflow</div>
                <div class="panel-body panel-collapse">
                    <div class="row">
                        <div class="col-sm-12">
                            <strong>Status</strong><br/>
                             {{ returns.processing_status.name }}
                        </div>
                        <div class="col-sm-12 top-buffer-s">
                            <strong>Currently assigned to</strong><br/>
                            <div class="form-group">
                                <select v-show="isLoading" class="form-control">
                                    <option value="">Loading...</option>
                                </select>
                                <select @change="assignTo"  v-if="!isLoading" class="form-control">
                                    <option value="null">Unassigned</option>
                        <!-- <option v-for="member in return.return_curators" :value="member.id">{{member.first_name}} {{member.last_name}}</option> -->
                                </select>
                      <!-- <a v-if="!canViewonly" @click.prevent="assignMyself()" class="actionBtn pull-right">Assign to me</a> -->
                            </div>
                        </div>
                        <div class="col-sm-12 top-buffer-s">
                            <strong>Action</strong><br/>
                            <button style="width:255px;" class="btn btn-primary btn-md" @click.prevent="acceptReturn()">Accept</button><br/><br/>
                            <button style="width:255px;" class="btn btn-primary btn-md" @click.prevent="amendmentRequest()">Request Amendment</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </div>

        <!-- Tabs Layout -->
        <div class="col-md-1">&nbsp;</div>
        <div :class="`${form_width ? form_width : 'col-md-9'}`">
            <div id="tabs" >
                <ul class="nav nav-tabs" id="tabs-section" data-tabs="tabs" >
                    <li class="active"><a id="0">1. Return</a></li>
                    <li v-if="returns.has_payment" ><a id="1">2. Confirmation</a></li>
                </ul>
            </div>
            {{ this.$slots.default }}
        </div>
    </div>
</template>


<script>
import Vue from 'vue';
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
  components: {
    CommsLogs,
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
      'isInternal',
      'isExternal',
      'current_user',
      'has_role'
    ]),
    returnsData: function() {
        return this.returns;
    }
  },
  methods: {
    ...mapActions([
      'setReturnsTabs',
      'setReturnsSpecies',
    ]),
    selectReturnsTab: function(component) {
        this.returns_tab_id = component.id;
        this.setReturnsTab({id: component.id, name: component.label});
    },
    initReturnsTab: function() {
        console.log('initReturnsTab')
        let tabs_list = [{name: 'step-0', label: '1. Return', id: 0},
                         {name: 'step-1', label: '2. Confirmation', id: 1},
                        ];
        this.setReturnsTabs(tabs_list);
    },
  },
}
</script>
