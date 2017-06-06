<template>
<div class="container" id="internalOrgAccessDash">
    <div class="row">
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Organisation</label>
                <select v-show="isLoading" class="form-control">
                    <option value="">Loading...</option>
                </select>
                <select v-if="!isLoading" class="form-control" v-model="filterOrganisation">
                    <option value="All">All</option>
                    <option v-for="campground in campgrounds" :value="campground.id">{{campground.name}}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Applicant</label>
                <select v-show="isLoading" class="form-control" name="">
                    <option value="">Loading...</option>
                </select>
                <select v-if="!isLoading" class="form-control" v-model="filterApplicant">
                    <option value="All">All</option>
                    <option v-for="region in regions" :value="region.id">{{region.name}}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Status</label>
                <select class="form-control" v-model="filterStatus">
                    <option value="All">All</option>
                    <option value="current">Current</option>
                </select>
            </div>
        </div>
    </div>
    <datatable ref="org_access_table" id="org-access-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders"></datatable>
</div>
</template>
<script>
import $ from 'jquery'
import datatable from '@vue-utils/datatable.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'OrganisationAccessDashboard',
  data() {
    let vm = this;
    return {
      loading: [],
      // Filters
      filterOrganisation: '',
      filterApplicant : '',
      filterStatus: 'All',
        dtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                processing:true,
                ajax: {
                    "url": api_endpoints.organisation_requests,
                    "dataSrc": '',
                },
                columns:[
                    {
                        data:"id",
                    },
                    {
                        data:"name",
                    },
                    {
                        data:"requester",
                    },
                    {
                        data:"status",
                    },
                    {
                        data:"lodgement_date",
                        mRender:function(data,type,full){
                            return moment(data).format('DD/MM/YYYY')
                        }
                    },
                    {
                        data:"assigned_officer",
                    },
                    {
                        data:"id",
                        mRender:function(data, type, full){
                            var column = "<td ><a href='/internal/organisations/access/\__ID__\' >View </a><br/><a href='/internal/organisations/access/\__ID__\'> Process </a>";
                            return column.replace(/__ID__/g, data);
                        }
                    },
                ]
            },
            dtHeaders:["Request Number","Organisation","Applicant","Status","Lodged on","Assigned To","Action"],
    }
  },
  watch: {},
  components: {
    datatable
  },
  computed: {
    isLoading: function () {
      return this.loading.length == 0;
    }
  },
  methods: {},
  mounted: function () {
  }
}
</script>
