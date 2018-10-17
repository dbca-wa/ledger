<template lang="html">
    <div>
        <div id="scrollspy-heading" class="col-lg-12" >
            <h4>Commercial Operator - {{proposal.application_type}} application: {{proposal.lodgement_number}}</h4>
        </div>

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
              <li class="nav-item">
                <a class="nav-link" id="pills-online-training-tab" data-toggle="pill" href="#pills-online-training" role="tab" aria-controls="pills-online-training" aria-selected="false">
                  5. Online Training
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-payment-tab" data-toggle="pill" href="#pills-payment" role="tab" aria-controls="pills-payment" aria-selected="false">
                  6. Payment
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="pills-confirm-tab" data-toggle="pill" href="#pills-confirm" role="tab" aria-controls="pills-confirm" aria-selected="false">
                  7. Confirmation
                </a>
              </li>

            </ul>
            <div class="tab-content" id="pills-tabContent">
              <div class="tab-pane fade show active" id="pills-applicant" role="tabpanel" aria-labelledby="pills-applicant-tab">... Applicant </div>
              <div class="tab-pane fade" id="pills-activities-land" role="tabpanel" aria-labelledby="pills-activities-land-tab">... Activities Land</div>
              <div class="tab-pane fade" id="pills-activities-marine" role="tabpanel" aria-labelledby="pills-activities-marine-tab">... Activities Marine</div>
              <div class="tab-pane fade" id="pills-other-details" role="tabpanel" aria-labelledby="pills-other-details-tab">... Other Details</div>
              <div class="tab-pane fade" id="pills-online-training" role="tabpanel" aria-labelledby="pills-online-training-tab">... Online Training</div>
              <div class="tab-pane fade" id="pills-payment" role="tabpanel" aria-labelledby="pills-payment-tab">... Payment</div>
              <div class="tab-pane fade" id="pills-confirm" role="tabpanel" aria-labelledby="pills-confirm-tab">... Confirmation</div>
            </div>


        <!--
        <Proposal v-if="proposal" :proposal="proposal" id="proposalStart">
            <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
            <input type='hidden' name="schema" :value="JSON.stringify(proposal)" />
            <input type='hidden' name="proposal_id" :value="1" />
            <div class="row" style="margin-bottom: 50px">
              <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
              <div class="navbar-inner">
                <div v-if="!proposal.readonly" class="container">
                  <p class="pull-right" style="margin-top:5px;">
                    <input type="button" @click.prevent="save_exit" class="btn btn-primary" value="Save and Exit"/>
                    <input type="button" @click.prevent="save" class="btn btn-primary" value="Save and Continue"/>
                    <input type="button" @click.prevent="submit" class="btn btn-primary" value="Submit"/>

                    <input id="save_and_continue_btn" type="hidden" @click.prevent="save_wo_confirm" class="btn btn-primary" value="Save Without Confirmation"/>
                  </p>
                </div>
                <div v-else class="container">
                  <p class="pull-right" style="margin-top:5px;">
                    <router-link class="btn btn-primary" :to="{name: 'external-proposals-dash'}">Back to Dashboard</router-link>
                  </p>
                </div>
              </div>
              </div>  
            </div>
        </Proposal>           
        -->

    </div>
</template>

<script>
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
</style>

