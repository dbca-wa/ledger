<!DOCTYPE html>
<template>
    <div class="addBooking">
        <form name="admissionsBooking" @submit.prevent="processForm">
            <div class="container">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="well" style="text-align:center;">
                            <h3>Paying Admission Fees</h3>
                        </div>
                        <div class="row" style="margin-top:2%;">
                            <div class="col-lg-6">
                                <div class="well">
                                    <h3 class="text-primary" style="text-align:center;">Personal Details</h3>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain2">Given Name(s)</label>
                                            <div class="col-sm-8">
                                                <input id="givenName" v-model="givenName" class="form-control" name="givenName" type="text" @blur="validateGivenName()" required/>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain2">Last Name</label>
                                            <div class="col-sm-8">
                                                <input id="lastName" v-model="lastName" class="form-control" name="lastName" type="text" @blur="validateLastName()" required/>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain2">Email</label>
                                            <div class="col-sm-8">
                                                <input  id="email" v-model="email" class="form-control" name="email" @blur="validateEmailFormat()" type="email" required/>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain2">Confirm Email</label>
                                            <div class="col-sm-8">
                                                <input  id="emailConfirm" v-model="emailConfirm" class="form-control" name="emailConfirm" @blur="validateEmail()" type="email" required/>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row" v-if="errorMsgPersonal">
                                        <div class="alert alert-danger" id="warning" role="alert">{{ errorMsgPersonal }}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="well">
                                    <h3 class="text-primary" style="text-align:center;">Booking Details</h3>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain">Arrival</label>
                                            <div class="col-sm-8">
                                                <input id="dateArrival" class="form-control" name="arrival" type="text" @blur="validateArrivalDate()" placeholder="DD/MM/YYYY" required/>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain">Overnight Stay</label>
                                            <div class="col-sm-8">
                                                <input id="overnightStayYes" v-model="overnightStay" name="overnightStay" refs="overnightStayYes" @change="validateOvernightStay()" value="yes" type="radio"/><label class="radio-label">Yes </label><input id="overnightStayNo" v-model="overnightStay" @change="validateOvernightStay()" name="overnightStay" type="radio" value="no" style="margin-left:2%"/><label class="radio-label">No</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain">Vessel Registration</label>
                                            <div class="col-sm-8">
                                                <input id="vesselReg" v-model="vesselReg" class="form-control" name="vesselReg" @blur="validateVesselReg()" type="text"/>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain">Number of Adults</label>
                                            <div class="col-sm-8">
                                                <input id="noOfAdults" v-model="noOfAdults" class="form-control" name="noOfAdults" @blur="validateNoOfPeople()" type="number" palceholder="0"/>
                                            </div>
                                        </div>
                                        <label class="label-small">(12 and over)</label>
                                    </div>
                                    <div class="row" style="display:none;">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain">Number of Concessions</label>
                                            <div class="col-sm-8">
                                                <input id="noOfConcessions" v-model="noOfConcessions" class="form-control" name="noOfConcessions" @blur="validateNoOfPeople()" type="number" palceholder="0"/>
                                            </div>
                                            <label class="label-small"> </label>
                                        </div>
                                        <label class="label-small"></label>
                                    </div>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain">Number of Children</label>
                                            <div class="col-sm-8">
                                                <input id="noOfChildren" v-model="noOfChildren" class="form-control" name="noOfChildren" @blur="validateNoOfPeople()" type="number" palceholder="0"/>
                                            </div>
                                        </div>
                                        <label class="label-small">(4 - 12)</label>
                                    </div>
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain">Number of Infants</label>
                                            <div class="col-sm-8">
                                                <input id="noOfInfants" v-model="noOfInfants" class="form-control" name="noOfInfants" @blur="validateNoOfPeople()" type="number" palceholder="0"/>
                                            </div>
                                        </div>
                                        <label class="label-small">(0 - 4)</label>
                                    </div>
                                    
                                    <div class="row">
                                        <div class="small-12 medium-12 large-4 columns">
                                            <label class="label-plain">Warning Reference</label>
                                            <div class="col-sm-8">
                                                <input id="warningRefNo" v-model="warningRefNo" class="form-control" name="warningRefNo" @blur="validateWarningRefNo()" type="text"/>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row" v-if="errorMsg">
                                        <div class="alert alert-danger" id="warning" role="alert">{{ errorMsg }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                        <div class="well">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="Total Price">Total Price <span class="text-muted">(GST inclusive.)</span></label>
                                        <div class="input-group">
                                            <span class="input-group-addon">AUD $</span>
                                            <input type="text" class="form-control" :value="total|formatMoney(2)" readonly="true">
                                        </div>
                                    </div>
                                </div>
                                <!-- <div class="col-md-6">
                                    <div class="form-group">
                                        <p style="margin-top:30px;">Changes not permitted.Cancel up to 29 days before arrival for 50% refund.</p>
                                    </div>
                                </div> -->
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="small-12 medium-12 large-4 columns">
                                        <label class="label-plain" style="width:250px;">Click <a href="http://ria.wa.gov.au/about-us/Fees-and-charges" taget="_blank">here</a> for price information.</label>                                        </div>
                                    </div>
                                <div class="col-md-6">
                                    <div class="row"> 
                                        <div class="col-md-8 col-md-offset-5">
                                            <div class="checkbox">
                                                <label><input type="checkbox" value="" v-model="toc">I agree to the <a target="_blank" id='terms-link' href="javascript:void(0);" v-on:click="loadTerms();">terms and conditions</a></label>
                                            </div>
                                            <button :disabled="!validToProceed" type="submit" class="btn btn-primary" style="width:180px;background-color:#4286f4;font-weight:bold;">Proceed to Payment</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        <modal name="messageModal" height="auto"
            transition="nice-modal-fade"
            :resizeable="false"
            :delay="100"
            :scrollable="true"
            :draggable="false">
            <div class="messageModal-content" align="center">
                <h1 id="ModalTitle">System Message</h1>
                <div align="left" style="padding:15px;">
                    <div class = "row">
                        <div class="col-sm-12">
                            <div class="alert alert-danger" align="center">
                                {{ message }}
                            </div>
                        </div>
                    </div>
                </div>
                <div align="left" style="margin-bottom:20px; margin-left:20px;">
                    <button type="button" v-on:click="messageModalConfirm()" class="btn btn-primary" style="width:80px;font-weight:bold;">OK</button>
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
import 'foundation-sites';
import 'foundation-datepicker/js/foundation-datepicker';
import moment from 'moment';
import JQuery from 'jquery';
import swal from 'sweetalert2';
import { api_endpoints } from './hooks';

let $ = JQuery
var nowTemp = new Date();
var now = moment.utc({year: nowTemp.getFullYear(), month: nowTemp.getMonth(), day: nowTemp.getDate(), hour: 0, minute: 0, second: 0}).toDate();

function getQueryParam(name, fallback) {
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)");
    var results = regex.exec(window.location.href);
    if (!results) return fallback;
    if (!results[2]) return fallback;
    return decodeURIComponent(results[2].replace(/\+/g, " "));
};

