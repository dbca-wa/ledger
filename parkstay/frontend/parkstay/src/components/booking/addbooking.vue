<template lang="html">
    <div id="addBooking">
        <form v-show="!isLoading" name="bookingForm">
            <div class="row">
                <div class="col-lg-12">
                    <div class="well">
                        <div class="row">
                            <div class="col-md-12">
                                <h3 class="text-primary">{{campground.name}}</h3>
                            </div>
                            <div class="col-md-4">
                                  <img v-if="campground.images && campground.images.length>0" :src="campground.images[0].image" width="250" class="img-thumbnail img-responsive">
                                  <img v-else src="https://placeholdit.imgix.net/~text?txtsize=33&txt=Campground&w=250&h=250" alt="campground"  width="250" class="img-thumbnail img-responsive">
                                  <p class="pricing" v-if="priceHistory">
                                      <strong >${{priceHistory[0].rate.adult|formatMoney(2)}}</strong>
                                      <br> <span class="text-muted">Per adult per night</span>
                                  </p>
                                  <p class="pricing" v-else>
                                      <strong >${{0|formatMoney(2)}}</strong>
                                       <span class="text-muted">Per adult per night</span><br>
                                      Select campsite for pricing details
                                  </p>
                            </div>
                            <div class="col-md-8">
                                <div class="row form-horizontal">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <label class="col-md-2 control-label pull-left required"  for="Dates">Dates: </label>
                                            <div class="col-md-4">
                                                <div class="input-group date" id="dateArrival">
                                                    <input type="text" class="form-control" name="arrival" placeholder="Arrival" >
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="input-group date" id="datedeparture">
                                                    <input type="text" class="form-control" name="departure" placeholder="departure">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label class="col-md-2 control-label pull-left required"  for="Campground">Guests: </label>
                                            <div class="col-md-8">
                                                  <div class="dropdown guests">
                                                      <input type="text" class="form-control dropdown-toggle" name="guests" placeholder="Guests" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" v-model="guestsText">
                                                      <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                                          <li v-for="guest in guestsPicker">
                                                              <div class="row">
                                                                  <div class="col-sm-8">
                                                                      <span class="item">
                                                                          {{guest.amount}} {{guest.name}} <span style="color:#888;font-weight:300;font-size:12px;">{{guest.description}}</span>
                                                                      </span>
                                                                      <br/><a href="#" class="text-info" v-show="guest.helpText">{{guest.helpText}}</a>
                                                                  </div>
                                                                  <div class="pull-right">
                                                                      <div class="btn-group btn-group-sm">
                                                                        <button type="button" class="btn btn-guest" @click.prevent.stop="addGuestCount(guest)"><span class="glyphicon glyphicon-plus"></span></button>
                                                                        <button type="button" class="btn btn-guest" @click.prevent.stop="removeGuestCount(guest)"><span class="glyphicon glyphicon-minus"></span></button>
                                                                      </div>
                                                                  </div>
                                                              </div>
                                                          </li>
                                                      </ul>
                                                  </div>
                                            </div>
                                        </div>
                                    </div>
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
                            <div class="col-lg-12">
                                <h3 class="text-primary">Camp Site</h3>
                                <p>
                                    Click <a href="#">here</a> to open the map of the campground to help you select the preferred campsite
                                </p>
                                <div class="row">
                                  <div class="col-md-6">
                                      <div class="form-group">
                                        <label for="Campsite" class="required">Campsite</label>
                                        <select class="form-control" name="campsite" v-model="selected_campsite">
                                            <option value=""></option>
                                            <option v-for="campsite in campsites" :value="campsite.id">{{campsite.name}} - {{campsite.type}}</option>
                                        </select>
                                      </div>
                                  </div>
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
                            <div class="col-lg-6">
                                <div class="row">
                                    <div class="col-lg-12">
                                        <h3 class="text-primary">Personal Details</h3>
                                    </div>
                                </div>
                                <div class="row">
                                  <div class="col-md-12">
                                      <div class="form-group">
                                        <label for="Email" class="required">Email</label>
                                        <input type="text" name="email" class="form-control" v-model="booking.email" list="matched_emails" @change="autofillUser()" @keyup="fetchUsers()"  >
                                        <datalist id="matched_emails">
                                            <option v-if="usersEmail" v-for="email in usersEmail" :value="email"></option>
                                        </datalist>
                                      </div>
                                  </div>
                                  <div class="col-md-6" v-show="false">
                                      <div class="form-group">
                                        <label for="Confirm Email" class="required">Confirm Email</label>
                                        <input type="text" name="confirm_email" class="form-control">
                                      </div>
                                  </div>
                                </div>
                                <div class="row">
                                  <div class="col-md-6">
                                      <div class="form-group">
                                        <label for="First Name" class="required">First Name</label>
                                        <input type="text" name="firstname" class="form-control" v-model="booking.firstname">
                                      </div>
                                  </div>
                                  <div class="col-md-6">
                                      <div class="form-group">
                                        <label for="Surname" class="required">Surname</label>
                                        <input type="text" name="surname" class="form-control" v-model="booking.surname">
                                      </div>
                                  </div>
                                </div>
                                <div class="row">
                                  <div class="col-md-6">
                                      <div class="form-group">
                                        <label for="Postcode" class="required">Postcode</label>
                                        <input type="text" name="postcode" class="form-control" v-model="booking.postcode">
                                      </div>
                                  </div>
                                  <div class="col-md-6">
                                      <div class="form-group">
                                        <label for="Country" class="required">Country</label>
                                        <input type="text" name="country" class="form-control" v-model="booking.country" >
                                      </div>
                                  </div>
                                </div>
                                <div class="row">
                              <div class="col-md-6">
                                  <div class="form-group">
                                    <label for="Phone" class="required">Phone <span class="text-muted">(mobile prefered)</span></label>
                                    <input type="text" name="phone" class="form-control" v-model="booking.phone">
                                  </div>
                              </div>
                              <div class="col-md-6" v-if="!park.entry_fee_required">
                                  <div class="form-group">
                                    <label for="Vehicle Registration">Vehicle Registration</label>
                                    <input type="text" name="vehicle" class="form-control" v-model="booking.vehicle">
                                  </div>
                              </div>
                            </div>
                            </div>
                            <div class="col-lg-6" v-if="park.entry_fee_required">
                                <div class="row">
                                    <div class="col-lg-12" v-if="park.entry_fee_required">
                                        <h3 class="text-primary">Park Entry Fees <small>(${{parkPrices.vehicle|formatMoney(2)}}/per vehicle)</small></h3>
                                    </div>
                                </div>
                                <div class="row">
                                  <div class="col-md-12">
                                      <div class="form-group">
                                          <label for="vehicles" class="required">Number of Vehicles</label>
                                          <div class="dropdown guests">
                                              <input type="number" min="0" max="10" name="vehicles" class="form-control dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" readonly="true" v-model="booking.parkEntry.vehicles" @change="updatePrices()">
                                              <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                                  <li v-for="park_entry in parkEntryPicker">
                                                      <div class="row">
                                                          <div class="col-sm-8">
                                                              <span class="item">
                                                                  {{park_entry.amount}} {{park_entry.name}} <span style="color:#888;font-weight:300;font-size:12px;"></span>
                                                              </span>
                                                              <br/><a href="#" class="text-info" v-show="park_entry.helpText">{{park_entry.helpText}}</a>
                                                          </div>
                                                          <div class="pull-right">
                                                              <div class="btn-group btn-group-sm">
                                                                <button type="button" class="btn btn-guest" @click.prevent.stop="addVehicleCount(park_entry)"><span class="glyphicon glyphicon-plus"></span></button>
                                                                <button type="button" class="btn btn-guest" @click.prevent.stop="removeVehicleCount(park_entry)"><span class="glyphicon glyphicon-minus"></span></button>
                                                              </div>
                                                          </div>
                                                      </div>
                                                  </li>
                                              </ul>
                                          </div>
                                      </div>
                                  </div>
                                </div>
                                <div class="row" v-for="v in parkEntryVehicles">
                                  <div class="col-md-12">
                                      <div class="form-group">
                                        <label for="Phone" class="required">{{v.description}}</label>
                                        <input type="text" name="regos[]" class="form-control" required="required" v-model="v.rego" @change="validateRego">
                                      </div>
                                  </div>
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
                                <label for="Total Price">Total Price <span class="text-muted">(GST inclusive.Park entry fee(where applicable) not included.)</span></label>
                                <div class="input-group">
                                  <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                  <input type="text" class="form-control" :placeholder="0|formatMoney(2)" :value="booking.price|formatMoney(2)" readonly="true">
                                </div>
                              </div>
                          </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <p class="text-muted">
                                    Payments will be recorded against the booking once the booking is completed and the payment is received.
                                </p>
                            </div>
                            <div class="col-md-6">
                              <button type="button" class="btn btn-primary btn-lg pull-right" @click="bookNow()"> Book</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
        <loader :isLoading="isLoading" >{{loading.join(' , ')}}...</loader>
    </div>

