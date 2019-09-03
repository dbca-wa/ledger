<template lang="html">
    <div>
        <!-- <div class="col-md-3" >
            <div class="panel panel-default fixed">
              <div class="panel-heading">
                <h5>Sections</h5>
              </div>
              <div class="panel-body" style="padding:0">
                  <ul class="list-group" id="scrollspy-section" style="margin-bottom:0">

                  </ul>
              </div>
            </div>
        </div> -->

        <div class="col-md-12">
            <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
              <li class="nav-item">
                <a class="nav-link active" id="pills-applicant-tab" data-toggle="pill" href="#pills-applicant" role="tab" aria-controls="pills-applicant" aria-selected="true">
                  1. Applicant
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-activities-land-tab" data-toggle="pill" href="#pills-activities-land" role="tab" aria-controls="pills-activities-land" aria-selected="false">
                  2. Activities (land)
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-activities-marine-tab" data-toggle="pill" href="#pills-activities-marine" role="tab" aria-controls="pills-activities-marine" aria-selected="false">
                  3. Activities (marine)
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-other-details-tab" data-toggle="pill" href="#pills-other-details" role="tab" aria-controls="pills-other-details" aria-selected="false">
                  4. Other Details
                </a>
              </li>
              <li v-if="is_external" class="nav-item" id="li-training">
                <a class="nav-link" id="pills-online-training-tab" data-toggle="pill" href="#pills-online-training" role="tab" aria-controls="pills-online-training" aria-selected="false">
                  5. Questionnaire
                </a>
              </li>
              <li v-if="is_external" class="nav-item" id="li-payment">
                <a class="nav-link disabled" id="pills-payment-tab" data-toggle="pill" href="" role="tab" aria-controls="pills-payment" aria-selected="false">
                  6. Payment
                </a>
              </li>
              <li v-if="is_external" class="nav-item" id="li-confirm">
                <a class="nav-link disabled" id="pills-confirm-tab" data-toggle="pill" href="" role="tab" aria-controls="pills-confirm" aria-selected="false">
                    7. Confirmation
                </a>
              </li>
            </ul>
            <div class="tab-content" id="pills-tabContent">
              <!-- <div class="tab-pane fade show active" id="pills-applicant" role="tabpanel" aria-labelledby="pills-applicant-tab">  -->
              <div class="tab-pane fade" id="pills-applicant" role="tabpanel" aria-labelledby="pills-applicant-tab">
                  <div v-if="is_external">
                    <Profile :isApplication="true" v-if="applicantType == 'SUB'" ref="profile"></Profile>
              
                    <Organisation :org_id="proposal.org_applicant" :isApplication="true" v-if="applicantType == 'ORG'" ref="organisation"></Organisation> 
                  </div>
                  <div v-else>
                    <Applicant :proposal="proposal" id="proposalStartApplicant"></Applicant>
                    <div v-if="is_internal">
                      <Assessment :proposal="proposal" :assessment="proposal.assessor_assessment" :hasAssessorMode="hasAssessorMode" :is_internal="is_internal" :is_referral="is_referral"></Assessment>
                      <div v-for="assess in proposal.referral_assessments">
                        <Assessment :proposal="proposal" :assessment="assess"></Assessment>
                      </div>
                    </div>
                    <div v-if="is_referral">
                    <!-- <Assessment :proposal="proposal" :assessment="referral.referral_assessment" :hasReferralMode="hasReferralMode" :is_internal="is_internal" :is_referral="is_referral"></Assessment> -->
                    </div>
                    

                  </div>
              </div>
              <div class="tab-pane fade" id="pills-activities-land" role="tabpanel" aria-labelledby="pills-activities-land-tab">

                <!--
				<div class="row">
                  <div class="col-md-6">
                    <div class="row">
                      <div class="panel panel-default">
                        <div class="panel-heading">
                          Panel 1
                        </div>
                        <ActivitiesLand :proposal="proposal" id="proposalStartActivitiesLand1" :canEditActivities="canEditActivities" ref="activities_land"></ActivitiesLand>
                      </div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <div class="row">
                      <div class="panel panel-default">
                        <div class="panel-heading">
                          Panel 2
                        </div>
                        <ActivitiesLand :proposal="proposal" id="proposalStartActivitiesLand2" :canEditActivities="canEditActivities" ref="activities_land2"></ActivitiesLand>
                      </div>
                    </div>
                  </div>
                </div>
                -->

                <ActivitiesLand :proposal="proposal" id="proposalStartActivitiesLand" :canEditActivities="canEditActivities" ref="activities_land"></ActivitiesLand>
              </div>
              <div class="tab-pane fade" id="pills-activities-marine" role="tabpanel" aria-labelledby="pills-activities-marine-tab">
                <ActivitiesMarine :proposal="proposal" id="proposalStartActivitiesMarine" :canEditActivities="canEditActivities" ref="activities_marine"></ActivitiesMarine>
              </div>
              <div class="tab-pane fade" id="pills-other-details" role="tabpanel" aria-labelledby="pills-other-details-tab">
                <OtherDetails :proposal="proposal" id="proposalStartOtherDetails" ref="other_details"></OtherDetails>
              </div>
              <div class="tab-pane fade" id="pills-online-training" role="tabpanel" aria-labelledby="pills-online-training-tab">
                <OnlineTraining :proposal="proposal" id="proposalStartOnlineTraining"></OnlineTraining>
              </div>
              <div class="tab-pane fade" id="pills-payment" role="tabpanel" aria-labelledby="pills-payment-tab">
                <!-- This is a Dummy Tab -->
              </div>
              <div class="tab-pane fade" id="pills-confirm" role="tabpanel" aria-labelledby="pills-confirm-tab">
                <Confirmation :proposal="proposal" id="proposalStartConfirmation"></Confirmation>
              </div>
            </div>
        </div>
    </div>
