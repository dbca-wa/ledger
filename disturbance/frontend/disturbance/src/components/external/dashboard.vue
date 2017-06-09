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
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Proposals <small>View existing proposals and lodge new ones</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Region</label>
                                <select v-show="isLoading" class="form-control">
                                    <option value="">Loading...</option>
                                </select>
                                <select v-if="!isLoading" class="form-control" v-model="filterProposalRegion">
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
                                <select v-if="!isLoading" class="form-control" v-model="filterProposalActivity">
                                    <option value="All">All</option>
                                    <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterProposalStatus">
                                    <option value="All">All</option>
                                    <option value="current">Current</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <router-link  style="margin-top:25px;" class="btn btn-primary pull-right" :to="{ name: 'apply_proposal' }">New Proposal</router-link>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Expiry From</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Expiry To</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Submitter</label>
                                <select class="form-control" v-model="filterProposalSubmitter">
                                    <option value="">Select Submitter</option>
                                    <option value="current">Current</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="proposal_datatable" id="proposal_datatable" :dtOptions="proposal_options" :dtHeaders="proposal_headers"/>
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
                                <select v-show="isLoading" class="form-control" name="">
                                    <option value="">Loading...</option>
                                </select>
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
      // Filters for Proposals
      filterProposalRegion: '',
      filterProposalActivity: '',
      filterProposalStatus: 'All',
      filterProposalLodgedFrom: '',
      filterProposalLodgedTo: '',
      filterProposalSubmitter: '',
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
      proposal_headers:["Number","Region","Activity","Title","Submiter","Proponent","Status","Logded on","Action"],
      proposal_options:{
          language: {
              processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
          },
          responsive: true,
          ajax: {
              "url": api_endpoints.proposals,
              "dataSrc": ''
          },
          columns: [
              {data: "id"},
              {
                  data:'data',
                  mRender:function (data,type,full) {
                      if (data) {
                          let region = (data[0].region)?data[0].region:'n/a';
                          return `${region}`;
                      }
                     return ''
                  }
              },
              {
                  data:'data',
                  mRender:function (data,type,full) {
                      if (data) {
                           return `${data[0].activity}`;
                      }
                     return ''
                  }
              },
              {
                  data:'data',
                  mRender:function (data,type,full) {
                      if (data) {
                           return `${data[0].project_details[0].project_title}`;
                      }
                     return ''
                  }
              },
              {
                  data: "submitter",
                  mRender:function (data,type,full) {
                      if (data) {
                           return `${data.first_name} ${data.last_name}`;
                      }
                     return ''
                  }
              },
              {data: "applicant"},
              {data: "processing_status"},
              {data: "lodgement_date"},
              {
                  mRender:function (data,type,full) {
                      let links = '';
                      if (full.processing_status == 'draft') {
                         links +=  `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                         links +=  `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                      }
                      if (full.processing_status == 'accepted' || full.processing_status == 'under review') {
                         links +=  `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                      }
                      return links;
                  }
              }
          ],
          processing: true
      }
    }
  },
  components:{
      datatable
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
      }
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

      vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
            e.preventDefault();
            var id = $(this).attr('data-discard-proposal');
            vm.discardProposal(id);
        });
  }
}
</script>