</template>

<script>
import {$,awesomplete,Moment,api_endpoints,validate,formValidate,helpers} from "../../hooks.js";
import loader from '../utils/loader.vue';
export default {
    name:"addBooking",
    data:function () {
        let vm =this;
        return{
            bookingForm:null,
            countries:[],
            selected_campsite:"",
            selected_arrival:"",
            selected_departure:"",
            priceHistory:null,
            booking:{
                arrival:"",
                departure:"",
                guests:{
                    adult:0,
                    concession:0,
                    child:0,
                    infant:0
                },
                campground:"",
                campsite:"",
                email:"",
                firstname:"",
                surname:"",
                postcode:"",
                country:"",
                phone:"",
                vehicle:"",
                price:"0",
                parkEntry:{
                    vehicles:0,
                },
                entryFees:{
                    vehicles : 0,
                    motorbike: 0,
                    concession:0,
                    entry_fee: 0,
                    regos:[]
                }
            },
            campsites:[],
            loading:[],
            campground:{},
            guestsText:"",
            guestsPicker:[
                {
                    id:"adult",
                    name:"Adults (no concession)",
                    amount:0,
                    description: ""
                },
                {
                    id:"concession",
                    name:"Concession",
                    amount:0,
                    description: "",
                    helpText:"accepted concession cards"
                },
                {
                    id:"child",
                    name:"Children",
                    amount:0,
                    description: "Ages 6-16"
                },
                {
                    id:"infant",
                    name:"Infants",
                    amount:0,
                    description: "Ages 0-5"
                },
            ],
            parkEntryPicker:[
                {
                    id:"vehicle",
                    name:"Vehicle",
                    amount:0,
                    price:0,
                    description: "Vehicle Regestration",
                    rego:""
                },
                {
                    id:"concession",
                    name:"Concession",
                    amount:0,
                    price:0,
                    description: "Concession Vehicle Regestration",
                    helpText:"accepted concession cards",
                    rego:""
                },
                {
                    id:"motorbike",
                    name:"Motorbike",
                    amount:0,
                    price:0,
                    description: "Motorbike Regestration",
                    rego:""
                }
            ],
            users:[],
            usersEmail:[],
            park:{
                entry_fee_required:false,
                entry_fee:0
            },
            parkEntryVehicles:[],
            parkPrices: {}
        };
    },
    components:{
        loader
    },
    computed:{
        isLoading:function () {
            return this.loading.length > 0;
        },
        maxEntryVehicles:function () {
            let vm = this;
            var entries =  ( vm.booking.parkEntry.vehicles <= 10 ) ? vm.booking.parkEntry.vehicles :  10;
            vm.booking.parkEntry.vehicles = entries;
            return entries;
        }
    },
    filters:{
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
    watch:{
        selected_campsite:function () {
            let vm = this;
            vm.updatePrices();
        },
        selected_arrival:function () {
            let vm = this;
            vm.updatePrices();
            vm.fetchCampsites();
        },
        selected_departure:function () {
            let vm = this;
            vm.updatePrices();
            vm.fetchCampsites();
        }
    },
    methods:{
        validateRego:function (e) {
            formValidate.isNotEmpty(e.target);
        },
        updatePrices:function () {
            let vm = this;
            vm.booking.campsite = vm.selected_campsite;
            vm.booking.price = 0;
            if (vm.selected_campsite) {
                if (vm.booking.arrival && vm.booking.departure) {
                    var arrival = Moment(vm.booking.arrival, "YYYY-MM-DD");
                    var departure = Moment(vm.booking.departure, "YYYY-MM-DD");
                    var nights = departure.diff(arrival,'days');
                    vm.loading.push('updating prices');
                    vm.$http.get(api_endpoints.campground_current_price(vm.campground.id,arrival.format("YYYY-MM-DD"),departure.format("YYYY-MM-DD"))).then((response)=>{
                        vm.priceHistory = null;
                        vm.priceHistory = response.body;
                        vm.generateBookingPrice();
                        vm.loading.splice('updating prices',1);
                    },(error)=>{
                        console.log(error);
                        vm.loading.splice('updating prices',1);
                    });
                }
            }
        },
        fetchCountries:function (){
            let vm =this;
            vm.loading.push('fetching countries');
            vm.$http.get(api_endpoints.countries).then((response)=>{
                vm.countries = response.body;
                var list = [];
                $.each(vm.countries,function (i,c) {
                    list.push(c.name);
                });
                vm.$nextTick(function () {
                    var input = vm.bookingForm.country;
                    var autoc = new awesomplete(input, {
                        list,
                        minChars: 1,
                        maxItems:5,
                        autoFirst: true,
                        sort:function (text,input) {
                            return text > input;
                        }
                    });
                    window.addEventListener('awesomplete-selectcomplete',function (e) {
                        vm.booking.country = e.text.value;
                    });
                    vm.loading.splice('fetching countries',1);
                });

            },(response)=>{
                console.log(response);
                vm.loading.splice('fetching countries',1);
            });
        },
        fetchCampsites:function () {
            let vm = this;
            if(vm.selected_arrival && vm.selected_departure){
                vm.loading.push('fetching campsites');
                vm.$http.get(api_endpoints.available_campsites(vm.booking.campground,vm.booking.arrival,vm.booking.departure)).then((response)=>{
                    vm.campsites = response.body;
                    if (vm.campsites.length >0) {
                        vm.selected_campsite =vm.campsites[0].id;
                    }
                    vm.loading.splice('fetching campsites',1);
                },(response)=>{
                    console.log(response);
                    vm.loading.splice('fetching campsites',1);
                });
            }
        },
        fetchCampground:function () {
            let vm =this;
            vm.loading.push('fetching campground');
            var cgId = vm.$route.params.cg;
            vm.$http.get(api_endpoints.campground(cgId)).then((response)=>{
                vm.campground = response.body;
                vm.booking.campground = vm.campground.id;
                vm.fetchCampsites();
                vm.fetchPark();
                vm.addEventListeners();
                vm.loading.splice('fetching campground',1);
            },(error)=>{
                console.log(error);
                vm.loading.splice('fetching campground',1);
            });
        },
        fetchPark:function () {
            let vm =this;
            vm.loading.push('fetching park');
            vm.$http.get(api_endpoints.park(vm.campground.park)).then((response)=>{
                vm.park = response.body;
                vm.loading.splice('fetching park',1);
            },(error)=>{
                console.log(error);
                vm.loading.splice('fetching park',1);
            });
        },
        addEventListeners:function(){
            let vm = this;
            var arrivalPicker = $(vm.bookingForm.arrival).closest('.date');
            var departurePicker = $(vm.bookingForm.departure).closest('.date');
            arrivalPicker.datetimepicker({
                format: 'DD/MM/YYYY',
                minDate: new Date(),
                maxDate: Moment().add(parseInt(vm.campground.max_advance_booking),'days')
            });
            departurePicker.datetimepicker({
                format: 'DD/MM/YYYY',
                useCurrent: false,
            });
            arrivalPicker.on('dp.change', function(e){
                vm.booking.arrival = arrivalPicker.data('DateTimePicker').date().format('YYYY/MM/DD');
                vm.selected_arrival = vm.booking.arrival;
                vm.selected_departure = "";
                vm.booking.departure = "";
                departurePicker.data("DateTimePicker").minDate(e.date);
                departurePicker.data("DateTimePicker").date(null);
            });
            departurePicker.on('dp.change', function(e){
                if (departurePicker.data('DateTimePicker').date()) {
                    vm.booking.departure = departurePicker.data('DateTimePicker').date().format('YYYY/MM/DD');
                    vm.selected_departure= vm.booking.departure;
                }else{
                    vm.booking.departure = null;
                    vm.selected_departure= vm.booking.departure;
                }
            });
        },
        addGuestCount:function (guest) {
            let vm =this;
            guest.amount += 1;
            switch (guest.id) {
                case 'adult':
                    vm.booking.guests.adult = guest.amount;
                    break;
                case 'concession':
                    vm.booking.guests.concession = guest.amount;
                    break;
                case 'child':
                    vm.booking.guests.child = guest.amount;
                    break;
                case 'infant':
                    vm.booking.guests.infant = guest.amount;
                    break;
                default:

            }
            vm.generateGuestCountText();
        },
        removeGuestCount:function (guest) {
            let vm =this;
            guest.amount = (guest.amount > 0) ?  guest.amount-1: 0;
            switch (guest.id) {
                case 'adult':
                    vm.booking.guests.adult = guest.amount;
                    break;
                case 'concession':
                    vm.booking.guests.concession = guest.amount;
                    break;
                case 'child':
                    vm.booking.guests.child = guest.amount;
                    break;
                case 'infant':
                    vm.booking.guests.infant = guest.amount;
                    break;
                default:

            }
            vm.generateGuestCountText();
        },
        generateGuestCountText:function () {
            let vm =this;
            var text = "";
            $.each(vm.guestsPicker,function (i,g) {
                (i != vm.guestsPicker.length-1) ? (g.amount > 0 )?text += g.amount+" "+g.name+",  ":"" :(g.amount > 0 ) ? text += g.amount+" "+g.name+" ":"";
            });
            vm.guestsText = text.replace(/,\s*$/, "");
            vm.generateBookingPrice();
        },
        generateBookingPrice:function () {
            let vm =this;
            vm.booking.price = 0;
            if (vm.park.entry_fee_required){
                vm.fetchParkPrices(function(){

                    $.each(vm.priceHistory,function (i,price) {
                        for (var guest in vm.booking.guests) {
                            if (vm.booking.guests.hasOwnProperty(guest)) {
                                vm.booking.price += vm.booking.guests[guest] * price.rate[guest];
                            }
                        }

                    });
                    vm.booking.entryFees.entry_fee = 0;
                    $.each(vm.parkEntryVehicles,function (i,entry) {
                        entry = JSON.parse(JSON.stringify(entry));
                        if (vm.parkPrices) {
                            switch (entry.id) {
                                case 'vehicle':
                                    vm.booking.entryFees.entry_fee += parseInt(vm.parkPrices.vehicle);
                                    vm.booking.entryFees.vehicle++;
                                    break;
                                case 'motorbike':
                                    vm.booking.entryFees.entry_fee +=  parseInt(vm.parkPrices.motorbike);
                                    vm.booking.entryFees.motorbike++;
                                    break;
                                case 'concession':
                                    vm.booking.entryFees.entry_fee +=  parseInt(vm.parkPrices.concession);
                                    vm.booking.entryFees.concession++;
                                    break;

                            }
                        }
                    });

                    vm.booking.price = vm.booking.price + vm.booking.entryFees.entry_fee;

                });
            }
        },
        fetchUsers:function (event) {
            let vm = this;
            vm.$http.get(api_endpoints.usersLookup(vm.booking.email)).then((response)=>{
                vm.users = response.body;
                vm.usersEmail = [];
                $.each(vm.users,function (i,u) {
                    vm.usersEmail.push(u.email);
                });
            });
        },
        fetchParkPrices:function (calcprices) {
            let vm = this;
            if (vm.booking.arrival) {
                var arrival = Moment(vm.booking.arrival, "YYYY-MM-DD").format("YYYY-MM-DD");
                vm.$http.get(api_endpoints.park_current_price(vm.park.id,arrival)).then((response)=>{
                    vm.parkPrices = response.body;
                    calcprices();
                });
            }else{
                vm.parkPrices = {};
                calcprices();
            }

        },
        autofillUser:function (event) {
            let vm =this;
            $.each(vm.users,function (i, user) {
                if (user.email == vm.booking.email) {
                    vm.booking.firstname = user.first_name;
                    vm.booking.surname = user.last_name;
                    vm.booking.phone = user.mobile_number;
                    if (user.profile_addresses[0]) {
                        vm.booking.postcode = user.profile_addresses[0].postcode;
                        vm.booking.country = user.profile_addresses[0].country;
                    }
                    return false;
                }
            })
        },
        bookNow:function () {
            let vm = this;
            if (vm.isFormValid()) {
                vm.loading.push('processing booking');
                vm.booking.entryFees = {
                    vehicle : 0,
                    motorbike: 0,
                    concession:0,
                    entry_fee: 0,
                    regos:[]
                };
                $.each(vm.parkEntryVehicles,function (i,entry) {
                    entry = JSON.parse(JSON.stringify(entry));
                    if (entry.rego != null || entry.rego != "null") {
                        vm.booking.entryFees.regos.push({
                            type:entry.id,
                            rego:entry.rego
                        });
                    }
                    switch (entry.id) {
                        case 'vehicle':
                            vm.booking.entryFees.entry_fee += parseInt(vm.parkPrices.vehicle);
                            vm.booking.entryFees.vehicle++;
                            break;
                        case 'motorbike':
                            vm.booking.entryFees.entry_fee +=  parseInt(vm.parkPrices.motorbike);
                            vm.booking.entryFees.motorbike++;
                            break;
                        case 'concession':
                            vm.booking.entryFees.entry_fee +=  parseInt(vm.parkPrices.concession);
                            vm.booking.entryFees.concession++;
                            break;

                    }
                });
                var booking = {
                    arrival:vm.booking.arrival,
                    departure:vm.booking.departure,
                    guests:vm.booking.guests,
                    campsite:vm.booking.campsite,
                    parkEntry:vm.booking.entryFees,
                    costs:{
                        campground:vm.priceHistory,
                        parkEntry:vm.parkPrices,
                        total:vm.booking.price
                    },
                    customer:{
                        email:vm.booking.email,
                        first_name:vm.booking.firstname,
                        last_name:vm.booking.surname,
                        phone:vm.booking.phone,
                        country:vm.booking.country,
                        postcode:vm.booking.postcode,
                    }
                }

                vm.$http.post(api_endpoints.bookings,JSON.stringify(booking),{
                    emulateJSON:true,
                    headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                }).then((success)=>{
                    location.reload();
                },(error)=>{
                    console.log(error);
                    vm.loading.splice('processing booking',1);
                });
            }

        },
        isFormValid:function () {
            let vm =this;
            return (vm.validateParkEntry() && $(vm.bookingForm).valid());
        },
        validateParkEntry:function () {
            let vm = this;
            var isValid = true;
            if (vm.booking.parkEntry.vehicles > 0) {
                if (vm.booking.parkEntry.vehicles > vm.booking.parkEntry.regos) {
                    isValid = false;
                }
            }
            return isValid;
        },
        addFormValidations: function() {
            $(this.bookingForm).validate({
                rules: {
                    arrival: "required",
                    departure: "required",
                    guests: "required",
                    campsite: "required",
                    email: {
                        required: true,
                        email: true
                    },
                    firstname: "required",
                    surname: "required",
                    phone: "required",
                    postcode: "required",
                    country: "required",
                    price_level: "required"
                },
                messages: {
                    firstname: "fill in all details",
                },
                showErrors: function(errorMap, errorList) {
                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);

                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });

                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");

                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
        },
        addVehicleCount:function (park_entry) {

            let vm = this;
            var count = vm.booking.parkEntry.vehicles
            if( park_entry.amount < 10 && count < 10){
                park_entry.amount = (park_entry.amount < 10)?park_entry.amount+= 1:park_entry.amount;
                vm.booking.parkEntry.vehicles++;
                vm.parkEntryVehicles.push(JSON.parse(JSON.stringify(park_entry)));
            }
            vm.updatePrices();
        },
        removeVehicleCount:function (park_entry) {
            let vm = this;
            var count = vm.booking.parkEntry.vehicles
            if( park_entry.amount > 0 && count > 0){
                var found = false;
                for (var i = park_entry.amount-1; i >= 0; i--) {
                    for (var j = vm.parkEntryVehicles.length-1; j >=0; j--) {
                        if (park_entry.description == vm.parkEntryVehicles[j].description) {
                            park_entry.amount = (park_entry.amount > 0)?park_entry.amount-=1:park_entry.amount;
                            vm.parkEntryVehicles.splice(j,1);
                            vm.booking.parkEntry.vehicles--;
                            found =true;
                            break;
                        }
                    }
                    if (found) {
                        break;
                    }

                }

            }
            vm.updatePrices();
        },
    },
    mounted:function () {
        let vm = this;
        vm.bookingForm = document.forms.bookingForm;
        vm.fetchCampground();
        vm.fetchCountries();
        vm.addFormValidations();
    }
}

</script>

<style lang="css">
    .pricing{
        margin-left: 25px;
        font-size: 20px;
    }
    .awesomplete{
        width:100%;
    }
    .dropdown-menu:before {
      position: absolute;
      top: -12px;
      left: 12px;
      display: inline-block;
      border-right: 12px solid transparent;
      border-bottom: 12px solid #ccc;
      border-left: 12px solid transparent;
      border-bottom-color: rgba(46, 109, 164, 1);
      content: '';
    }
    .dropdown-menu{
        top:120%;
        width: 300px;
    }
    .guests li{
        padding: 10px;
        margin-right: 10px;
        border-bottom: 1px solid #ccc;
    }
    .guests li:last-child{
        border-bottom: 0;
    }
    .guests.item{
        line-height: 2;
    }
    .btn-guest {
        color: #ccc;
        background-color: #fff;
        border-color: #ccc;
    }
    .required::after{
        content: '*';
        color:red;
    }
</style>
