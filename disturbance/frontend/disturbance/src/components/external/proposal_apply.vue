<template lang="html">
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Apply on behalf of
                            <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body collapse in" :id="pBody">
                        <form class="form-horizontal" name="personal_form" method="post">
                            <div class="col-sm-12">
                                <div class="form-group">
                                    <div v-for="org in profile.disturbance_organisations" class="radio">
                                        <label>
                                          <input type="radio" name="behalf_of_org" v-model="behalf_of"  :value="org.id"> On behalf of {{org.name}}
                                        </label>
                                    </div>
                                    <div class="radio">
                                        <label class="radio-inline">
                                          <input type="radio" name="behalf_of_org" v-model="behalf_of"  value="other" > On behalf of an organisation (as an authorised agent)
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div v-if="behalf_of == 'other'" class="col-sm-12">
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label">Organisation</label>
                                        <input type="text" class="form-control" name="first_name" placeholder="" v-model="agent.organisation">
                                    </div>
                                    <div class="form-group col-sm-1"></div>
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >ABN / ACN</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.abn">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Organisation contact given name(s)</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.given_names">
                                    </div>
                                    <div class="form-group col-sm-1"></div>
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Orgnisation contact surname</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.surname">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="form-group col-sm-5">
                                        <label for="" class="control-label" >Organisation contact email address</label>
                                        <input type="text" class="form-control" name="last_name" placeholder="" v-model="agent.email">
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label for="" class="control-label" >Proposal Type</label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="selected_application_id" @change="chainedSelectAppType(selected_application_id)">
											<option value="" selected disabled>Select proposal type</option>
                                            <option v-for="application_type in application_types" :value="application_type.value">
                                                {{ application_type.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-if="display_region_selectbox">
                                <label for="" class="control-label" >Region</label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="selected_region" @change="chainedSelectDistricts(selected_region)">
											<option value="" selected disabled>Select region</option>
                                            <option v-for="region in regions" :value="region.value">
                                                {{ region.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-if="display_region_selectbox && selected_region">
                                <label for="" class="control-label" >District</label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select  v-model="selected_district">
											<option value="" selected disabled>Select district</option>
                                            <option v-for="district in districts" :value="district.value">
                                                {{ district.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!--
                            <div v-if="activities.length > 0">
                                <label for="" class="control-label" >Activity</label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="selected_activity">
											<option value="" selected disabled>Select activity</option>
                                            <option v-for="activity in activities" :value="activity.value">
                                                {{ activity.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            -->

                            <div v-if="tenures.length > 0">
                                <label for="" class="control-label" >Tenure</label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="selected_tenure">
											<option value="" selected disabled>Select tenure</option>
                                            <option v-for="tenure in tenures" :value="tenure.value">
                                                {{ tenure.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="col-sm-12">
                                <button :disabled="isDisabled()" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
                             </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
import utils from './utils'
export default {
  data: function() {
    let vm = this;
    return {
        "proposal": null,
        agent: {},
        behalf_of: '',
        profile: {
            disturbance_organisations: []
        },
        "loading": [],
        form: null,
        pBody: 'pBody' + vm._uid,

        selected_application_id: '',
        selected_application_name: '',
        selected_region: '',
        selected_district: '',
        selected_activity: '',
        selected_tenure: '',
        application_types: [],
        regions: [],
        districts: [],
        activities: [],
        tenures: [],
        display_region_selectbox: false,
        /*

        application_types: [
            { text: 'Disturbance', value: 'Disturbance' },
            { text: 'Apiary', value: 'Apiary' }
        ],
        regions: [
            { text: 'Kimberley (Region)', value: 'Kimberley (Region)' },
            { text: 'East Kimberley (District)', value: 'East Kimberley (District)' },
            { text: 'West Kimberley (District)', value: 'West Kimberley (District)' },
            { text: 'Pilbara (Region)', value: 'Pilbara (Region)' }
        ],
        activities: [
            { text: 'Native Forest Silviculture and Timber Harvesting', value: 'NativeForestSilvicultureAndTimberHarvesting' },
            { text: 'Plantations', value: 'Plantations' },
            { text: 'Other Wood', value: 'OtherWood' }
        ],
        tenures: [
            { text: 'National park', value: 'National park' },
            { text: 'Nature reserve (class a19)', value: 'Nature reserve (class a19)' },
            { text: 'Conservation park', value: 'Conservation park' },
            { text: 'CALM Act section 5(1)g and 5(1)h reserve (class A20)', value: 'CALM Act section 5(1)g and 5(1)h reserve (class A20)' }
        ]
        */

    }
  },
  components: {
  },
  computed: {
    isLoading: function() {
      return this.loading.length > 0
    },
    org: function() {
        let vm = this;
        if (vm.behalf_of != '' || vm.behalf_of != 'other'){
            return vm.profile.disturbance_organisations.find(org => parseInt(org.id) === parseInt(vm.behalf_of)).name;
        }
        return '';
    },
    manyDistricts: function() {
      return this.districts.length > 1;
    }
  },
  methods: {
    submit: function() {
        let vm = this;
			
        swal({
            title: "Create " + vm.selected_application_name,
            text: "Are you sure you want to create " + this.alertText() + " proposal on behalf of "+vm.org+" ?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        }).then(() => {
         	vm.createProposal();
        },(error) => {
        });
    },
    alertText: function() {
        let vm = this;
		if (vm.selected_application_name == 'Disturbance') {
        	return "a disturbance";
		} else if (vm.selected_application_name == 'Apiary') {
        	return "an apiary";
		}
	},
    createProposal:function () {
        let vm = this;
		vm.$http.post('/api/proposal.json',{
			behalf_of: vm.behalf_of,
			application: vm.selected_application_id,
			region: vm.selected_region,
			district: vm.selected_district,
			activity: vm.selected_activity,
			tenure: vm.selected_tenure
		}).then(res => {
		    vm.proposal = res.body;
			vm.$router.push({
			    name:"draft_proposal",
				params:{proposal_id:vm.proposal.id}
			});
		},
		err => {
			console.log(err);
		});
    },
    isDisabled: function() {
        let vm = this;
        if (vm.selected_application_name == 'Disturbance') {
            //if (vm.behalf_of == '' || vm.selected_application_id == '' || vm.selected_region == '' || vm.selected_activity == '' || vm.selected_tenure == ''){
            if (vm.behalf_of == '' || vm.selected_application_id == '' || vm.selected_region == '' || vm.selected_tenure == ''){
	    		return true;
            }
        } else {
            if (vm.behalf_of == '' || vm.selected_application_id == ''){
	    		return true;
            }
        }
		return false;
    },
	fetchRegions: function(){
		let vm = this;

		vm.$http.get(api_endpoints.regions).then((response) => {
				vm.api_regions = response.body;
				//console.log('api_regions ' + response.body);

                for (var i = 0; i < vm.api_regions.length; i++) {
                    this.regions.push( {text: vm.api_regions[i].name, value: vm.api_regions[i].id, districts: vm.api_regions[i].districts} );
                }
				console.log('this.regions ' + vm.regions);
		},(error) => {
			console.log(error);
		})
	},

	searchList: function(id, search_list){
        /* Searches for dictionary in list */
        for (var i = 0; i < search_list.length; i++) {
            if (search_list[i].value == id) {
                return search_list[i];
            }
        }
        return [];
    },
	chainedSelectDistricts: function(region_id){
		let vm = this;
        vm.districts = [];

        var api_districts = this.searchList(region_id, vm.regions).districts;
        if (api_districts.length > 0) {
            for (var i = 0; i < api_districts.length; i++) {
                this.districts.push( {text: api_districts[i].name, value: api_districts[i].id} );
            }
        }
	},
    fetchApplicationTypes: function(){
		let vm = this;

		vm.$http.get(api_endpoints.application_types).then((response) => {
				vm.api_app_types = response.body;
				//console.log('api_app_types ' + response.body);

                for (var i = 0; i < vm.api_app_types.length; i++) {
                    this.application_types.push( {
                        text: vm.api_app_types[i].name, 
                        value: vm.api_app_types[i].id, 
                        //activities: (vm.api_app_types[i].activity_app_types.length > 0) ? vm.api_app_types[i].activity_app_types : [],
                        tenures: (vm.api_app_types[i].tenure_app_types.length > 0) ? vm.api_app_types[i].tenure_app_types : [],
                    } );
                }
				//console.log('this.application_types ' + vm.application_types);
		},(error) => {
			console.log(error);
		})
	},
    chainedSelectActivities: function(application_id){
		let vm = this;
        vm.activities = [];
        var api_activities = this.searchList(application_id, vm.application_types).activities;
        //var api_activities = vm.application_types[region_id-1].districts
        for (var i = 0; i < api_activities.length; i++) {
            this.activities.push( {text: api_activities[i].name, value: api_activities[i].id} );
        }
	},
    chainedSelectTenures: function(application_id){
		let vm = this;
        vm.tenures = [];
        var api_tenures = this.searchList(application_id, vm.application_types).tenures;
        for (var i = 0; i < api_tenures.length; i++) {
            this.tenures.push( {text: api_tenures[i].name, value: api_tenures[i].id} );
        }
	},
    chainedSelectAppType: function(application_id){
        /* reset */
		let vm = this;
        vm.selected_region = '';
        vm.selected_district = '';
        vm.selected_activity = '';
        vm.selected_tenure = '';
        vm.display_region_selectbox = false;

        vm.selected_application_name = this.searchList(application_id, vm.application_types).text
        //this.chainedSelectActivities(application_id);
        this.chainedSelectTenures(application_id);

        if (vm.selected_application_name == 'Disturbance') {
            vm.display_region_selectbox = true;
        } 

    }



  },
  mounted: function() {
    let vm = this;
    vm.fetchRegions();
    vm.fetchApplicationTypes();
    vm.form = document.forms.new_proposal;
  },
  beforeRouteEnter: function(to, from, next) {
    let initialisers = [
        utils.fetchProfile(),
        //utils.fetchProposal(to.params.proposal_id)
    ]
    next(vm => {
        Promise.all(initialisers).then(data => {
            vm.profile = data[0];
            //vm.proposal = data[1];
        })
    })
  }
}
</script>

<style lang="css">
input[type=text], select{
    width:40%;
    box-sizing:border-box;

    min-height: 34px;
    padding: 0;
    height: auto;
}
</style>
