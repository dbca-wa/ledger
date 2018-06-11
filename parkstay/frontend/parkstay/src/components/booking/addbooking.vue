<template lang="html">
    <div id="addBooking">
        <form v-show="!isLoading" name="bookingForm">
            <div class="row">
                <div class="col-lg-12">
                    <div class="well">
                        <div class="row">
                            <div class="col-md-12">
                                <h3 class="text-primary">Book a Campsite at {{campground.name}}</h3>
                            </div>
                            <div class="col-md-12">
                                <p>Please visit the <a target='_blank' v-bind:href="'/availability_admin/?site_id=' + campground.id "> Campsite Availability checker</a> for expected availability.</p>                          
                            </div>
                            <div class="row">
                                <div class="col-md-12">
                                    <div class="form-group">
                                        <div class="col-md-12">
                                            <label class="control-label pull-left required" for="Dates">Dates: </label>
                                        <div class="col-md-3">
                                            <div class="input-group date" id="dateArrival">
                                                <input type="text" class="form-control" name="arrival" placeholder="Arrival">
                                                <span class="input-group-addon">
                                                    <span class="glyphicon glyphicon-calendar"></span>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="input-group date" id="datedeparture">
                                                <input type="text" class="form-control" name="departure" placeholder="Departure">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="form-group">
                                                <label class="control-label pull-left required"  for="Campground">Guests: </label>
                                                <div class="col-md-8">
                                                    <div class="dropdown guests">
                                                        <input type="text" class="form-control dropdown-toggle" name="guests" placeholder="Guests" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" v-model="guestsText">
                                                        <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                                            <li v-for="guest in guestsPicker">
                                                                <div class="row">
                                                                     <div class="col-sm-4">
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
                    <div class="row">
                        <div class="col-lg-12">
                            <div id="campsite-booking" v-if="campground.site_type == 0">
                                <div v-show="booking.campsites.length < 1" class="col-lg-12 text-center">
                                    <h2>No Campsites Available For The Provided Dates</h2>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row"> 
                        <div class="col-sm-12">
                            <div v-show="booking.campsites.length > 0" >
                                <div class="column table-scroll">
                                    <table class="hover table table-striped table-bordered dt-responsive nowrap" cellspacing="0" width="100%"  name="campsite" v-model="selected_campsite">
                                        <thead>
                                            <tr>
                                                <th class="form-group">Campsite</th>
                                                <th >Sites to book
                                                    <input class="checkbox" type="checkbox" id="selectAll"  v-model="selectAll"> 
                                                </th>
                                            </tr>
                                        </thead>
                                            <tbody><template v-for="campsite in booking.campsites">
                                                <tr>
                                                    <td class="form-group"> {{campsite.name}} - {{campsite.type}}</td>
                                                    <td>
                                                        <input class="checkbox" type="checkbox" :value="campsite.id" v-model="multibook_selected" @change="updatePrices()" number>
                                                    </td>                                              
                                                </tr></template>
                                            </tbody>
                                    </table>
                                </div>                                        
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <div id="campsite-class-booking" v-if="(campground.site_type == 1) || (campground.site_type == 2)">
                                <div class="row">
                                    <div v-show="booking.campsite_classes.length < 1" class="col-lg-12 text-center">
                                        <h2>No Campsites Available For The Provided Dates</h2>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>  
                    <div class="row"> 
                        <div class="col-sm-12">
                            <div v-show="booking.campsite_classes.length > 1">
                                <div class="column table-scroll">
                                    <table class="hover table table-striped table-bordered dt-responsive nowrap"  cellspacing="0" width="100%" name="campsite-type" v-model="selected_campsite_class">
                                        <thead>
                                            <tr>
                                                 <th class="site">Campsite</th>
                                                 <th class="book">Availability</th>
                                                 <th class="numBook">Number of sites to book</th>
                                            </tr>
                                        </thead>
                                        <tbody><template v-for="c in booking.campsite_classes">
                                            <tr>
                                                <td class="site"> {{c.name}} </td>
                                                <td class="book"> {{ c.campsites.length }} available </td>
                                                <td class="numBook">
                                                    <input type="number" min="1" v-bind:max="c.campsites.length" name="campsite-type" class="form-control" v-model="c.selected_campsite_class" @change="updatePrices()">
                                                </td>
                                            </tr></template>
                                        </tbody>
                                    </table>
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
                                        <input type="text" name="email" class="form-control" v-model="booking.email" list="matched_emails" @keyup="fetchUsers()"  >
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
                                        <select class="form-control" name="country" v-model="booking.country">
                                            <option v-for="c in countries" :value="c.iso_3166_1_a2">{{ c.printable_name }}</option>
                                        </select>
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
                                  <div class="col-md-6">
                                      <div class="form-group">
                                        <label class="required">{{v.description}}</label>
                                        <input type="text" class="form-control" required="required" v-model="v.rego" @change="validateRego">
                                      </div>
                                  </div>
                                  <div class="col-md-6">
                                      <div class="form-group">
                                        <label>Entry fee</label>
                                        <input type="checkbox" class="form-control" required="required" v-model="v.entry_fee" @change="updatePrices()">
                                      </div>
                                  </div>
                                </div>
                                <p><b>NOTE:</b> A vehicle entry fee is not required for the holder of a valid Park Pass.</p>
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
                                    <div class="form-group">
                                        <label for="Total Price">Total Price <span class="text-muted">(GST inclusive.)</span></label>
                                        <div class="input-group">
                                        <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                        <input type="text" class="form-control" :placeholder="0|formatMoney(2)" v-bind:value="booking.price|formatMoney(2)" readonly="true">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-lg-12">
                                    <div class="form-group">
                                        <input type="checkbox" name="overrideCharge" class="form control" v-model="overrideCharge"/>
                                        <label for="OverrideCharge">Override price charged </label>
                                        <div class="input-group" v-if="overrideCharge">
                                            <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                            <input type="text" class="form-control" name="overridePrice" :placeholder="0|formatMoney(2)" v-model="booking.override_price">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-lg-12">
                                    <div class="form-group" v-if="overrideCharge">
                                        <reason type="discount" name="overrideReason" v-model="booking.override_reason" ref="reason" required="true"></reason>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="row">
                                <div class="col-lg-12">
                                    <p class="text-muted">
                                        Payments will need to be recorded against the booking once the booking is completed and the payment is received.
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="row">                          
                                <div class="col-lg-12">
                                    <button type="button" class="btn btn-primary btn-lg pull-right" @click="bookNow()"> Book</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </form>
        <loader :isLoading="isLoading" >{{loading.join(' , ')}}...</loader>
        <modal :large="true" @cancel="finishBooking()" :force="true">
            <h1 slot="title">Tax Invoice</h1>
            <div class="row" height="500px">
                <div class="col-lg-12">
                    <iframe id="invoice_frame" width="100%" height="700px" class="embed-responsive-item" frameborder="0"></iframe>
                </div>
            </div>
            <div slot="footer">
                <button id="okBtn" type="button" class="btn btn-default" @click="finishBooking()">Finalize Booking</button>
            </div>
        </modal>
    </div>

