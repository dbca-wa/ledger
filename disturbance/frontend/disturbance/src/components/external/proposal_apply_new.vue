<template lang="html">
    <div class="" >
        <div class="">
            <!-- <div class="col-sm-3"></div> -->
            <div class="">
                <form class="form-horizontal" name="personal_form" method="post">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Region, District, Activity Type, Sub Activity, ...
                                <a :href="'#'+pBody2" data-toggle="collapse"  data-parent="#userInfo2" expanded="true" :aria-controls="pBody2">
                                    <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                                </a>
                            </h3>
                        </div>
                        <div class="panel-body collapse in" :id="pBody2">
                            <div v-if="proposal">
                                <label for="" class="control-label" >Region * <a :href="region_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a> </label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="proposal.region" class="form-control" style="width:40%" @change="chainedSelectDistricts(proposal.region)" :disabled="proposal.readonly">
											<option value="" selected disabled>Select region</option>
                                            <option v-for="region in regions" :value="region.value">
                                                {{ region.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div> 

                            <div v-if="proposal.region">
                                <label for="" class="control-label" style="font-weight: normal;">District <a :href="district_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select  v-model="proposal.district" class="form-control" style="width:40%" :disabled="proposal.readonly">
											<option value="" selected disabled>Select district</option>
                                            <option v-for="district in districts" :value="district.value">
                                                {{ district.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-if="display_activity_matrix_selectbox">
								<div v-if="activities.length > 0">
									<label for="" class="control-label" >Activity Type * <a :href="activity_type_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
									<div class="col-sm-12">
										<div class="form-group">
											<select v-model="proposal.activity" @change="chainedSelectSubActivities1(proposal.activity)" class="form-control" style="width:40%" :disabled="proposal.readonly">
												<option value="" selected disabled>Select activity</option>
												<option v-for="activity in activities" :value="activity.value">
													{{ activity.text }}
												</option>
											</select>
										</div>
									</div>
								</div>

								<div v-if="sub_activities1.length > 0">
									<label for="" class="control-label" >Sub Activity 1 * <a :href="sub_activity_1_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
									<div class="col-sm-12">
										<div class="form-group">
											<select v-model="proposal.sub_activity_level1" @change="chainedSelectSubActivities2(proposal.sub_activity_level1)" class="form-control" style="width:40%" :disabled="proposal.readonly">
												<option value="" selected disabled>Select sub_activity 1</option>
												<option v-for="sub_activity1 in sub_activities1" :value="sub_activity1.value">
													{{ sub_activity1.text }}
												</option>
											</select>
										</div>
									</div>
								</div>

								<div v-if="sub_activities2.length > 0">
									<label for="" class="control-label" >Sub Activity 2 * <a :href="sub_activity_2_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
									<div class="col-sm-12">
										<div class="form-group">
											<select v-model="proposal.sub_activity_level2" @change="chainedSelectCategories(proposal.sub_activity_level2)" class="form-control" style="width:40%" :disabled="proposal.readonly">
												<option value="" selected disabled>Select sub_activity 2</option>
												<option v-for="sub_activity2 in sub_activities2" :value="sub_activity2.value">
													{{ sub_activity2.text }}
												</option>
											</select>
										</div>
									</div>
								</div>

								<div v-if="categories.length > 0">
									<label for="" class="control-label" >Category * <a :href="category_help_url" target="_blank"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a></label>
									<div class="col-sm-12">
										<div class="form-group">
											<select v-model="proposal.management_area" @change="get_approval_level(proposal.management_area)" class="form-control" style="width:40%" :disabled="proposal.readonly">
												<option value="" selected disabled>Select category</option>
												<option v-for="category in categories" :value="category.value" :name="category.approval">
													{{ category.text }}
												</option>
											</select>
										</div>
									</div>
								</div>
                            </div>
                        </div>
                    </div>

                    <!-- <div class="col-sm-12">
                        <button v-if="!creatingProposal" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
                        <button v-else disabled class="pull-right btn btn-primary"><i class="fa fa-spin fa-spinner"></i>&nbsp;Creating</button>
                    </div> -->
                  </div>
                </form>
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
    name:'new-apply',
    props:{
            proposal:{
                type:Object,
            },
    },
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
        pBody2: 'pBody2' + vm._uid,

        selected_application_id: '',
        selected_application_name: '',
        selected_region: '',
        selected_district: '',
        application_types: [],
        selected_activity: '',
        selected_sub_activity1: '',
        selected_sub_activity2: '',
        selected_category: '',
        regions: [],
        districts: [],
        activity_matrix: [],
        activities: [],
        sub_activities1: [],
        sub_activities2: [],
        categories: [],
        approval_level: '',
        creatingProposal: false,
        display_region_selectbox: false,
        display_activity_matrix_selectbox: false,
        site_url: (api_endpoints.site_url.endsWith("/")) ? (api_endpoints.site_url): (api_endpoints.site_url + "/"),
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
    },
    proposal_type_help_url: function() {
      return this.site_url + "help/disturbance/user/#apply_proposal_type"
    },
    region_help_url: function() {
      return this.site_url + "help/disturbance/user/#apply_region"
    },
    district_help_url: function() {
      return this.site_url + "help/disturbance/user/#apply_district"
    },
    activity_type_help_url: function() {
      return this.site_url + "help/disturbance/user/#apply_activity_type"
    },
    sub_activity_1_help_url: function() {
      return this.site_url + "help/disturbance/user/#apply_sub_activity_1"
    },
    sub_activity_2_help_url: function() {
      return this.site_url + "help/disturbance/user/#apply_sub_activity_2"
    },
    category_help_url: function() {
      return this.site_url + "help/disturbance/user/#apply_category"
    }

  },
  methods: {
    submit: function() {
        let vm = this;
			
        swal({
            title: "Create ",
            text: "Are you sure you want to create ",
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
		if (vm.selected_application_name == 'Apiary') {
        	return "an " + vm.selected_application_name.toLowerCase();
		} else {
        	return "a " + vm.selected_application_name.toLowerCase();
		}
	},
    createProposal:function () {
        let vm = this;
        vm.creatingProposal = true;
		vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,vm.proposal.id+'/update_region_section'),{
			region: vm.selected_region,
			district: vm.selected_district,
			activity: vm.selected_activity,
            sub_activity1: vm.selected_sub_activity1,
            sub_activity2: vm.selected_sub_activity2,
            category: vm.selected_category,
            approval_level: vm.approval_level
		}).then(res => {
		    vm.proposal = res.body;
			// vm.$router.push({
			//     name:"draft_proposal",
			// 	params:{proposal_id:vm.proposal.id}
			// });
            vm.creatingProposal = false;
		},
		err => {
			console.log(err);
		});
    },
    isDisabled: function() {
        let vm = this;

        if (vm.selected_application_name != 'Apiary') {
            if (vm.behalf_of == '' || vm.selected_application_id == '' || vm.selected_region == '' || vm.approval_level == ''){
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
                vm.setProposalData2(this.regions);
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
    chainedSelectDistricts2: function(region_id, regions){
        let vm = this;
        vm.districts = [];

        var api_districts = this.searchList(region_id, regions).districts;
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
                        //tenures: (vm.api_app_types[i].tenure_app_types.length > 0) ? vm.api_app_types[i].tenure_app_types : [],
                    } );
                }
		},(error) => {
			console.log(error);
		})
	},
    chainedSelectAppType: function(application_id){
        /* reset */
		let vm = this;
        vm.selected_region = '';
        vm.selected_district = '';
        vm.selected_activity = '';
        vm.display_region_selectbox = false;
        vm.display_activity_matrix_selectbox = false;

        vm.selected_application_name = this.searchList(application_id, vm.application_types).text
        //this.chainedSelectActivities(application_id);
        //this.chainedSelectActivities(application_id);

        if (vm.selected_application_name == 'Apiary') {
            vm.display_region_selectbox = false;
            vm.display_activity_matrix_selectbox = false;
        }  else {
            vm.display_region_selectbox = true;
            vm.display_activity_matrix_selectbox = true;
        }

    },

	fetchActivityMatrix: function(){
		let vm = this;
        vm.sub_activities1 = [];
        vm.sub_activities2 = [];
        vm.categories = [];
        vm.approval_level = '';

		vm.$http.get(api_endpoints.activity_matrix).then((response) => {
				this.activity_matrix = response.body[0].schema[0];
				this.keys_ordered = response.body[0].ordered;
				//console.log('this.activity_matrix ' + response.body[0].schema);

                var keys = this.keys_ordered ? Object.keys(this.activity_matrix).sort() : Object.keys(this.activity_matrix)
                for (var i = 0; i < keys.length; i++) {
                    this.activities.push( {text: keys[i], value: keys[i]} );
                }
		},(error) => {
			console.log(error);
		})
	},
    chainedSelectSubActivities1: function(activity_name){
		let vm = this;
        vm.sub_activities1 = [];
        vm.sub_activities2 = [];
        vm.categories = [];
        vm.selected_sub_activity1 = '';
        vm.selected_sub_activity2 = '';
        vm.selected_category = '';
        vm.approval_level = '';

        vm.sub_activities1 = [];
        var [api_activities, res] = this.get_sub_matrix(activity_name, vm.activity_matrix)
        if (res == "null" || res == null) {
            //for (var i = 0; i < vm.activity_matrix.length; i++) {
            //    if (activity_name == vm.activity_matrix[i]['text']) {
            //        vm.activity_matrix[i]['sub_matrix']
            //    }
            //}
            vm.proposal.approval_level = api_activities;
            return;
        } else if (res == "pass") {
            var api_sub_activities = this.get_sub_matrix("pass", api_activities[0])[0];
            if ("pass" in api_sub_activities[0]) {
                // go straight to categories widget
                var categories = api_sub_activities[0]['pass']
                for (var i = 0; i < categories.length; i++) {
                    this.categories.push( {text: categories[i][0], value: categories[i][0], approval: categories[i][1]} );
                }

            } else {
                // go to sub_activity2 widget
                for (var i = 0; i < api_sub_activities.length; i++) {
                    var key = Object.keys(api_activities[i])[0];
                    this.sub_activities1.push( {text: key, value: key, sub_matrix: api_activities[i][key]} );
                }
            }
        } else {
            for (var i = 0; i < api_activities.length; i++) {
                var key = Object.keys(api_activities[i])[0];
                this.sub_activities1.push( {text: key, value: key, sub_matrix: api_activities[i][key]} );
            }
        }
	},

    chainedSelectSubActivities2: function(activity_name){
		let vm = this;
        vm.sub_activities2 = [];
        vm.categories = [];
        vm.selected_sub_activity2 = '';
        vm.selected_category = '';
        vm.approval_level = '';

        //var api_activities = this.get_sub_matrix(activity_name, vm.sub_activities1[0]['text'])
        var [api_activities, res] = this.get_sub_matrix(activity_name, vm.sub_activities1)
        if (res == "null" || res == null) {
            vm.proposal.approval_level = api_activities;
            return;
        } else if (res == "pass") {
            for (var i = 0; i < api_activities.length; i++) {
                this.categories.push( {text: api_activities[i][0], value: api_activities[i][0], approval: api_activities[i][1]} );
            }
        } else {
            for (var i = 0; i < vm.sub_activities1.length; i++) {
                if (activity_name == vm.sub_activities1[i]['text']) {
                    var api_activities2 = vm.sub_activities1[i]['sub_matrix'];
                    for (var j = 0; j < api_activities2.length; j++) {
                        var key = Object.keys(api_activities2[j])[0];
                        this.sub_activities2.push( {text: key, value: key, sub_matrix: api_activities2[j][key]} );
                    }
                }
            }
        }
	},
    chainedSelectCategories: function(activity_name){
		let vm = this;
        vm.categories = [];
        vm.selected_category = '';
        vm.approval_level = '';

        for (var i = 0; i < vm.sub_activities2.length; i++) {
            if (activity_name == vm.sub_activities2[i]['text']) {
                var api_categories = vm.sub_activities2[i]['sub_matrix'];
                for (var j = 0; j < api_categories.length; j++) {
                    this.categories.push( {text: api_categories[j][0], value: api_categories[j][0], approval: api_categories[j][1]} );
                }
            }
        }
	},

    get_sub_matrix: function(activity_name, sub_activities){
        // this.sub_activities1[0]['text']
        if (activity_name in sub_activities) {
            if (sub_activities[activity_name].length > 0) {
                if ('pass' in sub_activities[activity_name][0]) {
                    return [sub_activities[activity_name], "pass"];

                } else if ('null' in sub_activities[activity_name][0]) {
                    if (sub_activities[activity_name]['sub_matrix'] == null) {
                        var approval_level = sub_activities[activity_name][0]['null'][0][0];
                    } else {
                        var approval_level = sub_activities[activity_name]['sub_matrix'][0]['null'][0];
                    }
                    return [approval_level, "null"];
                    //return [sub_activities[activity_name], "null"];
                }
            }
           
            // not a sub_matrix --> this is the main activity_matrix data (as provided by the REST API)
            return [sub_activities[activity_name], true];
        }
        for (var i = 0; i < sub_activities.length; i++) {
            if (activity_name == sub_activities[i]['text']) {
                var key_sub_matrix = Object.keys(sub_activities[i]['sub_matrix'][0])[0];
                if (key_sub_matrix == "null") {
                    var approval_level = sub_activities[i]['sub_matrix'][0]['null'][0];
                    return [approval_level, null]
                } else if (key_sub_matrix == "pass") {
                    return [sub_activities[i]['sub_matrix'][0]['pass'], "pass"]
                } else {
                    return [sub_activities[i]['sub_matrix'][0], true];
                }
            }
        }
    },
    get_approval_level: function(category_name) {
        let vm = this;
        for (var i = 0; i < vm.categories.length; i++) {
            if (category_name == vm.categories[i]['text']) {
                vm.proposal.approval_level = vm.categories[i]['approval'];
            }
        }
        
    },
    setProposalData: function(regions){
        let vm=this;
        //console.log("here", vm.proposal)
        if(vm.proposal){
            //vm.chainedSelectAppType(vm.proposal.application_type)
            vm.selected_application_name=vm.proposal.application_type;
            if (vm.selected_application_name == 'Apiary') {
                vm.display_region_selectbox = false;
                vm.display_activity_matrix_selectbox = false;
            }  else {
                vm.display_region_selectbox = true;
                vm.display_activity_matrix_selectbox = true;
            }
            vm.selected_region=vm.proposal.region;
            vm.selected_district=vm.proposal.district;
            vm.selected_activity=vm.proposal.activity;
            // vm.selected_sub_activity1=vm.proposal.data[0]["regionActivitySection"][0]["Sub-activity level 1"]
            vm.chainedSelectDistricts2(vm.selected_region, regions);
            vm.chainedSelectSubActivities1(vm.selected_activity);
            //vm.selected_sub_activity1=vm.proposal.data[0]["regionActivitySection"][0]["Sub-activity level 1"]
            vm.selected_sub_activity1=vm.proposal.sub_activity_level1;
            vm.chainedSelectSubActivities2(vm.selected_sub_activity1);
            //vm.selected_sub_activity2=vm.proposal.data[0]["regionActivitySection"][0]["Sub-activity level 2"]
            vm.selected_sub_activity2=vm.proposal.sub_activity_level2;
            if(vm.selected_sub_activity2!=""){
                chainedSelectCategories(vm.selected_sub_activity2);
            }
            //vm.selected_category= vm.proposal.data[0]["regionActivitySection"][0]["Management area"]
            vm.selected_category= vm.proposal.management_area;
            vm.approval_level= vm.proposal.approval_level;
        }
    },
    setProposalData2: function(regions){
        let vm=this;
        if(vm.proposal){
            vm.selected_application_name=vm.proposal.application_type;
            if (vm.selected_application_name == 'Apiary') {
                vm.display_region_selectbox = false;
                vm.display_activity_matrix_selectbox = false;
            }  else {
                vm.display_region_selectbox = true;
                vm.display_activity_matrix_selectbox = true;
            }
            
            vm.chainedSelectDistricts2(vm.proposal.region, regions);
            vm.chainedSelectSubActivities1(vm.proposal.activity);
            if(vm.proposal.sub_activity_level1!="" && vm.proposal.sub_activity_level1!=null){
            vm.chainedSelectSubActivities2(vm.proposal.sub_activity_level1);
            }
            if(vm.proposal.sub_activity_level2!="" && vm.proposal.sub_activity_level2!=null){
                chainedSelectCategories(vm.proposal.sub_activity_level2);
            }
        }
    }


  },
  mounted: function() {
    let vm = this;
    vm.fetchRegions();
    vm.fetchApplicationTypes();
    vm.fetchActivityMatrix();
    vm.form = document.forms.new_proposal;
  },
  
  beforeRouteEnter: function(to, from, next) {

    let initialisers = [
        utils.fetchProfile(),
        
    ]
    next(vm => {
        vm.loading.push('fetching profile')
        Promise.all(initialisers).then(data => {
            vm.profile = data[0];
            //vm.proposal = data[1];
            vm.loading.splice('fetching profile', 1)
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

.group-box {
	border-style: solid;
	border-width: thin;
	border-color: #FFFFFF;
}
</style>