export default {
    name:'admissionsBooking',
    el: '#admissionsBooking',
    data: function() {
        let vm = this;
        return {
        mooringUrl: global.parkstayUrl || process.env.PARKSTAY_URL,
        arrivalDate: moment.utc(getQueryParam('arrival', moment.utc(now).format('YYYY/MM/DD')), 'YYYY/MM/DD'),
        overnightStay: '',
        vesselReg: '',
        noOfAdults: '0',
        noOfConcessions: '0',
        noOfChildren: '0',
        noOfInfants: '0',
        warningRefNo: '',
        givenName: '',
        lastName: '',
        email: '',
        emailConfirm: '',
        currentCostDateStart: '',
        currentCostDateEnd: '',
        adultCost: 0,
        adultOvernightCost: 0,
        childrenCost: 0,
        childrenOvernightCost: 0,
        infantCost: 0,
        infantOvernightCost: 0,
        familyCost: 0,
        familyOvernightCost: 0,
        total: 0,
        errorMsg: null,
        errorMsgPersonal: null,
        toc: false,
        message: null,
        noPayment: false,
        terms: '',
        errors: {
            arrivalDate: false,
            overnightStay: false,
            vesselReg: false,
            noOfAdults: false,
            noOfConcessions: false,
            noOfChildren: false,
            noOfInfants: false,
            warningRefNo: false,
            givenName: false,
            lastName: false,
            email: false,
            emailConfirm: false,
            }
        }
    },
    computed: {
        validToProceed: {
            cache: false,
            get: function(){
                if (this.toc && !this.errorMsg && !this.errorMsgPersonal &&!this.noPayment ){
                    return true;
                } else {
                    return false;
                } 
            }
        },
        arrivalDateString: {
            cache: false,
            get: function() {
                return this.arrivalEl[0].value ? moment(this.arrivalData.getDate()).format('YYYY/MM/DD') : null; 
            }
        },
    },
    watch: {
        noOfAdults: function(val){
            this.validateNoOfPeople();
        },
        noOfChildren: function(val){
            this.validateNoOfPeople();
        },
        noOfInfants: function(val){
            this.validateNoOfPeople();
        }
    },
    filters: {
        formatMoney:function(n,c, d, t){
            c = isNaN(c = Math.abs(c)) ? 2 : c;
            d = d == undefined ? "." : d;
            t = t == undefined ? "," : t;
            var s = n < 0 ? "-" : "";
            var i = String(parseInt(n = Math.abs(Number(n) || 0).toFixed(c)));
            var j = (j = i.length) > 3 ? j % 3 : 0;
            return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
        }
    },
    props: {

    },
    methods: {
        messageModalConfirm: function(){
            this.message = null;
            this.$modal.hide('messageModal');
        },
        processForm: function(){
            var vm = this;
            console.log("processing");
            var formInvalid = false;
            var givenName = this.givenName;
            this.validateGivenName();
            var lastName = this.lastName;
            this.validateLastName();
            var email = this.email;
            this.validateEmail();
            var arrival = this.arrivalDateString;
            this.validateArrivalDate();
            var overnightStay = this.overnightStay;
            this.validateOvernightStay();
            var noOfAdults = this.noOfAdults;
            var noOfConcessions = this.noOfConcessions;
            var noOfChildren = this.noOfChildren;
            var noOfInfants = this.noOfInfants;
            this.validateNoOfPeople();
            var warningRefNo = this.warningRefNo;
            this.validateWarningRefNo();
            
            var errs = this.errors
            if(errs.arrivalDate === true || errs.overnightStay === true || errs.givenName === true || errs.lastName === true || errs.email === true || errs.noOfAdults === true || errs.noOfChildren === true || errs.noOfInfants === true){
                formInvalid = true;
            }
            if(!formInvalid){
                //we can continue and send off to basket.
                var vesselReg = this.vesselReg;
                var location = $('#location').val();
                var submitData = {
                    arrival: arrival,
                    overnightStay: overnightStay,
                    vesselReg: vesselReg,
                    noOfAdults: noOfAdults,
                    noOfConcessions: noOfConcessions,
                    noOfChildren: noOfChildren,
                    noOfInfants: noOfInfants,
                    warningRefNo: warningRefNo,
                    givenName: givenName,
                    lastName: lastName,
                    email: email,
                    location: location,
                    // mooring_group: mooring_group
                }
                $.ajax({
                    url: vm.mooringUrl + "/api/create_admissions_booking",
                    method: 'POST',
                    data: submitData,
                    dataType: 'json',
                    crossDomain: true,
                    xhrFields: {
                        withCredentials: true
                    },
                    success: function(data, stat, xhr) {
                        console.log(data);
                        if (data.status == 'success') {
                            console.log("success");
                            window.location.href = vm.mooringUrl + data.redirect;
                        } else if (data.status == 'failure'){
                            console.log("failure");
                            if (data.error[1].includes("Admissions Oracle Code")){
                                var msg = data.error[1].split('.')[0];
                                vm.message = msg;
                                vm.$modal.show('messageModal');
                            } else {
			            swal({
				            title: 'Error',
				            text: data.error[1],
				            type: 'error',
				            showCancelButton: false,
				            confirmButtonText: 'CLOSE',
				            showLoaderOnConfirm: true,
				            allowOutsideClick: false
			            })
	


			    }
                        }
                    },
                    error: function(xhr, stat, err) {
                        console.log('POST error');
                        console.log((xhr.responseJSON && xhr.responseJSON.msg) ? xhr.responseJSON.msg : '"'+err+'" response when communicating with Mooring.');
                    }
                });
            } else {
                //we return to the form with errors.
            }
        },
        validateGivenName: function(){
            var error = "Please enter a valid given name.";
            var fieldToCheck = this.givenName;
            if(!fieldToCheck){
                this.errors.givenName = true;
                this.errorMsgPersonal = error
            } else {
                this.errors.givenName = false;
                if(this.errorMsgPersonal == error){
                    this.errorMsgPersonal = null;
                }
            }
        },
        validateLastName: function(){
            var error = "Please enter a valid surname.";
            var fieldToCheck = this.lastName;
            if(!fieldToCheck){
                this.errors.lastName = true;
                this.errorMsgPersonal = error;
            } else {
                this.errors.lastName = false;
                if(this.errorMsgPersonal == error){
                    this.errorMsgPersonal = null;
                }
            }
        },
        validateEmail: function(){
            var error1 = "Please enter a valid email.";
            var error2 = "Email does not match.";
            var error3 = "Email does not follow convention.\nexample@domain.com";
            var fieldToCheck = this.email;
            var emailConfirm = this.emailConfirm;
            if(!fieldToCheck){
                this.errors.email = true;
                this.errorMsgPersonal = error1;
            } else {
                var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                if(re.test(fieldToCheck)){
                    if(fieldToCheck === emailConfirm){
                        this.errors.email = false;
                        this.errors.emailConfirm = false;
                        if(this.errorMsgPersonal == error1 || this.errorMsgPersonal == error2 || this.errorMsgPersonal == error3){
                            this.errorMsgPersonal = null;
                        }
                    } else {
                        this.errors.emailConfirm = true;
                        this.errorMsgPersonal = error2
                    }
                } else {
                    this.errors.email = true;
                    this.errorMsgPersonal = error3
                }  
            }
        },
        validateEmailFormat: function(){
            var error1 = "Please enter a valid email.";
            var error2 = "Email does not follow convention.\nexample@domain.com";
            var fieldToCheck = this.email;
            if(!fieldToCheck){
                this.errors.email = true;
                this.errorMsgPersonal = error1;
            } else {
                var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                if(re.test(fieldToCheck)){
                    this.errorMsgPersonal = null;
                    this.errors.email = false;
                } else {
                    this.errors.email = true;
                    this.errorMsgPersonal = error2;
                }
            }
        },
        validateArrivalDate: function(){
            var error1 = "If paying for a prior warning, please ensure you enter the reference number.";
            var error2 = "Please select a date from the past if paying for a warning.";
            var fieldToCheck = this.arrivalDate;
            if(!fieldToCheck){
                this.errors.arrivalDate = true;
            } else {
                this.calculateTotal();
                var selectedDate = new Date(fieldToCheck);
                if(selectedDate < now && !this.warningRefNo){
                    this.errors.arrivalDate = true;
                    this.errorMsg = error1;
                } else if (selectedDate > now && this.warningRefNo){
                    this.errors.warningRefNo = true;
                    this.errorMsg = error2;
                } else {
                    this.errors.arrivalDate = false;
                    if(this.errorMsg == error1 || this.errorMsg == error2){
                        this.errorMsg = null;
                    }
                }
            }
        },
        validateVesselReg: function() {
            let vm = this;
            vm.vesselReg = vm.vesselReg.replace(/ /g, ""); 
            var reg = vm.vesselReg;
            var data = {
                'rego': reg
            }
            vm.noPayment = false;
            if(reg){
                $.ajax({
                    url: process.env.PARKSTAY_URL + "/api/registeredVessels/",
                    dataType: 'json',
                    data: data,
                    method: 'GET',
                    success: function(data, stat, xhr) {
                        if(data[0]){
                            if(data[0].admissionsPaid){
                                vm.message = "Admission Fees for this vessel are already paid.";
                                vm.noPayment = true;
                                vm.$modal.show('messageModal');
                            }
                        } else {
                            console.log("Registration was not found.")
                        }
                    }
                });
            }
        },
        validateWarningRefNo: function(){
            var error1 = "If paying for a prior warning, please ensure you enter the reference number.";
            var error2 = "Please select a date from the past if paying for a warning.";
            var fieldToCheck = this.warningRefNo;
            var selectedDate = new Date(this.arrivalDate);
            if(fieldToCheck && selectedDate > now){
                this.errors.warningRefNo = true;
                this.errorMsg = error2
            } else if (!fieldToCheck && selectedDate < now){
                this.errors.arrivalDate = true;
                this.errorMsg = error1
            } else {
                this.errors.warningRefNo = false;
                if(this.errorMsg == error1 || this.errorMsg == error2){
                    this.errorMsg = null;
                }
            }
        },
        validateOvernightStay: function(){
            var error = "Please make a selection for overnight stay."
            var fieldToCheck = this.overnightStay;
            if(!fieldToCheck){
                this.errors.overnightStay = true;
                document.getElementById("overnightStayYes").required = true;
                this.errorMsg = error;
            } else {
                this.calculateTotal();
                this.errors.overnightStay = false;
                if(this.errorMsg == error){
                    this.errorMsg = null;
                }
            }
        },
        validateNoOfPeople: function() {
            var error1 = "Please enter at least 1 person for admission booking.";
            var error2 = "Cannot purchase for a negative value for people.";
            var totalP = parseInt(this.noOfAdults) + parseInt(this.noOfConcessions) + parseInt(this.noOfChildren) + parseInt(this.noOfInfants);
            if(!totalP || totalP == 0){
                this.errors.noOfAdults = true;
                this.errors.noOfConcessions = true;
                this.errors.noOfChildren = true;
                this.errors.noOfInfants = true;
                this.errorMsg = error1;
            } else if (parseInt(this.noOfAdults) < 0 || parseInt(this.noOfConcessions) < 0 || parseInt(this.noOfChildren) < 0 || parseInt(this.noOfInfants) < 0){
                this.errors.noOfAdults = true;
                this.errors.noOfConcessions = true;
                this.errors.noOfChildren = true;
                this.errors.noOfInfants = true;
                this.errorMsg = error2;
            } else {
                this.calculateTotal();
                this.errors.noOfAdults = false;
                this.errors.noOfConcessions = false;
                this.errors.noOfChildren = false;
                this.errors.noOfInfants = false;
                if(this.errorMsg == error1 || this.errorMsg == error2){
                    this.errorMsg = null;
                }
            }
        },
        setPrices: function(data, callback){
            this.currentCostDateStart = data.period_start;
            this.adultCost = data.adult_cost;
            this.adultOvernightCost = data.adult_overnight_cost;
            this.childrenCost = data.children_cost;
            this.childrenOvernightCost = data.children_overnight_cost;
            this.infantCost = data.infant_cost;
            this.infantOvernightCost = data.infant_overnight_cost;
            this.familyCost = data.family_cost;
            this.familyOvernightCost = data.family_overnight_cost;
            callback();
        },
        getPrices: function(callback){
            console.log(this.arrivalDate);
            var date = moment(this.arrivalDate).format('YYYY-MM-DD');
            var location = $('#location').val();
            var data = {
                'date': date,
                'location': location,
            }
            $.ajax({
                url: process.env.PARKSTAY_URL + "/api/admissions/get_price_by_location.json/",
                method: 'GET',
                data: data,
                dataType: 'json',
                success: (function(data){
                    if(data.price.period_end == 'null'){
                        var temp = new Date();
                        this.currentCostDateEnd = (temp.getDate + 1000);
                    } else {
                        this.currentCostDateEnd = data.price.period_end;
                    }
                    this.setPrices(data.price, callback);

                    // for(var i = 0; i < data.length; i++){
                    //     var checkDate = Date.parse(date);
                    //     var checkingDate = Date.parse(data[i].period_start);
                    //     if(data[i].period_end == null){
                    //         if(checkingDate <= checkDate){
                    //             var temp = new Date();
                    //             this.currentCostDateEnd = (temp.getDate + 1000);
                    //             this.setPrices(data[i], callback);
                    //         }
                    //     } else {
                    //         var checkingDate2 = Date.parse(data[i].period_end);
                    //         if(checkingDate <= checkDate && checkingDate2 >= checkDate){
                    //             this.currentCostDateEnd = data[i].period_end;
                    //             this.setPrices(data[i], callback);
                    //         }
                    //     }
                    // }
                    return false;                
                }).bind(this)
            }); 
        },
        loadTerms: function() { 
           var terms = $('#terms').val();
           console.log(terms);
           window.open(terms,'_terms');

	},
        calculateTotal: function(){
            var date = new Date(this.arrivalDate);
            var temp = date.toISOString().substring(0,10);
            
            if(!(this.currentCostDateStart <= temp && this.currentCostDateEnd >= temp)){
                this.getPrices(this.prepareTotal);
            } else {
                this.prepareTotal();
            }    
        },
        prepareTotal: function(){
            var family = 0;
            var adults = parseInt(this.noOfAdults);
            var children = parseInt(this.noOfChildren);

            if (adults > 1 && children > 1) {
                if (adults == children) {
                    if (adults % 2 == 0) {
                        family = adults/2
                        adults = 0
                        children = 0
                    } else {
                        adults -= 1
                        family = adults/2
                        adults = 1
                        children = 1
                    }
                }
                else if (adults > children) {
                    if (children % 2 == 0){
                        family = children/2
                        adults -= children
                        children = 0
                    } else{
                        children -= 1
                        family = children/2
                        adults -= children
                        children = 1
                    }
                }
                else{
                    if (adults % 2 == 0){
                        family = adults/2
                        children -= adults
                        adults = 0
                    } else{
                        adults -= 1
                        family = adults/2
                        children -= adults
                        adults = 1
                    } 
                }
            }
            if (this.overnightStay == "yes"){
                this.total = (this.adultOvernightCost * adults) + (this.childrenOvernightCost * children) + (this.infantOvernightCost * this.noOfInfants) + (this.familyOvernightCost * family);
            } else {
                this.total = (this.adultCost * adults) + (this.childrenCost * children) + (this.infantCost * this.noOfInfants) + (this.familyCost * family);
            }
            return;
        }
        //Other methods can go here.
    },
    mounted: function(){
        let vm = this;
        $(document).foundation();
        this.arrivalEl = $('#dateArrival');

        this.arrivalData = this.arrivalEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                return;
            }
        }).on('changeDate', function (ev) {
            ev.target.dispatchEvent(new CustomEvent('change'));
        }).on('change', function (ev) {
            vm.arrivalData.hide();
            vm.arrivalDate = moment(vm.arrivalData.date);
            vm.validateArrivalDate();
        }).on('keydown', function (ev) {
            if (ev.keyCode == 13) {
                ev.target.dispatchEvent(new CustomEvent('change'));
            }
        }).data('datepicker');

        this.arrivalData.date = this.arrivalDate.toDate();
        this.arrivalData.setValue();
        this.arrivalData.fill();

        //Get the user to autofill the boxes.
        // this.terms = $('#terms').val(); 
        // $('#terms-link').val(this.terms);
        $.ajax({
            url: vm.mooringUrl + "/api/profile",
            method: 'GET',
            dataType: 'json',
            success: (function(data) {
                
                if(data.is_staff == true){

                } else {
                    vm.givenName = data.first_name;
                    vm.lastName = data.last_name;
                    vm.email = data.email;
                    vm.emailConfirm = data.email;
                    document.getElementById("givenName").readOnly = true;
                    document.getElementById("lastName").readOnly = true;
                    document.getElementById("email").readOnly = true;
                    document.getElementById("emailConfirm").readOnly = true;
                }
                
            }.bind(this)),
            error: function(xhr, stat, err) {
                console.log('Could not get user.');
                console.log((xhr.responseJSON && xhr.responseJSON.msg) ? xhr.responseJSON.msg : '"'+err+'" response when communicating with Mooring.');
            }
        });
    }
};

</script>

<style lang='css'>
.label-plain{
    float:left;
    clear: left;
    width: 170px;
    text-align: left;
}
.label-plain2{
    float:left;
    clear: left;
    width: 150px;
    text-align: left;
}

.label-small{
    float:left;
    clear: left;
    text-align: left;
    font-size: 10px;
    margin-top: -18px;
    font-weight:normal;
}

.radio-label{
    margin-left:10px;
}



</style>
