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
                                <input  class="form-check-input" ref="Checkbox" type="checkbox" @click="selectAccreditation($event, c)" v-model="selected_accreditations" :value="c.key" data-parsley-required :disabled="proposal.readonly" />
                                        {{ c.value }}
                            </li>
                        </ul>
                        <div v-for=" accreditation in proposal.other_details.accreditations">
                            <div v-if="!accreditation.is_deleted" class="col-sm-12">
                                <Accreditation :accreditation="accreditation":proposal_id="proposal.id" :readonly="proposal.readonly" id="accreditation"></Accreditation>
                            </div>
                            <!-- <fieldset class="scheduler-border">
                                <legend class="scheduler-border">{{accreditation_type.value}}</legend>
                                <div class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-right"  for="Name">Expiry Date</label>
                                        </div>
                                        <div class="col-sm-9">
                                            <div class="input-group date" ref="accreditation_expiry" style="width: 70%;">
                                                <input type="text" class="form-control" v-model="proposal.other_details.accreditation_expiry" name="accreditation_expiry" placeholder="DD/MM/YYYY">
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
                                            <FileField :proposal_id="proposal.id" isRepeatable="false" name="accreditation_certificate" :id="'proposal'+proposal.id"></FileField>
                                        </div>
                                    </div>
                                </div>
                            </fieldset> -->
                        </div>
                    </div>
                </div>
            </div>                
        </div>
    </div>
    <div class="col-sm-12">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title">License Period <small></small>
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
                                <div class="col-sm-9" style="margin-bottom: 5px">
                                    <select class="form-control" v-model="proposal.other_details.preferred_licence_period" ref="preferred_licence_period" :disabled="proposal.readonly">
                                        <option v-for="l in licence_period_choices" :value="l.key">{{l.value}}</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Nominated start date</label>
                                </div>
                                <div class="col-sm-9">
                                    <div class="input-group date" ref="nominated_start_date" style="width: 70%;">
                                        <input type="text" class="form-control" v-model="proposal.other_details.nominated_start_date" name="nominated_start_date" placeholder="DD/MM/YYYY" :disabled="proposal.readonly">
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
                            <div class="row" v-for="(m, index) in proposal.other_details.mooring">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Mooring number</label>
                                </div>
                                <div class="col-sm-9" style="margin-bottom: 5px">
                                    <input type="text" class="form-control" name="Mooring number" placeholder="" :disabled="proposal.readonly" v-model="proposal.other_details.mooring[index]">
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <span><a @click="addMooring()" target="_blank" class="control-label pull-left" v-if="!proposal.readonly">Add another mooring</a></span>
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
                <h3 class="panel-title">Insurance <small></small>
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
                                    <FileField :proposal_id="proposal.id" isRepeatable="false" name="currency_certificate" :id="'proposal'+proposal.id" :readonly="proposal.readonly"></FileField>
                                </div>
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Expiry Date
                                    </label>
                                </div>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="insurance_expiry" style="width: 70%;">
                                        <input type="text" class="form-control" name="insurance_expiry" placeholder="DD/MM/YYYY" v-model="proposal.other_details.insurance_expiry" :disabled="proposal.readonly">
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
                <h3 class="panel-title">Other Details <small></small>
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
                                    <textarea class="form-control" v-model="proposal.other_details.other_comments" :disabled="proposal.readonly"></textarea>
                                </div>                                
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <FileField :proposal_id="proposal.id" isRepeatable="true" name="other_details" :id="'proposal'+proposal.id" :readonly="proposal.readonly"></FileField>
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
                                    <input type="radio" value="true" v-model="proposal.other_details.credit_fees" :disabled="proposal.readonly"/>Yes
                                </label>
                            </div>
                            <div class="col-sm-3">
                                <label>
                                    <input type="radio" value="false" v-model="proposal.other_details.credit_fees" :disabled="proposal.readonly"/>No
                                </label>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-6">
                                    <label class="control-label pull-left"  for="Name">Do you require Cash / Credit Payment Docket books?</label>
                            </div>
                            <div class="col-sm-3">
                                <label>
                                    <input type="radio" v-model="proposal.other_details.credit_docket_books" value="true" @change="handleRadioChange" ref="docket_books_yes" :disabled="proposal.readonly"/>Yes
                                </label>
                            </div>
                            <div class="col-sm-3">
                                <label>
                                    <input type="radio" v-model="proposal.other_details.credit_docket_books" value="false" @change="handleRadioChange" :disabled="proposal.readonly"/>No
                                </label>
                            </div>
                        </div>
                        <div>
                            <div id="show_docket" class="hidden">
                            <div class="col-sm-6" >
                                <label class="control-label pull-left"  for="Name">Number of docket books</label>
                            </div>
                            <div class="col-sm-6">
                                <input type="text" class="form-control" name="docket_books_number" placeholder="" :disabled="proposal.readonly" v-model="proposal.other_details.docket_books_number">
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
                                    <label>Print the deed poll, sign it, have it witnessed and attach it to this application</label>
                                </div>   
                            </div>
                            <div class="row">
                                <div class="col-sm-12">
                                    <FileField :proposal_id="proposal.id" isRepeatable="false" name="deed_poll" :id="'proposal'+proposal.id" :readonly="proposal.readonly"></FileField>
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
//import FileField from './required_docs.vue'
import Accreditation from './accreditation_type.vue'
import FileField from '@/components/forms/filefield.vue'
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
                selected_accreditations:[],
                licence_period_choices:[],
                mooring: [''],
                //mooring:[{'value':''}],
                datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true,
            },
            }
        },
        components: {
          FileField,
          Accreditation
        },
        computed: {
            
        },
        watch:{
            
            accreditation_type: function(){
                this.proposal.other_details.accreditation_type=this.accreditation_type.key;
            },
        },
        methods:{
            handleRadioChange: function(e){
                    if(e.target.value=="true"){
                        console.log(e.target.value);
                        $('#show_docket').removeClass('hidden')
                    }
                    else{
                        $('#show_docket').addClass('hidden')
                    }
                
            },
            showDockteNumber: function(){
                let vm=this;
                if(vm.proposal && vm.proposal.other_details.credit_docket_books){
                    var input = this.$refs.docket_books_yes;
                    var e = document.createEvent('HTMLEvents');
                    e.initEvent('change', true, true);
                    var disabledStatus = input.disabled;
                    try {
                        /* Firefox will not fire events for disabled widgets, so (temporarily) enabling them */
                        if(disabledStatus) {
                            input.disabled = false;
                        }
                        input.dispatchEvent(e);
                    } finally {
                        if(disabledStatus) {
                            input.disabled = true;
                        }
                    }
                }
            },
            addMooring: function(){
                let vm=this;
                //var new_mooring= helpers.copyObject(vm.mooring)
                var new_mooring= helpers.copyObject(vm.proposal.other_details.mooring)
                new_mooring.push('');
                vm.proposal.other_details.mooring=new_mooring;
                console.log(vm.proposal.other_details.mooring);
            },
            fetchAccreditationChoices: function(){
                let vm = this;
                vm.$http.get('/api/accreditation_choices.json').then((response) => {
                    vm.accreditation_choices = response.body;
                    if(vm.proposal.other_details.accreditation_type
                        ){
                        for(var i=0; i<vm.accreditation_choices.length; i++){
                            if(vm.accreditation_choices[i].key==vm.proposal.other_details.accreditation_type){
                                vm.accreditation_type=vm.accreditation_choices[i]
                            }
                        }
                    }
                    
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
            checkProposalAccreditation: function(){
                let vm= this;
                if(vm.proposal && vm.proposal.other_details){
                    for(var i=0; i<vm.proposal.other_details.accreditations.length; i++){
                        vm.proposal.other_details.accreditations[i].is_deleted=false;
                        vm.selected_accreditations.push(vm.proposal.other_details.accreditations[i].accreditation_type);
                    }
                }
            },
            selectAccreditation: function(e, accreditation_type){
                let vm=this;
                if(e.target.checked){
                    var found=false;
                    for(var i=0;i<vm.proposal.other_details.accreditations.length; i++){
                        if(vm.proposal.other_details.accreditations[i].accreditation_type==accreditation_type.key){
                            found=true;
                            vm.proposal.other_details.accreditations[i].is_deleted=false;
                        }
                    }
                    if(found==false){
                    var data={
                        'accreditation_type': accreditation_type.key,
                        'accreditation_expiry':'',
                        'comments':'',
                        'proposal_other_details': vm.proposal.other_details.id,
                        'is_deleted': false,
                        'accreditation_type_value': accreditation_type.value
                    }
                    var acc=helpers.copyObject(vm.proposal.other_details.accreditations);
                    acc.push(data);
                    vm.proposal.other_details.accreditations=acc;
                    }
                }
                else{
                    for(var i=0;i<vm.proposal.other_details.accreditations.length; i++)
                    {

                        if(vm.proposal.other_details.accreditations[i].accreditation_type==accreditation_type.key)
                        {
                            if(vm.proposal.other_details.accreditations[i].id){
                                //console.log('yes')
                                var acc=helpers.copyObject(vm.proposal.other_details.accreditations);
                                acc[i].is_deleted=true;
                                vm.proposal.other_details.accreditations=acc;
                            }
                            else{
                                var acc=helpers.copyObject(vm.proposal.other_details.accreditations);
                                acc.splice(i,1);
                                vm.proposal.other_details.accreditations=acc;
                            }
                        }
                    }
                }
            },
            eventListeners:function (){
                let vm=this;
                $(vm.$refs.accreditation_expiry).datetimepicker(vm.datepickerOptions);
                $(vm.$refs.accreditation_expiry).on('dp.change', function(e){
                    if ($(vm.$refs.accreditation_expiry).data('DateTimePicker').date()) {
                        

                        vm.proposal.other_details.accreditation_expiry =  e.date.format('DD/MM/YYYY');
                    }
                    else if ($(vm.$refs.accreditation_expiry).data('date') === "") {
                        vm.proposal.other_details.accreditation_expiry = "";
                    }
                 });
                //Nominated start date listener
                $(vm.$refs.nominated_start_date).datetimepicker(vm.datepickerOptions);
                $(vm.$refs.nominated_start_date).on('dp.change', function(e){
                    if ($(vm.$refs.nominated_start_date).data('DateTimePicker').date()) {
                        

                        vm.proposal.other_details.nominated_start_date =  e.date.format('DD/MM/YYYY');
                    }
                    else if ($(vm.$refs.nominated_start_date).data('date') === "") {
                        vm.proposal.other_details.nominated_start_date = "";
                    }
                 });
                //Insurance expiry date listener
                $(vm.$refs.insurance_expiry).datetimepicker(vm.datepickerOptions);
                $(vm.$refs.insurance_expiry).on('dp.change', function(e){
                    if ($(vm.$refs.insurance_expiry).data('DateTimePicker').date()) {
                        

                        vm.proposal.other_details.insurance_expiry =  e.date.format('DD/MM/YYYY');
                    }
                    else if ($(vm.$refs.insurance_expiry).data('date') === "") {
                        vm.proposal.other_details.insurance_expiry = "";
                    }
                 });
                // Intialise select2
                $(vm.$refs.preferred_licence_period).select2({
                    "theme": "bootstrap",
                    allowClear: true,
                    placeholder:"Select preferred licence period"
                }).
                on("select2:select",function (e) {
                    var selected = $(e.currentTarget);
                    vm.proposal.other_details.preferred_licence_period = selected.val();
                    vm.proposal.other_details.preferred_licence_period_id = selected.val();
                }).
                on("select2:unselect",function (e) {
                    var selected = $(e.currentTarget);
                    vm.proposal.other_details.preferred_licence_period = selected.val();
                    vm.proposal.other_details.preferred_licence_period_id = selected.val();
                });
            },
        },
        mounted: function(){
            let vm = this;
            vm.fetchAccreditationChoices();
            vm.fetchLicencePeriodChoices();
            vm.checkProposalAccreditation();
            vm.showDockteNumber();
            this.$nextTick(()=>{
                vm.eventListeners();
            });
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

