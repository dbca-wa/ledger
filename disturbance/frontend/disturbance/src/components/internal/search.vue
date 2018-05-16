<template>
<div class="container" id="internalSearch">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Search Organisations
                        <a :href="'#'+oBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="oBody">
                    <div class="row">
                        <form name="searchOrganisationForm">
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label class="control-label" for="Organisation">Search Organisation</label>
                                    <select v-if="organisations == null" class="form-control" name="organisation" v-model="selected_organisation">
                                        <option value="">Loading...</option>
                                    </select>
                                    <select v-else ref="searchOrg" class="form-control" name="organisation">
                                        <option value="">Select Organisation</option>
                                        <option v-for="o in organisations" :value="o.id">{{ o.name }}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-12 text-center">
                                <router-link :disabled="selected_organisation == ''" :to="{name:'internal-org-detail',params:{'org_id':parseInt(selected_organisation)}}" class="btn btn-primary">View Details</router-link>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Search Keywords
                        <a :href="'#'+kBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="kBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="kBody">
                    <div class="row">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Search Reference Number
                        <a :href="'#'+rBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="rBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="rBody">
                    <div class="row">
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</template>
<script>
import $ from 'jquery'
import datatable from '@/utils/vue/datatable.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
import utils from './utils'
export default {
  name: 'ExternalDashboard',
  data() {
    let vm = this;
    return {
      rBody: 'rBody' + vm._uid,
      oBody: 'oBody' + vm._uid,
      kBody: 'kBody' + vm._uid,
      loading: [],
      selected_organisation:'',
      organisations: null,
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
                        links +=  `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                        return links;
                  }
              }
          ],
          processing: true
      }
    }
    
  },
    watch: {},
    components: {
        datatable,
    },
    beforeRouteEnter:function(to,from,next){
        utils.fetchOrganisations().then((response)=>{
            next(vm => {
                vm.organisations = response;
            });
        },
        (error) =>{
            console.log(error);
        });
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        }
    },
    methods: {
        addListeners: function(){
            let vm = this;
            // Initialise select2 for region
            $(vm.$refs.searchOrg).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Organisation"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_organisation = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.selected_organisation = selected.val();
            });
        }
    },
    mounted: function () {
        let vm = this;
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        } );
    },
    updated: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.addListeners();
        });
        
    }
}
</script>
