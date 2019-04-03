<template lang="html">
<div class="row" id="userInfo">
    <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Accreditation Details <small>123</small>
                <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
                </h3>
            </div>
            <div class="panel-body collapse in" :id="pBody">
                <div class="" >                        
                    <div class="form-horizontal col-sm-12 borderDecoration">
                        <label class="control-label">Are you currently accredited?</label>
                        <ul class="list-inline"  >
                            <li v-for="c in accreditation_choices" class="form-check list-inline-item">
                                <input  class="form-check-input" ref="Checkbox" type="checkbox" v-model="proposal.other_details.accreditation_type" :value="c.key" data-parsley-required />
                                        {{ c.value }}
                            </li>
                        </ul>
                        <div v-if="proposal.other_details.accreditation_type">
                            <fieldset class="scheduler-border">
                                <legend class="scheduler-border">{{proposal.other_details.accreditation_type}}</legend>
                                <div class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left"  for="Name">Expiry Date</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <div class="input-group date" ref="expiry_date" style="width: 70%;">
                                                <input type="text" class="form-control" v-model="proposal.other_details.accreditation_expiry" name="expiry_date" placeholder="DD/MM/YYYY">
                                                <span class="input-group-addon">
                                                    <span class="glyphicon glyphicon-calendar"></span>
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left"  for="Name">Accreditation certificates</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <FileField :proposal_id="proposal.id" isRepeatable="false" name="accreditation_certificate" required_doc_id="1" :id="'proposal'+proposal.id"></FileField>
                                        </div>
                                    </div>
                                </div>
                            </fieldset>
                        </div>
                    </div>
                </div>
            </div>                
        </div>
    </div>
    <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">License Period <small>123</small>
                <a class="panelClicker" :href="'#'+lBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="lBody">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
                </h3>
            </div>
            <div class="panel-body collapse in" :id="lBody">
                <div class="" >                        
                    <div class="form-horizontal col-sm-12 borderDecoration">
                        
                        <div class="form-group">
                            <div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Preferred licence period</label>
                                </div>
                                <div class="col-sm-9">
                                    <select class="form-control" v-model="proposal.other_details.preferred_licence_period">
                                        <option v-for="l in licence_period_choices" :value="z">{{l.value}}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Nominated start date</label>
                                </div>
                                <div class="col-sm-9">
                                    <div class="input-group date" ref="nominated_start_date" style="width: 70%;">
                                        <input type="text" class="form-control" v-model="proposal.other_details.nominated_start_date" name="nominated_start_date" placeholder="DD/MM/YYYY">
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div> 
                    </div>
                </div>
            </div>                
        </div>
    </div>
    <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Moorings <small>(marine-based activities)</small>
                <a class="panelClicker" :href="'#'+mBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="mBody">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
                </h3>
            </div>
            <div class="panel-body collapse in" :id="mBody">
                <div class="" >                        
                    <div class="form-horizontal col-sm-12 borderDecoration">
                        <div class="form-group">
                            <div class="row">
                                <div class="col-sm-12">
                                    <label>Provide the mooring number for any mooring within a marine reseve your operation will use</label>
                                </div>   
                            </div>
                            <div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Mooring number</label>
                                </div>
                                <div class="col-sm-9">
                                    <input type="text" class="form-control" name="Mooring number" placeholder="">
                                </div>
                            </div>
                        </div>
                   </div>
                </div>
            </div>                
        </div>
    </div>
    <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Insurance <small>123</small>
                <a class="panelClicker" :href="'#'+iBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="iBody">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
                </h3>
            </div>
            <div class="panel-body collapse in" :id="iBody">
                <div class="" >                        
                    <div class="form-horizontal col-sm-12 borderDecoration">
                        <div class="form-group">
                            <div class="row">
                                <div class="col-sm-12">
                                    <label>
                                    <ol type="a">
                                        <li>The operator shall at all times during the period of the Licence maiantain a policy of public liability insurance, that covers the areas and operations allowed under the licence, in the name of the Operator tot the extent of its rights and interests for a sum of not less than $10 million per event.</li>
                                        <li>The operator shall provide the Director General proof of the existence and currency of such insurance policy whenever requested by the Director General during the term of the Licence</li>
                                    </ol></label>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Certificate of currency
                                    </label>
                                </div>
                                <div class="col-sm-3">
                                    <FileField :proposal_id="proposal.id" isRepeatable="false" name="currency_certificate" required_doc_id="1" :id="'proposal'+proposal.id"></FileField>
                                </div>
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Expiry Date
                                    </label>
                                </div>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="expiry_date" style="width: 70%;">
                                        <input type="text" class="form-control" name="expiry_date" placeholder="DD/MM/YYYY" v-model="proposal.other_details.insurance_expiry">
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>                
        </div>
    </div>
    <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Other Detials <small></small>
                <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="oBody">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
                </h3>
            </div>
            <div class="panel-body collapse in" :id="oBody">
                <div class="" >                        
                    <div class="form-horizontal col-sm-12 borderDecoration">
                       <div class="form-group">
                           <div class="row">
                                <div class="col-sm-12">
                                    <label>Provide any comments and upload any additional documentation like brochures, itineraries etc. that may help with the assessment of this application</label>
                                </div>   
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <textarea class="form-control" v-model="proposal.other_details.other_comments"></textarea>
                                </div>                                
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <FileField :proposal_id="proposal.id" isRepeatable="true" name="other_details" required_doc_id="1" :id="'proposal'+proposal.id"></FileField>
                                </div>                                
                            </div>
                       </div> 
                    </div>
                </div>
            </div>                
        </div>
    </div>
    <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Park Entry and Camping Fees <small></small>
                <a class="panelClicker" :href="'#'+cBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="cBody">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
                </h3>
            </div>
            <div class="panel-body collapse in" :id="cBody">
                <div class="" >                        
                    <div class="form-horizontal col-sm-12 borderDecoration">
                        <div class="row">
                            <div class="col-sm-6">
                                    <label class="control-label pull-left"  for="Name">Do you require credit facilities for payment of fees</label>
                            </div>
                            <div class="col-sm-3">
                                <label>
                                    <input type="radio" value="true" v-model="proposal.other_details.credit_fees"/>Yes
                                </label>
                            </div>
                            <div class="col-sm-3">
                                <label>
                                    <input type="radio" value="false" v-model="proposal.other_details.credit_fees"/>No
                                </label>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-6">
                                    <label class="control-label pull-left"  for="Name">Do you require Cash / Credit Payment Docket books?</label>
                            </div>
                            <div class="col-sm-3">
                                <label>
                                    <input type="radio" v-model="proposal.other_details.credit_docket_books" value="true"/>Yes
                                </label>
                            </div>
                            <div class="col-sm-3">
                                <label>
                                    <input type="radio" v-model="proposal.other_details.credit_docket_books" value="false"/>No
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>                
        </div>
    </div>
    <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">Deed Poll<small></small>
                <a class="panelClicker" :href="'#'+dBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="dBody">
                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                </a>
                </h3>
            </div>
            <div class="panel-body collapse in" :id="dBody">
                <div class="" >                        
                    <div class="form-horizontal col-sm-12 borderDecoration">
                        <div class="form-group">
                           <div class="row">
                                <div class="col-sm-12">
                                    <label>Print the deed poll, sign it, have it witnesses and attach it to this application</label>
                                </div>   
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <FileField :proposal_id="proposal.id" isRepeatable="false" name="deed_poll" required_doc_id="1" :id="'proposal'+proposal.id"></FileField>
                                </div>                                
                            </div>
                       </div> 
                    </div>
                </div>
            </div>                
        </div>
    </div>

