<template>
<div class="container" id="externalDash">
    <div class="row">
        <div class="col-sm-12">
            <div class="well well-sm">
                <p>
                    Welcome to the Values Impact Assessment online system dashboard.<br/><br/> Here you can access your existing approvals, view any proposals in progress, lodge new<br/> proposals or submit information required to comply with requirements listed
                    on your approval
                </p>
            </div>
        </div>
    </div>
    <ProposalDashTable level='external' :url='proposals_url'/>
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Approvals <small>View existing approvals and ammed or renew them</small>
                        <a :href="'#'+aBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="aBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="aBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Region</label>
                                <select v-show="isLoading" class="form-control">
                                    <option value="">Loading...</option>
                                </select>
                                <select v-if="!isLoading" class="form-control" v-model="filterApprovalRegion">
                                    <option value="All">All</option>
                                    <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Activity</label>
                                <select v-show="isLoading" class="form-control" name="">
                                    <option value="">Loading...</option>
                                </select>
                                <select v-if="!isLoading" class="form-control" v-model="filterApprovalActivity">
                                    <option value="All">All</option>
                                    <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterApprovalStatus">
                                    <option value="All">All</option>
                                    <option value="current">Current</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Expiry From</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterApprovalExpiryFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Expiry To</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterApprovalExpiryTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Compliance with requirements <small>View submitted compliances and submit new ones</small>
                        <a :href="'#'+cBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="cBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="cBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Region</label>
                                <select v-show="isLoading" class="form-control">
                                    <option value="">Loading...</option>
                                </select>
                                <select v-if="!isLoading" class="form-control" v-model="filterComplianceRegion">
                                    <option value="All">All</option>
                                    <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Activity</label>
                                <select v-if="!isLoading" class="form-control" v-model="filterComplianceActivity">
                                    <option value="All">All</option>
                                    <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterComplianceStatus">
                                    <option value="All">All</option>
                                    <option value="current">Current</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Expiry From</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceDueFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Expiry To</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceDueTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
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

import datatable from '@/utils/vue/datatable.vue'
import ProposalDashTable from '@common-utils/proposals_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'ExternalDashboard',
    data() {
        let vm = this;
        return {
        aBody: 'aBody' + vm._uid,
        pBody: 'pBody' + vm._uid,
        cBody: 'cBody' + vm._uid,
        loading: [],
        proposals_url: helpers.add_endpoint_json(api_endpoints.proposals,'user_list'),
        // Filters for Approvals
        filterApprovalRegion: '',
        filterApprovalActivity: '',
        filterApprovalStatus: 'All',
        filterApprovalExpiryFrom: '',
        filterApprovalExpiryTo: '',
        // Filters for Compliance
        filterComplianceRegion: '',
        filterComplianceActivity: '',
        filterComplianceStatus: 'All',
        filterComplianceDueFrom: '',
        filterComplianceDueTo: '',
        //
        datepickerOptions:{
            format: 'DD/MM/YYYY',
            showClear:true,
            useCurrent:false,
            keepInvalid:true,
            allowInputToggle:true
        },
      }
  },
  components:{
      datatable,
        ProposalDashTable
  },
  watch: {},
  computed: {
    isLoading: function () {
      return this.loading.length == 0;
    }
  },
  methods: {
      discardProposal:function (proposal_id) {
          let vm = this;
          swal({
              title: "Discard Proposal",
              text: "Are you sure you want to discard this proposal?",
              type: "warning",
              showCancelButton: true,
              confirmButtonText: 'Discard Proposal',
              confirmButtonColor:'#d9534f'
          }).then(() => {
              vm.$http.delete(api_endpoints.discard_proposal(proposal_id))
              .then((response) => {
                  swal(
                    'Discarded',
                    'Your proposal has been discarded',
                    'success'
                  )
                  vm.$refs.proposal_datatable.vmDataTable.ajax.reload();
              }, (error) => {
                  console.log(error);
              });
          },(error) => {

          });
        },
  },
  mounted: function () {
      let vm =this;
    $( 'a[data-toggle="collapse"]' )
      .on( 'click', function () {
        var chev = $( this )
          .children()[ 0 ];
        window.setTimeout( function () {
          $( chev )
            .toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
        }, 100 );
      } );

  }
}
</script>
