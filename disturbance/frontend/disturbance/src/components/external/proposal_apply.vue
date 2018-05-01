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
                                        <select v-model="selected_application_type">
											<option value="" selected>Select proposal type</option>
                                            <option v-for="application_type in application_types" :value="application_type.value">
                                                {{ application_type.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label for="" class="control-label" >Region</label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="selected_region">
											<option value="" selected>Select region</option>
                                            <option v-for="region in regions" :value="region.value">
                                                {{ region.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label for="" class="control-label" >Activity</label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="selected_activity">
											<option value="" selected>Select activity</option>
                                            <option v-for="activity in activities" :value="activity.value">
                                                {{ activity.text }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label for="" class="control-label" >Tenure</label>
                                <div class="col-sm-12">
                                    <div class="form-group">
                                        <select v-model="selected_tenure">
											<option value="" selected>Select tenure</option>
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

        selected_application_type: '',
        selected_region: '',
        selected_activity: '',
        selected_tenure: '',
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
    }
  },
  methods: {
    submit: function() {
        let vm = this;
			
        swal({
            title: "Create " + vm.selected_application_type,
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
		if (vm.selected_application_type == 'Disturbance') {
        	return "a disturbance";
		} else if (vm.selected_application_type == 'Apiary') {
        	return "an apiary";
		}
	},
    createProposal:function () {
        let vm = this;
		vm.$http.post('/api/proposal.json',{
			behalf_of: vm.behalf_of,
			application_name: vm.selected_application_type,
			region: vm.selected_region,
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
        if (vm.behalf_of == '' || vm.selected_application_type == '' || vm.selected_region == '' || vm.selected_activity == '' || vm.selected_tenure == ''){
			return true;
        }
		return false;
    },
	fetchRegions: function(){
		let vm = this;
		//vm.$http.get('/api/region/').then((response) => {
		vm.$http.get('/api/region/').then(response => response.json())
			.then(json => {
			//next(vm => {
			//	this.api_regions = response.body;
			//	console.log('api_regions ' + response.body);
			//})
				this.api_regions = response.body;
				console.log('api_regions ' + response.body);
		},(error) => {
			console.log(error);
		})
	}

  },
  mounted: function() {
    let vm = this;
	vm.fetchRegions();
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
}
</style>