</template>

<script>
import {$,awesomplete,Moment,api_endpoints,validate,formValidate,helpers,debounce} from "../../hooks.js";
import loader from '../utils/loader.vue';
import modal from '../utils/bootstrap-modal.vue';
import reason from '../utils/reasons.vue';
export default {
    name:"addBooking",
    data:function () {
        let vm =this;
        return {
            overrideCharge: false,
            isModalOpen:false,
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
                    adult:2,
                    concession:0,
                    child:0,
                    infant:0
                },
                campground:"",
                campsites: [],
                campsite_classes:[],
                email:"",
                firstname:"",
                surname:"",
                postcode:"",
                country:"AU",
                phone:"",
                vehicle:"",
                price:"0",
                override_price:"0",
                override_reason:"",
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
            loading:[],
            campground:{},
            guestsText:"",
            guestsPicker:[
                {
                    id:"adult",
                    name:"Adults (no concession)",
                    amount:2,
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
                    description: "Vehicle Registration",
                    rego:"",
                    entry_fee: true
                },
                {
                    id:"concession",
                    name:"Concession",
                    amount:0,
                    price:0,
                    description: "Concession Vehicle Registration",
                    helpText:"accepted concession cards",
                    rego:"",
                    entry_fee: true
                },
                {
                    id:"motorbike",
                    name:"Motorbike",
                    amount:0,
                    price:0,
                    description: "Motorbike Registration",
                    rego:"",
                    entry_fee: true
                }
            ],
            users:[],
            usersEmail:[],
            park:{
                entry_fee_required:false,
                entry_fee:0
            },
            parkEntryVehicles:[],
            parkPrices: {
                "id": null,
                "period_start": null,
                "period_end": null,
                "reason": 1,
                "details": "other",
                "vehicle": "0.00",
                "concession": "0.00",
                "motorbike": "0.00",
                "editable": false
            },
            stayHistory:[],
            arrivalPicker: {},
            departurePicker: {},
            selected_campsite_class:-1,
            booking_type:"campsite",
            booking_types:{
                CAMPSITE: "campsite",
                CLASS:"class"
            },
			multibook_selected:[]
        };
    },
    components:{
        loader,
        modal,
        reason
    },
    computed: {
        isLoading:function () {
            return this.loading.length > 0;
        },
        maxEntryVehicles:function () {
            let vm = this;
            var entries =  ( vm.booking.parkEntry.vehicles <= 10 ) ? vm.booking.parkEntry.vehicles :  10;
            vm.booking.parkEntry.vehicles = entries;
            return entries;
        },
        selectAll:{
            get: function () {
				let vm = this;
                return vm.booking.campsites ? vm.multibook_selected.length == vm.booking.campsites.length : false;
            },
            set: function (value) {
				let vm = this;
                var selected = [];

                if (value) {
                    vm.booking.campsites.forEach(function (campsite) {
                        selected.push(campsite.id);
                    });
                }

                vm.multibook_selected = selected;
				vm.updatePrices();
            }
        },
        selected_campsites: function () {
            let vm = this;
            var results = [];
            if (vm.booking_type == vm.booking_types.CAMPSITE) {
				results = vm.multibook_selected;
            } else {
                vm.booking.campsite_classes.forEach(function (el) {
                    for (var i=0; i<el.selected_campsite_class; i++) {
                        results.push(el.campsites[i]);
                    }
                });
            }
            return results;
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
    watch:{
        selected_campsite:function () {
            let vm = this;
            vm.updatePrices();
        },
        selected_campsite_class:function () {
            let vm =this;
            vm.selected_campsite =vm.booking.campsite_classes[vm.selected_campsite_class].campsites[0];
        },
        selected_arrival:function () {
            let vm = this;
            if (vm.booking.arrival) {
                $.each(vm.stayHistory,function (i,his) {
                    var range = Moment.range(Moment(his.range_start,"DD/MM/YYYY"),Moment(his.range_end,"DD/MM/YYYY"));
                    var arrival = Moment(vm.booking.arrival,"YYYY-MM-DD");
                    if (range.contains(arrival)) {
                        vm.departurePicker.data("DateTimePicker").maxDate(arrival.clone().add(his.max_days,'days'));
                        vm.departurePicker.data("DateTimePicker").date(null);
                    }
                });
            }
            vm.fetchSites();
            vm.updatePrices();
        },
        selected_departure:function () {
            let vm = this;
            vm.fetchSites();
            vm.updatePrices();
        },
        booking_type:function () {
            let vm =this;
            vm.fetchSites();
        }
    },
    methods:{
        fetchSites:function () {
            let vm =this;
            if (vm.booking_type == vm.booking_types.CAMPSITE) {
                vm.fetchCampsites();
            }
            if (vm.booking_type == vm.booking_types.CLASS) {
                vm.fetchCampsiteClasses();
            }
        },
        validateRego:function (e) {
            formValidate.isNotEmpty(e.target);
        },
        updatePrices:function () {
            let vm = this;
            vm.booking.price = 0;
            var campsite_ids = vm.selected_campsites;
            if (vm.selected_campsite) {
                if (vm.booking.arrival && vm.booking.departure) {
                    var arrival = Moment(vm.booking.arrival, "YYYY-MM-DD");
                    var departure = Moment(vm.booking.departure, "YYYY-MM-DD");
                    var nights = departure.diff(arrival,'days');
                    vm.$http.post(
                        api_endpoints.campsites_current_price(),
                        {
                            campsites: campsite_ids,
                            arrival: arrival.format("YYYY-MM-DD"),
                            departure: departure.format("YYYY-MM-DD")
                        },
                        {headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}}
                    ).then((response)=>{
                        vm.priceHistory = null;
                        vm.priceHistory = response.body;
                        vm.generateBookingPrice();
                    },(error)=>{
                        console.log(error);
                    });
                }
            }
        },
        fetchCountries:function (){
            let vm =this;
            vm.loading.push('fetching countries');
            vm.$http.get(api_endpoints.countries).then((response)=>{
                vm.countries = response.body;
                vm.loading.splice('fetching countries',1);
            },(response)=>{
                console.log(response);
                vm.loading.splice('fetching countries',1);
            });
        },
        fetchCampsites:function () {
            let vm = this;
            if(vm.selected_arrival && vm.selected_departure){
                vm.loading.push('fetching campsites');
                vm.$http.get(api_endpoints.available_campsites(
                    vm.booking.campground,
                    Moment(vm.booking.arrival, "YYYY-MM-DD").format("YYYY/MM/DD"),
                    Moment(vm.booking.departure, "YYYY-MM-DD").format("YYYY/MM/DD")
                )).then((response)=>{
                    vm.booking.campsites = response.body;
                    if (vm.booking.campsites.length >0) {
                        vm.selected_campsite =vm.booking.campsites[0].id;
                    }
                    vm.loading.splice('fetching campsites',1);
                },(response)=>{
                    console.log(response);
                    vm.loading.splice('fetching campsites',1);
                });
            }
        },
        fetchCampsiteClasses:function () {
            let vm = this;
            if(vm.selected_arrival && vm.selected_departure){
                vm.loading.push('fetching campsite classes');
                vm.$http.get(api_endpoints. available_campsite_classes(
                    vm.booking.campground,
                    Moment(vm.booking.arrival, "YYYY-MM-DD").format("YYYY/MM/DD"),
                    Moment(vm.booking.departure, "YYYY-MM-DD").format("YYYY/MM/DD")
                    )).then((response)=>{
                    vm.booking.campsite_classes = response.body;
                    if (vm.booking.campsite_classes.length >0) {
                        vm.selected_campsite =vm.booking.campsite_classes[0].campsites[0];
                        vm.selected_campsite_class = 0;
                    }
                    vm.loading.splice('fetching campsite classes',1);
                },(response)=>{
                    console.log(response);
                    vm.loading.splice('fetching campsite classes',1);
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
                vm.booking_type = (vm.campground.site_type == 0) ? vm.booking_types.CAMPSITE : vm.booking_types.CLASS;
                vm.fetchStayHistory();
                vm.fetchCampsites();
                vm.fetchPark();
                vm.addEventListeners();
                vm.loading.splice('fetching campground',1);
            },(error)=>{
                console.log(error);
                vm.loading.splice('fetching campground',1);
            });
        },
        fetchStayHistory:function () {
            let vm =this;
            vm.loading.push('fetching stay history');
            vm.$http.get(api_endpoints.campgroundStayHistory(vm.campground.id)).then((response)=>{
                if(response.body.length > 0){
                    vm.stayHistory = response.body;
                }
                vm.loading.splice('fetching stay history',1);
            },(error)=>{
                console.log(error);
                vm.loading.splice('fetching stay history',1);
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
            vm.arrivalPicker = $(vm.bookingForm.arrival).closest('.date');
            vm.departurePicker = $(vm.bookingForm.departure).closest('.date');
            vm.arrivalPicker.datetimepicker({
                format: 'DD/MM/YYYY',
                minDate: Moment().startOf('day'),
                maxDate: Moment().add(parseInt(vm.campground.max_advance_booking),'days')
            });
            vm.departurePicker.datetimepicker({
                format: 'DD/MM/YYYY',
                useCurrent: false,
            });
            vm.arrivalPicker.on('dp.change', function(e){
                vm.booking.arrival = vm.arrivalPicker.data('DateTimePicker').date().format('YYYY-MM-DD');
                vm.selected_arrival = vm.booking.arrival;
                vm.selected_departure = "";
                vm.booking.departure = "";
                var selected_date =  e.date.clone();//Object.assign({},e.date);
                var minDate = selected_date.clone().add(1,'days');
                var maxDate = minDate.clone().add(28,'days');
                vm.departurePicker.data("DateTimePicker").maxDate(maxDate);
                vm.departurePicker.data("DateTimePicker").minDate(minDate);
                vm.departurePicker.data("DateTimePicker").date(null);
            });
            vm.departurePicker.on('dp.change', function(e){
                if (vm.departurePicker.data('DateTimePicker').date()) {
                    vm.booking.departure = vm.departurePicker.data('DateTimePicker').date().format('YYYY-MM-DD');
                    vm.selected_departure= vm.booking.departure;
                }else{
                    vm.booking.departure = null;
                    vm.selected_departure= vm.booking.departure;
                }
            });
            vm.$http.get(api_endpoints.campgroundCampsites(vm.campground.id)).then((response) => {
                var campsites = response.body;
                vm.$http.get(api_endpoints.campsite_current_price(campsites[0].id,Moment().format("YYYY-MM-DD"),Moment().add(1,'days').format("YYYY-MM-DD"))).then((response)=>{
                    vm.priceHistory = null;
                    vm.priceHistory = response.body;
                    vm.loading.splice('updating prices',1);
                },(error)=>{
                    console.log(error);
                    vm.loading.splice('updating prices',1);
                });
            }, (error) => {
                console.log(error);
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
                    vm.updateParkEntryPrices()
                    vm.booking.price = vm.booking.price + vm.booking.entryFees.entry_fee;
                });
            } else {
                $.each(vm.priceHistory,function (i,price) {
                    for (var guest in vm.booking.guests) {
                        if (vm.booking.guests.hasOwnProperty(guest)) {
                            vm.booking.price += vm.booking.guests[guest] * price.rate[guest];
                        }
                    }
                });
            }
        },
        updateParkEntryPrices:function () {
            let vm =this;
            vm.booking.entryFees.entry_fee = 0;
            if (vm.selected_campsite) {
                if (vm.booking.arrival && vm.booking.departure) {
                    $.each(vm.parkEntryVehicles,function (i,entry) {
                        entry = JSON.parse(JSON.stringify(entry));
                        if (vm.parkPrices && entry.entry_fee) {
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
                }
            }
        },
        fetchUsers:debounce(function (event) {
            let vm = this;
            vm.$http.get(api_endpoints.usersLookup(vm.booking.email)).then((response)=>{
                vm.users = response.body;
                vm.usersEmail = [];
                $.each(vm.users,function (i,u) {
                    vm.usersEmail.push(u.email);
                });
                vm.autofillUser();
            });
        }, 1000),
        fetchParkPrices:function (calcprices) {
            let vm = this;
            if (vm.booking.arrival) {
                vm.$http.get(api_endpoints.park_current_price(vm.park.id, vm.booking.arrival)).then((response)=>{
                    var resp = response.body;
                    if (resp.constructor != Array) {
                        vm.parkPrices = response.body;
                    }else{
                        vm.parkPrices.vehicle = "0.00";
                        vm.parkPrices.motorbike = "0.00";
                        vm.parkPrices.concession = "0.00";
                    }
                    calcprices();
                });
            }else{
                vm.parkPrices.vehicle = "0.00";
                vm.parkPrices.motorbike = "0.00";
                vm.parkPrices.concession = "0.00";
                calcprices();
            }
        },
        autofillUser: function (event) {
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
                            type: entry.id,
                            rego: entry.rego,
                            entry_fee: entry.entry_fee
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
                    campsites: vm.selected_campsites,
                    costs:{
                        campground:vm.priceHistory,
                        parkEntry:vm.parkPrices,
                        total:vm.booking.price
                    },
                    override_price:vm.booking.override_price,
                    override_reason:vm.booking.override_reason,
                    customer:{
                        email:vm.booking.email,
                        first_name:vm.booking.firstname,
                        last_name:vm.booking.surname,
                        phone:vm.booking.phone,
                        country:vm.booking.country,
                        postcode:vm.booking.postcode,
                    },
                    regos: vm.booking.entryFees.regos
                }
                vm.$store.dispatch("updateAlert",{
                    visible:false,
                    type:"danger",
                    message: ""
                });
                vm.$http.post(api_endpoints.bookings,JSON.stringify(booking),{
                    emulateJSON:true,
                    headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                }).then((response)=>{
                    vm.loading.splice('processing booking',1);
                    var frame = $('#invoice_frame');
                    frame[0].src = '/ledger/payments/invoice/'+response.body.invoices[0];
                    vm.isModalOpen=true;
                },(error)=>{
                    let error_str = helpers.apiVueResourceError(error);
                    vm.$store.dispatch("updateAlert",{
						visible:true,
						type:"danger",
						message: error_str
					});
                    vm.loading.splice('processing booking',1);
                });
            }
        },
        finishBooking:function () {
            let vm =this;
            vm.isModalOpen =false;
            vm.$router.push({name:"booking-dashboard"});
        },
        isFormValid:function () {
            let vm =this;
            return (vm.validateParkEntry() && vm.overrideChargeReason() && $(vm.bookingForm).valid());
        },
        validateParkEntry:function () {
            let vm = this;
            var validRegos = vm.parkEntryVehicles.reduce(function (acc, el) {
                return acc + (el.rego ? 1 : 0);
            }, 0);

            return (validRegos == vm.parkEntryVehicles.length);
        },
        overrideChargeReason:function () {
            let vm = this;
            if(vm.overrideCharge){
                if(vm.booking.override_price != null && vm.booking.override_reason == "") {                   
                    return false;
                } 
            }
            return true;
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
            vm.booking.price = vm.booking.price - vm.booking.entryFees.entry_fee;
            vm.updateParkEntryPrices();
            vm.booking.price = vm.booking.price + vm.booking.entryFees.entry_fee;
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
            vm.booking.price = vm.booking.price - vm.booking.entryFees.entry_fee;
            vm.updateParkEntryPrices();
            vm.booking.price = vm.booking.price + vm.booking.entryFees.entry_fee;
        },
    },
    mounted:function () {
        let vm = this;
        vm.bookingForm = document.forms.bookingForm;
        vm.fetchCampground();
        vm.fetchCountries();
        vm.addFormValidations();
        vm.generateGuestCountText();
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
    .tab-content{
        padding:15px 0px;
    }
    .nav-tabs{
        margin-top: 15px;
    }
</style>