</template>

<script>
    import Profile from '@/components/user/profile.vue'
    import Organisation from '@/components/external/organisations/manage.vue'
    import Applicant from '@/components/common/tclass/applicant.vue'
    import Assessment from '@/components/common/tclass/assessment.vue'
    //import ActivitiesLand from '@/components/common/tclass/treeview.vue'
    import ActivitiesLand from '@/components/common/tclass/activities_land.vue'
    import ActivitiesMarine from '@/components/common/tclass/activities_marine.vue'
    import OtherDetails from '@/components/common/tclass/other_details.vue'
    import OnlineTraining from '@/components/common/tclass/online_training.vue'
    //import ApplicationFee from '@/components/common/tclass/application_fee.vue'
    //import Confirmation from '@/components/common/tclass/confirmation.vue'
    import Confirmation from '@/components/common/tclass/confirmation.vue'
    export default {
        props:{
            proposal:{
                type: Object,
                required:true
            },
            canEditActivities:{
              type: Boolean,
              default: true
            },
            is_external:{
              type: Boolean,
              default: false
            },
            is_internal:{
              type: Boolean,
              default: false
            },
            is_referral:{
              type: Boolean,
              default: false
            },
            hasReferralMode:{
                type:Boolean,
                default: false
            },
            hasAssessorMode:{
                type:Boolean,
                default: false
            },
            referral:{
                type: Object,
                required:false
            },
        },
        data:function () {
            return{
                values:null
            }
        },
        components: {
            Applicant,
            ActivitiesLand,
            ActivitiesMarine,
            OtherDetails,
            OnlineTraining,
            //ApplicationFee,
            Confirmation,
            Profile,
            Organisation,
            Assessment
        },
        computed:{
          applicantType: function(){
            return this.proposal.applicant_type;
        },
        },
        methods:{
            set_tabs:function(){
                let vm = this;

                /* set Applicant tab Active */
                $('#pills-tab a[href="#pills-applicant"]').tab('show');

                if (vm.proposal.fee_paid) {
                    /* Online Training tab */
                    $('#pills-online-training-tab').attr('style', 'background-color:#E5E8E8 !important; color: #99A3A4;');
                    $('#li-training').attr('class', 'nav-item disabled');
                    $('#pills-online-training-tab').attr("href", "")
                }

                if (!vm.proposal.training_completed) {
                    /* Payment tab  (this is enabled after online_training is completed - in online_training.vue)*/
                    $('#pills-payment-tab').attr('style', 'background-color:#E5E8E8 !important; color: #99A3A4;');
                    $('#li-payment').attr('class', 'nav-item disabled');
                }

                /* Confirmation tab - Always Disabled */
                $('#pills-confirm-tab').attr('style', 'background-color:#E5E8E8 !important; color: #99A3A4;');
                $('#li-confirm').attr('class', 'nav-item disabled');
            },
            eventListener: function(){
              let vm=this;
              $('a[href="#pills-activities-land"]').on('shown.bs.tab', function (e) {
                vm.$refs.activities_land.$refs.vehicles_table.$refs.vehicle_datatable.vmDataTable.columns.adjust().responsive.recalc();
              });
              $('a[href="#pills-activities-marine"]').on('shown.bs.tab', function (e) {
                vm.$refs.activities_marine.$refs.vessel_table.$refs.vessel_datatable.vmDataTable.columns.adjust().responsive.recalc();
              });
            },

        },
        mounted: function() {
            let vm = this;
            vm.set_tabs();
            vm.form = document.forms.new_proposal;
            vm.eventListener();
            //window.addEventListener('beforeunload', vm.leaving);
            //indow.addEventListener('onblur', vm.leaving);

        }
 
    }
</script>

<style lang="css" scoped>
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }

    .nav-item {
        background-color: rgb(200,200,200,0.8) !important;
        margin-bottom: 2px;
    }

    .nav-item>li>a {
        background-color: yellow !important;
        color: #fff;
    }

    .nav-item>li.active>a, .nav-item>li.active>a:hover, .nav-item>li.active>a:focus {
      color: white;
      background-color: blue;
      border: 1px solid #888888;
    }

	.admin > div {
	  display: inline-block;
	  vertical-align: top;
	  margin-right: 1em;
	}
</style>

