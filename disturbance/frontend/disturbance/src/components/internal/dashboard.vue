<template>
<div class="container" id="externalDash">
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
                            <router-link  style="margin-top:25px;" class="btn btn-primary pull-right" :to="{ name: 'new_proposal' }">New Proposal</router-link>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Lodged From</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Lodged To</label>
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
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Proposals referred to me
                        <a :href="'#'+rBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="rBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="rBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Region</label>
                                <select v-show="isLoading" class="form-control">
                                    <option value="">Loading...</option>
                                </select>
                                <select v-if="!isLoading" class="form-control" v-model="filterReferalRegion">
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
                                <select v-if="!isLoading" class="form-control" v-model="filterReferalActivity">
                                    <option value="All">All</option>
                                    <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterReferalStatus">
                                    <option value="All">All</option>
                                    <option value="current">Current</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Lodged From</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterReferalLodgedFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Lodged To</label>
                            <div class="input-group date" id="booking-date-from">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterReferalLodgedTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Submitter</label>
                                <select class="form-control" v-model="filterReferalSubmitter">
                                    <option value="">Select Submitter</option>
                                    <option value="current">Current</option>
                                </select>
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
      rBody: 'rBody' + vm._uid,
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
      // Filters for Referals
      filterReferalRegion: '',
      filterReferalActivity: '',
      filterReferalStatus: 'All',
      filterReferalLodgedFrom: '',
      filterReferalLodgedTo: '',
      filterReferalSubmitter: '',
    }
  },
  watch: {},
  computed: {
    isLoading: function () {
      return this.loading.length == 0;
    }
  },
  methods: {},
  mounted: function () {
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
