<template>
<div class="container" id="internalSearch">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Search People 
                        <a :href="'#'+cBody" data-toggle="collapse"  data-parent="#peopleInfo" expanded="true" :aria-controls="cBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="cBody">
                    <div class="row">
                        <div class="col-md-4">
                            <label class="control-label">
                                <a href="/internal/users">Click here to search for people</a>
                            </label>
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
                    <h3 class="panel-title">Search Organisations
                        <a :href="'#'+oBody" data-toggle="collapse"  data-parent="#organisationInfo" expanded="false" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse" :id="oBody">
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
                        <a :href="'#'+kBody" data-toggle="collapse"  data-parent="#keywordInfo" expanded="false" :aria-controls="kBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse" :id="kBody">
                    <div class="row">
                        <form name="searchKeywordForm">
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label class="control-label" for="Keyword">Search Keyword</label>
                                </div>
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
                    <h3 class="panel-title">Search Reference Number 
                        <a :href="'#'+rBody" data-toggle="collapse"  data-parent="#referenceNumberInfo" expanded="false" :aria-controls="rBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse" :id="rBody">
                    <div class="row">
                        <form name="searchReferenceNumberForm">
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label class="control-label" for="ReferenceNumber">Search Reference Number</label>
                                </div>
                            </div>
                        </form>
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
      cBody: 'cBody' + vm._uid,
      kBody: 'kBody' + vm._uid,
      loading: [],
      selected_organisation:'',
      organisations: null,
    }
  },
    watch: {},
    components: {
        datatable,
    },
    beforeRouteEnter:function(to,from,next){
        let initialisers = [
            utils.fetchOrganisations(),
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {
                vm.organisations = data[0];
            });
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
