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
                <a class="nav-link" id="pills-activity-tab" data-toggle="pill" href="#pills-activity" role="tab" aria-controls="pills-activity" aria-selected="false">
                  2. Activity
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-access-tab" data-toggle="pill" href="#pills-access" role="tab" aria-controls="pills-access" aria-selected="false">
                  3. Access
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-equipment-tab" data-toggle="pill" href="#pills-equipment" role="tab" aria-controls="pills-equipment" aria-selected="false">
                  4. Equipment
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
              <div class="tab-pane fade" id="pills-activity" role="tabpanel" aria-labelledby="pills-activity-tab">
                <Activity :proposal="proposal" id="proposalStartActivity"></Activity>
              </div>
              <div class="tab-pane fade" id="pills-access" role="tabpanel" aria-labelledby="pills-access-tab">
                <Access :proposal="proposal" id="proposalStartAccess"></Access>
              </div>
              <div class="tab-pane fade" id="pills-equipment" role="tabpanel" aria-labelledby="pills-equipment-tab">
                <Equipment :proposal="proposal" id="proposalStartEquipment"></Equipment>
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
    import Applicant from '@/components/common/filming/applicant.vue'
    import Activity from '@/components/common/filming/activity.vue'
    import Access from '@/components/common/filming/access.vue'
    import Equipment from '@/components/common/filming/equipment.vue'
    import OtherDetails from '@/components/common/filming/other_details.vue'
    import OnlineTraining from '@/components/common/filming/online_training.vue'
    import Payment from '@/components/common/filming/payment.vue'
    import Confirmation from '@/components/common/filming/confirmation.vue'
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
            Activity,
            Access,
            Equipment,
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

