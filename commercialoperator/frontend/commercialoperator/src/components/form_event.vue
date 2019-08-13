<template lang="html">
    <div>
        <div class="col-md-3" >
            <div class="panel panel-default fixed">
              <div class="panel-heading">
                <h5>Sections</h5>
              </div>
              <div class="panel-body" style="padding:0">
                  <ul class="list-group" id="scrollspy-section" style="margin-bottom:0">

                  </ul>
              </div>
            </div>
        </div>

        <div class="col-md-9">
            <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
              <li class="nav-item">
                <a class="nav-link active" id="pills-applicant-tab" data-toggle="pill" href="#pills-applicant" role="tab" aria-controls="pills-applicant" aria-selected="true">
                  1. Applicant
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-activities-tab" data-toggle="pill" href="#pills-activities" role="tab" aria-controls="pills-activities" aria-selected="false">
                  2. Activities
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-event-management-tab" data-toggle="pill" href="#pills-event-management" role="tab" aria-controls="pills-event-management" aria-selected="false">
                  3. Event Management
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-vehicles-vessels-tab" data-toggle="pill" href="#pills-vehicles-vessels" role="tab" aria-controls="pills-vehicles-vessels" aria-selected="false">
                  4. Vehicles/Vessels
                </a>
              </li>

              <li class="nav-item">
                <a class="nav-link" id="pills-other-details-tab" data-toggle="pill" href="#pills-other-details" role="tab" aria-controls="pills-other-details" aria-selected="false">
                  5. Other Details
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-online-training-tab" data-toggle="pill" href="#pills-online-training" role="tab" aria-controls="pills-online-training" aria-selected="false">
                  6. Online Training
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-payment-tab" data-toggle="pill" href="#pills-payment" role="tab" aria-controls="pills-payment" aria-selected="false">
                  7. Payment
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-confirm-tab" data-toggle="pill" href="#pills-confirm" role="tab" aria-controls="pills-confirm" aria-selected="false">
                  8. Confirmation
                </a>
              </li>

            </ul>
            <div class="tab-content" id="pills-tabContent">
              <div class="tab-pane fade show active" id="pills-applicant" role="tabpanel" aria-labelledby="pills-applicant-tab"> 
                <Applicant :proposal="proposal" id="proposalStartApplicant"></Applicant>
              </div>
              <div class="tab-pane fade" id="pills-activities" role="tabpanel" aria-labelledby="pills-activities-tab">
                <Activities :proposal="proposal" id="proposalStartActivities"></Activities>
              </div>
              <div class="tab-pane fade" id="pills-event-management" role="tabpanel" aria-labelledby="pills-event-management-tab">
                <EventManagement :proposal="proposal" id="proposalStartEventManagement"></EventManagement>
              </div>
              <div class="tab-pane fade" id="pills-vehicles-vessels" role="tabpanel" aria-labelledby="pills-vehicles-vessels-tab">
                <VehiclesVessels :proposal="proposal" id="proposalStartVehiclesVessels"></VehiclesVessels>
              </div>
              <div class="tab-pane fade" id="pills-other-details" role="tabpanel" aria-labelledby="pills-other-details-tab">
                <OtherDetails :proposal="proposal" id="proposalStartOtherDetails"></OtherDetails>
              </div>
              <div class="tab-pane fade" id="pills-online-training" role="tabpanel" aria-labelledby="pills-online-training-tab">
                <OnlineTraining :proposal="proposal" id="proposalStartOnlineTraining"></OnlineTraining>
              </div>
              <div class="tab-pane fade" id="pills-payment" role="tabpanel" aria-labelledby="pills-payment-tab">
                <Payment :proposal="proposal" id="proposalStartPayment"></Payment>
              </div>
              <div class="tab-pane fade" id="pills-confirm" role="tabpanel" aria-labelledby="pills-confirm-tab">
                <Confirmation :proposal="proposal" id="proposalStartConfirmation"></Confirmation>
              </div>
            </div>
        </div>
    </div>
</template>

<script>
    import Applicant from '@/components/common/event/applicant.vue'
    import Activities from '@/components/common/event/activities.vue'
    import EventManagement from '@/components/common/event/event_management.vue'
    import VehiclesVessels from '@/components/common/event/vehicles_vessels.vue'
    import OtherDetails from '@/components/common/event/other_details.vue'
    import OnlineTraining from '@/components/common/event/online_training.vue'
    import Payment from '@/components/common/event/payment.vue'
    import Confirmation from '@/components/common/event/confirmation.vue'
    export default {
        props:{
            proposal:{
                type: Object,
                required:true
            },
            withSectionsSelector:{
                type: Boolean,
                default: true
            },
            form_width: {
                type: String,
                default: 'col-md-9'
            }
        },
        data:function () {
            return{
                values:null
            }
        },
        components: {
            Applicant,
            Activities,
            EventManagement,
            VehiclesVessels,
            OtherDetails,
            OnlineTraining,
            Payment,
            Confirmation
        },
        methods:{
        },
        mounted: function() {
            let vm = this;
            $('#pills-tab a[href="#pills-applicant"]').tab('show');
            vm.form = document.forms.new_proposal;
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

</style>