</div>
</template>

<script>
import Vue from 'vue' 
import FileField from './required_docs.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
        props:{
            proposal:{
                type: Object,
                required:true
            }
        },
        data:function () {
            let vm = this;
            return{
                pBody: 'pBody'+vm._uid,
                lBody: 'lBody'+vm._uid,
                iBody: 'iBody'+vm._uid,
                mBody: 'mBody'+vm._uid,
                oBody: 'oBody'+vm._uid,
                cBody: 'cBody'+vm._uid,
                dBody: 'dBody'+vm._uid,
                values:null,
                accreditation_choices:[],
                accreditation_type:[],
                licence_period_choices:[],
                datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            }
        },
        components: {
          FileField,
        },
        methods:{
            fetchAccreditationChoices: function(){
                let vm = this;
                vm.$http.get('/api/accreditation_choices.json').then((response) => {
                    vm.accreditation_choices = response.body;
                    
                },(error) => {
                    console.log(error);
                } );
            },
            fetchLicencePeriodChoices: function(){
                let vm = this;
                vm.$http.get('/api/licence_period_choices.json').then((response) => {
                    vm.licence_period_choices = response.body;
                    
                },(error) => {
                    console.log(error);
                } );
            },
        },
        mounted: function(){
            let vm = this;
            vm.fetchAccreditationChoices();
            vm.fetchLicencePeriodChoices();
        }
    }
</script>

<style lang="css" scoped>
    /*ul, li {
        zoom:1;
        display: inline;
    }*/
    fieldset.scheduler-border {
    border: 1px groove #ddd !important;
    padding: 0 1.4em 1.4em 1.4em !important;
    margin: 0 0 1.5em 0 !important;
    -webkit-box-shadow:  0px 0px 0px 0px #000;
            box-shadow:  0px 0px 0px 0px #000;
    }
    legend.scheduler-border {
    width:inherit; /* Or auto */
    padding:0 10px; /* To give a bit of padding on the left and right */
    border-bottom:none;
    }
</style>

