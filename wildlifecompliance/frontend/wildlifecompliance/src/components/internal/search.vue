<template>
<div class="container" id="internalSearch">
    <UserDashTable level="internal" :url="users_url" />
    <OrganisationDashTable />
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Keywords
                        <a :href="'#'+kBody" data-toggle="collapse"  data-parent="#keywordInfo" expanded="true" :aria-controls="kBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="kBody">
                    <div class="row">
                      <div>
                        <div class="form-group">
                          <label for="" class="control-label col-lg-12">Filter</label>
                          <div class="form-check form-check-inline col-md-3">
                              <input  class="form-check-input" ref="searchApplication" id="searchApplication" name="searchApplication" type="checkbox" v-model="searchApplication" />
                              <label class="form-check-label" for="searchApplication">Application</label>

                          </div>
                          <div class="form-check form-check-inline col-md-3">
                              <input  class="form-check-input" ref="searchLicence" id="searchLicence" name="searchLicence" type="checkbox" v-model="searchLicence" />
                              <label class="form-check-label" for="searchLicence">Licence</label>
                          </div>
                          <div class="form-check form-check-inline col-md-3">
                              <input  class="form-check-input" ref="searchReturn" id="searchReturn" name="searchReturn" type="checkbox" v-model="searchReturn" />
                              <label class="form-check-label" for="searchReturn">Return with requirements</label>
                          </div>
                          <label for="" class="control-label col-lg-12">Keyword</label>
                            <div class="col-md-8">
                              <input type="search"  class="form-control input-sm" name="details" placeholder="" v-model="keyWord"></input>
                            </div>
                            <div class="col-md-1">
                            </div>
                            <div class="col-md-3">
                              <input type="button" @click.prevent="addKeyword" class="btn btn-primary" value="Add"/>
                            </div>
                        </div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-lg-12">
                          <ul class="list-inline" style="display: inline; width: auto;">
                              <li class="list-inline-item" v-for="(item,i) in searchKeywords">
                                <button @click.prevent="" class="btn btn-light" style="margin-top:5px; margin-bottom: 5px">{{item}}</button><a href="" @click.prevent="removeKeyword(i)"><span class="glyphicon glyphicon-remove "></span></a>
                              </li>
                          </ul>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-lg-12">
                        <div>
                          <input :disabled="!hasSearchKeywords" type="button" @click.prevent="searchKeyword" class="btn btn-primary" style="margin-bottom: 5px"value="Search"/>
                          <input type="reset" @click.prevent="clearKeywordSearch" class="btn btn-primary" style="margin-bottom: 5px"value="Clear"/>
                        </div>
                      </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="keyword_search_datatable" :id="datatable_id" :dtOptions="keyword_search_options"  :dtHeaders="keyword_search_headers"/>
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
                    <h3 class="panel-title">Reference Number
                        <a :href="'#'+rBody" data-toggle="collapse"  data-parent="#referenceNumberInfo" expanded="true" :aria-controls="rBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="rBody">
                    <div class="row">
                       <label for="" class="control-label col-lg-12">Reference Number</label>
                          <div class="col-md-8">
                              <input type="search"  class="form-control input-sm" name="referenceWord" placeholder="" v-model="referenceWord"></input>
                          </div>
                          <div >
                            <input type="button" @click.prevent="search_reference" class="btn btn-primary" style="margin-bottom: 5px" value="Search"/>
                        </div>
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
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
import alert from '@/utils/vue/alert.vue'
import UserDashTable from '@common-components/users_dashboard.vue'
import OrganisationDashTable from '@internal-components/organisations/organisations_dashboard.vue'
import '@/scss/dashboards/search.scss';
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
import utils from './utils'
export default {
    name: 'SearchDashboard',
    data() {
        let vm = this;
        return {
            users_url: helpers.add_endpoint_join(api_endpoints.users_paginated,'datatable_list/?format=datatables'),
            rBody: 'rBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            cBody: 'cBody' + vm._uid,
            kBody: 'kBody' + vm._uid,
            loading: [],
            searchKeywords: [],
            hasSearchKeywords: false,
            selected_organisation:'',
            organisations: null,
            searchApplication: true,
            searchLicence: false,
            searchReturn: false,
            referenceWord: '',
            keyWord: null,
            results: [],
            errors: false,
            errorString: '',
            datatable_id: 'keyword-search-datatable-'+vm._uid,
            keyword_search_headers:["Number","Type","Applicant","Text Found","Action"],
            keyword_search_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                data: vm.results,
                columns: [
                    {data: "number"},
                    {data:"record_type"},
                    {data: "applicant"},
                    {data: "text",
                        mRender: function (data,type,full) {
                            if(data.value) {
                                return data.value;
                            }
                            else {
                                return data;
                            }
                        }
                    },
                    {data: "record_id",
                        mRender:function (data,type,full) {
                            let links = '';
                            if(full.type == 'Application') {
                              links +=  `<a href='/internal/application/${full.id}'>View</a><br/>`;
                            }
                            if(full.type == 'Licence') {
                              links +=  `<a href="${full.licence_document}" target="_blank">View</a>`;
                            }
                            if(full.type == 'Return') {
                              links +=  `<a href='/internal/return/${full.id}'>View</a><br/>`;
                            }
                            return links;
                        }
                    }
                ],
                processing: true
            }
        }
    },
    watch: {
        searchKeywords: function() {
            if (this.searchKeywords.length > 0){
                this.hasSearchKeywords = true;
            } else {
                this.hasSearchKeywords = false;
            };
        }
    },
    components: {
        alert,
        datatable,
        UserDashTable,
        OrganisationDashTable
    },
    beforeRouteEnter:function(to,from,next){
        let initialisers = [
            utils.fetchOrganisations(),
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.organisations = data[0].results;
            });
        });
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        },
        showError: function() {
            return this.errors;
        }
    },
    methods: {
        addListeners: function(){
            let vm = this;
            // Initialise select2 for organisation
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
        },
        search_reference: function() {
          let vm = this;
          if(vm.referenceWord)
          {
            vm.$http.post('/api/search_reference.json',{
              reference_number: vm.referenceWord,

            }).then(res => {
              console.log(res)
              vm.errors = false;
              vm.errorString = '';
              vm.$router.push({ path: '/internal/'+res.body.type+'/'+res.body.id });
              },
            error => {
              console.log(error);
              vm.errors = true;
              vm.errorString = helpers.apiVueResourceError(error);
            });
          }
        },
        addKeyword: function() {
          let vm = this;
          if(vm.keyWord != null)
          {
            vm.searchKeywords.push(vm.keyWord);
          }
        },
        removeKeyword: function(index) {
          let vm = this;
          if(index >-1)
          {
            vm.searchKeywords.splice(index,1);
          }
        },
        clearKeywordSearch: function() {
          let vm = this;
          if(vm.keyWord != null)
          {
            vm.searchKeywords = [];
          }
          vm.keyWord = null;
          vm.results = [];
          vm.$refs.keyword_search_datatable.vmDataTable.clear()
          vm.$refs.keyword_search_datatable.vmDataTable.draw();
        },
        searchKeyword: function() {
          let vm = this;
          if(this.searchKeywords.length > 0)
          {
            vm.$http.post('/api/search_keywords.json',{
              searchKeywords: vm.searchKeywords,
              searchApplication: vm.searchApplication,
              searchLicence: vm.searchLicence,
              searchReturn: vm.searchReturn,
              is_internal: true,
            }).then(res => {
              vm.results = res.body;
              vm.$refs.keyword_search_datatable.vmDataTable.clear()
              vm.$refs.keyword_search_datatable.vmDataTable.rows.add(vm.results);
              vm.$refs.keyword_search_datatable.vmDataTable.draw();
            },
            err => {
              console.log(err);
            });
          }
        },
    },
    mounted: function () {
        let vm = this;
        vm.keyword_search_options.data = vm.results;
        vm.$refs.keyword_search_datatable.vmDataTable.draw();
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