<template lang="html">
    <div id="changeBooking">
        <form v-show="!isLoading" name="bookingForm">
            <div class="row">
                <div class="col-lg-12">
                    <div class="well">
                        <div class="row">
                            <div class="col-md-12">
                                <h3 class="text-primary">{{booking.full_name}}</h3>
                            </div>
                            <div class="col-md-8 col-md-offset-1">
                                <div class="row form-horizontal">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <div class="col-md-4">
                                                <label class="control-label pull-left required"  for="Dates">Campground: </label>
                                            </div>
                                            <div class="col-md-8">
                                                <select @change="updateCampground" class="form-control" name="campground" v-model="booking.campground">
                                                    <option v-for="c in onlineCampgrounds" :value="c.id">{{c.name}}</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="form-group" v-if="booking.campground != null || booking.campground != ''">
                                            <div class="col-md-4">
                                                <label class="control-label pull-left required"  for="Dates" >Camp Site: </label>
                                            </div>
                                            <div class="col-md-8" v-if="campsites.length > 0"></div>
                                            <div class="col-md-8" >
                                                <select class="form-control" style="width: 100%;" id="multi-campsites" name="campground" placeholder="" multiple v-model="selected_campsites">
                                                    <option v-for="c in campsites" v-bind:value="c.id">{{c.name}} - {{c.status}}</option>
                                                </select>
                                            </div>                                           
                                            <div class="col-md-8" v-else>
                                                <h4>Sorry, no available campsites were found.</h4>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <div class="col-md-4">
                                                <label class="control-label pull-left required"  for="Dates">Dates: </label>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="input-group date" id="dateArrival">
                                                    <input type="text" class="form-control" name="arrival" placeholder="Arrival" v-model="selected_arrival">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="input-group date" id="datedeparture">
                                                    <input type="text" class="form-control" name="departure" placeholder="Departure" v-model="selected_departure">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <div class="col-md-4">
                                                <label class="control-label pull-left required"  for="Campground">Guests: </label>
                                            </div>
                                            <div class="col-md-8">
                                                  <div class="dropdown guests">
                                                      <input type="text" readonly class="form-control dropdown-toggle" name="guests" placeholder="Guests" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" v-model="guestsText">
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
                            <div class="col-lg-8 col-md-offset-1">
                                <div class="row form-horizontal">
                                  <div class="col-md-12">
                                      <div class="form-group">
                                          <label for="vehicles" class="required col-md-4">Number of Vehicles</label>
                                          <div class="dropdown guests col-md-8">
                                              <input type="number" min="0" max="10" name="vehicles" class="form-control dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" readonly="true" v-model="booking.parkEntry.vehicles">
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
                                    <div class="col-md-6 col-md-offset-4">
                                        <div class="form-group">
                                            <label class="required">{{v.description}}</label>
                                            <input type="text" class="form-control vehicleLookup" required="required" v-model="v.rego" @change="validateRego">
                                        </div>
                                    </div>
                                    <div class="col-md-2" v-if="park.entry_fee_required">
                                        <label>Entry Fee</label>
                                        <div class="form-check">
                                            <label class="form-check-label">
                                                <input class="form-check-input" type="checkbox" required="required" v-model="v.entry_fee" @change="updatePrices">
                                            </label>
                                        </div>
                                  </div>
                                </div>
                            </div>
                            <div class="col-lg-8 col-md-offset-1">
                                <div class="row form-horizontal" v-if="initialised">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <label class="col-md-4" for="Total Price">Total Price <span class="text-muted">(GST inclusive.)</span></label>
                                            <div class="col-md-8">
                                                <div class="input-group">
                                                    <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                                    <input type="text" class="form-control" :placeholder="0|formatMoney(2)" :value="booking_price|formatMoney(2)" readonly="true">
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label class="col-md-4" for="Old Total Price">Old Total Price <span class="text-muted">(GST inclusive.)</span></label>
                                            <div class="col-md-8">
                                                <div class="input-group">
                                                    <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                                    <input type="text" class="form-control" :placeholder="0|formatMoney(2)" :value="booking.cost_total|formatMoney(2)" readonly="true">
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label class="col-md-4" for="Amount Paid">Amount Paid</label>
                                            <div class="col-md-8">
                                                <div class="input-group">
                                                    <span class="input-group-addon">AUD <i class="fa fa-usd"></i></span>
                                                    <input type="text" class="form-control" :placeholder="0|formatMoney(2)" :value="booking.amount_paid|formatMoney(2)" readonly="true">
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                        </div>
                        <div class="row" style="margin-top:20px;">
                            <div class="col-md-12">
                              <button type="button" :disabled="campsites.length == 0" class="btn btn-primary btn-lg pull-right" style="margin-top:15px;" @click="updateNow()">Save Changes</button>
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
import Vue from 'vue'
import booking_helpers from './booking_helpers'
import {
    $,
    awesomplete,
    Moment,
    api_endpoints,
    validate,
    formValidate,
    helpers,
    store
} from "../../hooks.js";
import loader from '../utils/loader.vue';
import {
    mapGetters
} from 'vuex'
import modal from '../utils/bootstrap-modal.vue';
export default {
    name: "ChangeBooking",
    data: function() {
        let vm = this;
        return {
            bookingForm: null,
            selected_campsite: "",
            selected_arrival: "",
            selected_departure: "",
            priceHistory: null,
            booking: {
                parkEntry: {
                    vehicles: 0
                },
            },
            campsites: [],
            loading: [],
            guestsText: "",
            campground: null,
            guestsPicker: [{
                    id: "adults",
                    name: "Adults (no concession)",
                    amount: 0,
                    description: ""
                },
                {
                    id: "concession",
                    name: "Concession",
                    amount: 0,
                    description: "",
                    helpText: "accepted concession cards"
                },
                {
                    id: "children",
                    name: "Children",
                    amount: 0,
                    description: "Ages 6-16"
                },
                {
                    id: "infants",
                    name: "Infants",
                    amount: 0,
                    description: "Ages 0-5"
                },
            ],
            parkEntryPicker: [{
                    id: "vehicle",
                    name: "Vehicle",
                    amount: 0,
                    price: 0,
                    description: "Vehicle Registration",
                    rego: "",
                    entry_fee: false
                },
                {
                    id: "concession",
                    name: "Concession",
                    amount: 0,
                    price: 0,
                    description: "Concession Vehicle Registration",
                    helpText: "accepted concession cards",
                    rego: "",
                    entry_fee: false
                },
                {
                    id: "motorbike",
                    name: "Motorbike",
                    amount: 0,
                    price: 0,
                    description: "Motorbike Registration",
                    rego: "",
                    entry_fee: false
                }
            ],
            park: {
                entry_fee_required: false,
                entry_fee: 0
            },
            parkEntryVehicles: [],
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
            stayHistory: [],
            arrivalPicker: {},
            departurePicker: {},
            campsite_classes: [],
            selected_campsites: [],
            booking_type: "campsite",
            initialised: false,
            fetchingSites: false,
            booking_price: 0,
        };
    },
    components: {
        loader,
        modal
    },
    computed: {
        isLoading: function() {
            return this.loading.length > 0;
        },
        maxEntryVehicles: function() {
            let vm = this;
            var entries = (vm.booking.parkEntry.vehicles <= 10) ? vm.booking.parkEntry.vehicles : 10;
            vm.booking.parkEntry.vehicles = entries;
            return entries;
        },
        onlineCampgrounds(){
            return this.campgrounds.filter(c => c.campground_type === 0);
        },
        ...mapGetters({
            campgrounds: 'campgrounds'
        })
    },
    filters: {
        formatMoney: function(n, c, d, t) {
            c = isNaN(c = Math.abs(c)) ? 2 : c;
            d = d == undefined ? "." : d;
            t = t == undefined ? "," : t;
            var s = n < 0 ? "-" : "";
            var i = String(parseInt(n = Math.abs(Number(n) || 0).toFixed(c)));
            var j = (j = i.length) > 3 ? j % 3 : 0;
            return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
        }
    },
    watch: {
        selected_campsite: function() {
            let vm = this;
            vm.updatePrices();
        },
        selected_arrival: function() {
            let vm = this;
            if (vm.booking.arrival) {
                $.each(vm.stayHistory, function(i, his) {
                    var range = Moment.range(Moment(his.range_start, "DD/MM/YYYY"), Moment(his.range_end, "DD/MM/YYYY"));
                    var arrival = Moment(vm.booking.arrival, "YYYY-MM-DD");
                    if (range.contains(arrival)) {
                        vm.departurePicker.data("DateTimePicker").maxDate(arrival.clone().add(his.max_days, 'days'));
                        vm.departurePicker.data("DateTimePicker").date(null);
                    }
                });
            }
            if (this.initialised){
            }
            vm.fetchSites();
            vm.updatePrices();
        },
        selected_departure: function() {
            let vm = this;
            if (this.initialised){
            }
            vm.fetchSites();
            vm.updatePrices();
        },
        booking_type: function() {
            let vm = this;
            //vm.fetchSites();
        },
    },
    methods: {
        validateRego: function(e) {
            formValidate.isNotEmpty(e.target);
        },
        updateCampground(){
            let vm = this;
            vm.campground = vm.booking.campground ? vm.campgrounds.find(c => parseInt(c.id) === parseInt(vm.booking.campground)) : null;
            vm.fetchSites();
        },
        initSelectTwo:function () {
            let vm = this;
            setTimeout(function () {
                $('#multi-campsites').select2({
                    theme: 'bootstrap',
                    allowClear: true,
                    placeholder: "Select Campsites",
                    tags:false,
                }).
                on("select2:select",function (e) {
                    vm.selected_campsites = $(e.currentTarget).val();
                }).
                on("select2:unselect",function (e) {
                    vm.selected_campsites = $(e.currentTarget).val();
                });
            },100)
        },
        updatePrices: function() {
            let vm = this;
            var campsite_ids = vm.selected_campsites;
            vm.booking.price = 0;
            if (vm.selected_campsite) {
                if (vm.booking.arrival && vm.booking.departure) {
                    var arrival = Moment(vm.selected_arrival, "DD/MM/YYYY");
                    var departure = Moment(vm.selected_departure, "DD/MM/YYYY");
                    var nights = departure.diff(arrival, 'days');
                    vm.loading.push('updating prices');
                    vm.$http.post(api_endpoints.campsites_current_price(),
                    {
                        campsites: campsite_ids,
                        arrival: arrival.format("YYYY-MM-DD"), 
                        departure: departure.format("YYYY-MM-DD")
                    },
                    {headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}}
                    ).then((response) => {
                        vm.priceHistory = null;
                        vm.priceHistory = response.body;
                        vm.generateBookingPrice();
                        vm.loading.splice('updating prices', 1);
                    }, (error) => {
                        console.log(error);
                        vm.loading.splice('updating prices', 1);
                    });
                }
            }
        },
        generateBookingPrice:function () {
            let vm =this;
            vm.booking.price = 0;
            if (vm.park.entry_fee_required){
                vm.fetchParkPrices(function(){
                    $.each(vm.priceHistory,function (i,price) {
                        for (var guest in vm.booking.guests) {
                            switch(guest){
                                case 'adults':
                                vm.booking.price += vm.booking.guests[guest] * parseFloat(price.rate['adult']);
                                break;
                                case 'concession':
                                vm.booking.price += vm.booking.guests[guest] * parseFloat(price.rate['concession']);
                                break;
                                case 'children':
                                vm.booking.price += vm.booking.guests[guest] * parseFloat(price.rate['child']);
                                break;
                                case 'infants':
                                vm.booking.price += vm.booking.guests[guest] * parseFloat(price.rate['infant']);
                                break;
                            }
                        }
                    });
                    vm.updateParkEntryPrices()
                    vm.booking.price = vm.booking.price + vm.booking.entryFees.entry_fee;
                    vm.booking_price = vm.booking.price;
                });
            } else {
                $.each(vm.priceHistory,function (i,price) {
                    for (var guest in vm.booking.guests) {
                        switch(guest){
                            case 'adults':
                            vm.booking.price += vm.booking.guests[guest] * parseFloat(price.rate['adult']);
                            break;
                            case 'concession':
                            vm.booking.price += vm.booking.guests[guest] * parseFloat(price.rate['concession']);
                            break;
                            case 'children':
                            vm.booking.price += vm.booking.guests[guest] * parseFloat(price.rate['child']);
                            break;
                            case 'infants':
                            vm.booking.price += vm.booking.guests[guest] * parseFloat(price.rate['infant']);
                            break;
                        }
                    }
                });
                vm.booking.price = vm.booking.price + vm.booking.entryFees.entry_fee;
                vm.booking_price = vm.booking.price;
            }
        },
        fetchSites: function() {
            let vm = this;
            if (!vm.fetchingSites){
                if (vm.selected_arrival && vm.selected_departure) {
                    vm.fetchingSites = true;
                    vm.loading.push('fetching campsites');
                    vm.$http.get(api_endpoints.available_campsites_booking(vm.booking.campground, vm.booking.arrival, vm.booking.departure,vm.booking.id)).then((response) => {
                        vm.fetchingSites = false;
                        vm.campsites = response.body;
                        if (vm.campsites.length > 0) {
                            let c_lookup = vm.campsites.find(c => parseInt(c.id) === parseInt(vm.selected_campsite));
                            if (c_lookup == null || c_lookup == undefined){
                                vm.selected_campsite = vm.campsites[0].id;
                            }
                        }
                        vm.loading.splice('fetching campsites', 1);
                    }, (response) => {
                        console.log(response);
                        vm.loading.splice('fetching campsites', 1);
                        vm.fetchingSites = false;
                    });
                }
            }
        },
        fetchStayHistory: function() {
            let vm = this;
            vm.loading.push('fetching stay history');
            vm.$http.get(api_endpoints.campgroundStayHistory(vm.campground.id)).then((response) => {
                if (response.body.length > 0) {
                    vm.stayHistory = response.body;
                }
                vm.loading.splice('fetching stay history', 1);
            }, (error) => {
                console.log(error);
                vm.loading.splice('fetching stay history', 1);
            });

        },
        fetchPark: function() {
            let vm = this;
            vm.loading.push('fetching park');
            vm.$http.get(api_endpoints.park(vm.campground.park)).then((response) => {
                vm.park = response.body;
                vm.loading.splice('fetching park details', 1);
            }, (error) => {
                console.log(error);
                vm.loading.splice('fetching park details', 1);
            });
        },
        addEventListeners: function() {
            let vm = this;
            vm.arrivalPicker = $(vm.bookingForm.arrival).closest('.date');
            vm.departurePicker = $(vm.bookingForm.departure).closest('.date');
            vm.arrivalPicker.datetimepicker({
                format: 'DD/MM/YYYY',
                minDate: Moment().startOf('day'),
            });
            vm.departurePicker.datetimepicker({
                format: 'DD/MM/YYYY',
                useCurrent: false,
            });

            vm.arrivalPicker.on('dp.change', function(e) {
                vm.booking.arrival = vm.arrivalPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
                vm.selected_arrival = vm.booking.arrival;
                vm.selected_departure = "";
                vm.booking.departure = "";
                var selected_date = e.date.clone(); //Object.assign({},e.date);
                var minDate = selected_date.clone().add(1, 'days');
                vm.departurePicker.data("DateTimePicker").minDate(minDate);
                // Set the departure date to a day after the arrival date
                vm.departurePicker.data("DateTimePicker").date(minDate);
            });
            vm.departurePicker.on('dp.change', function(e) {
                if (vm.departurePicker.data('DateTimePicker').date()) {
                    vm.booking.departure = vm.departurePicker.data('DateTimePicker').date().format('DD/MM/YYYY');
                    vm.selected_departure = vm.booking.departure;
                } else {
                    vm.booking.departure = null;
                    vm.selected_departure = vm.booking.departure;
                }
            });
            // Set the initial minimum departure date for the booking
            vm.departurePicker.data("DateTimePicker").minDate(Moment(vm.selected_arrival,"DD/MM/YYYY").add(1,'days'));
        },
        addGuestCount: function(guest) {
            let vm = this;
            guest.amount += 1;
            switch (guest.id) {
                case 'adults':
                    vm.booking.guests.adults = guest.amount;
                    break;
                case 'concession':
                    vm.booking.guests.concession = guest.amount;
                    break;
                case 'children':
                    vm.booking.guests.children = guest.amount;
                    break;
                case 'infants':
                    vm.booking.guests.infants = guest.amount;
                    break;
                default:

            }
            vm.generateGuestCountText();
        },
        removeGuestCount: function(guest) {
            let vm = this;
            guest.amount = (guest.amount > 0) ? guest.amount - 1 : 0;
            switch (guest.id) {
                case 'adults':
                    vm.booking.guests.adults = guest.amount;
                    break;
                case 'concession':
                    vm.booking.guests.concession = guest.amount;
                    break;
                case 'children':
                    vm.booking.guests.children = guest.amount;
                    break;
                case 'infants':
                    vm.booking.guests.infants = guest.amount;
                    break;
                default:

            }
            vm.generateGuestCountText();
        },
        generateGuestCountText: function() {
            let vm = this;
            var text = "";
            $.each(vm.guestsPicker, function(i, g) {
                (i != vm.guestsPicker.length - 1) ? (g.amount > 0) ? text += g.amount + " " + g.name + ",  ": "": (g.amount > 0) ? text += g.amount + " " + g.name + " " : "";
            });
            vm.guestsText = text.replace(/,\s*$/, "");
            if(vm.initialised){
                vm.generateBookingPrice();
            }
        },
        updateParkEntryPrices: function() {
            let vm = this;
            vm.booking.entryFees.entry_fee = 0;
            if (vm.selected_campsite) {
                if (vm.booking.arrival && vm.booking.departure) {
                    $.each(vm.parkEntryVehicles, function(i, entry) {
                        entry = JSON.parse(JSON.stringify(entry));
                        if (vm.parkPrices && entry.entry_fee) {
                            switch (entry.id) {
                                case 'vehicle':
                                    vm.booking.entryFees.entry_fee += parseInt(vm.parkPrices.vehicle);
                                    //vm.booking.entryFees.vehicle++;
                                    break;
                                case 'motorbike':
                                    vm.booking.entryFees.entry_fee += parseInt(vm.parkPrices.motorbike);
                                    //vm.booking.entryFees.motorbike++;
                                    break;
                                case 'concession':
                                    vm.booking.entryFees.entry_fee += parseInt(vm.parkPrices.concession);
                                    //vm.booking.entryFees.concession++;
                                    break;
                                default:
                                    break;
                            }
                        }
                    });
                }
            }
        },
        fetchParkPrices: function(calcprices) {
            let vm = this;
            if (vm.booking.arrival) {
                var arrival = Moment(vm.booking.arrival, "DD/MM/YYYY").format("YYYY-MM-DD");
                vm.$http.get(api_endpoints.park_current_price(vm.park.id, arrival)).then((response) => {
                    var resp = response.body;
                    if (resp.constructor != Array) {
                        vm.parkPrices = response.body;
                    } else {
                        vm.parkPrices.vehicle = "0.00";
                        vm.parkPrices.motorbike = "0.00";
                        vm.parkPrices.concession = "0.00";
                    }
                    calcprices();
                });
            } else {
                vm.parkPrices.vehicle = "0.00";
                vm.parkPrices.motorbike = "0.00";
                vm.parkPrices.concession = "0.00";
                calcprices();
            }

        },
        updateNow(){
            let vm = this;
            let booking = {};
            // Deal with booking vehicles
            if (vm.isFormValid()){
                vm.loading.push('updating booking');
                booking.entryFees = {
                    vehicle: 0,
                    motorbike: 0,
                    concession: 0,
                    regos: []
                };
                $.each(vm.parkEntryVehicles, function(i, entry) {
                    entry = JSON.parse(JSON.stringify(entry));
                    if (entry.rego != null || entry.rego != "null") {
                        booking.entryFees.regos.push({
                            type: entry.id,
                            rego: entry.rego,
                            entry_fee: entry.entry_fee
                        });
                    }
                    switch (entry.id) {
                        case 'vehicle':
                            booking.entryFees.vehicle++;
                            break;
                        case 'motorbike':
                            booking.entryFees.motorbike++;
                            break;
                        case 'concession':
                            booking.entryFees.concession++;
                            break;

                    }
                });
                // Deal with the rest of the booking
                booking.arrival = vm.booking.arrival;
                booking.departure = vm.booking.departure;
                booking.guests = vm.booking.guests;
                booking.campsites = vm.selected_campsites;
                booking.campground = vm.booking.campground
                // Hide the alert
                vm.$store.dispatch("updateAlert", {
                    visible: false,
                    type: "danger",
                    message: ""
                });
                vm.$http.put(api_endpoints.booking(vm.booking.id), JSON.stringify(booking), {
                    emulateJSON: true,
                    headers: {
                        'X-CSRFToken': helpers.getCookie('csrftoken')
                    },
                }).then((response) => {
                    vm.loading.splice('updating booking', 1);
                    vm.finishBooking();
                }, (error) => {
                    let error_str = helpers.apiVueResourceError(error);
                    vm.$store.dispatch("updateAlert", {
                        visible: true,
                        type: "danger",
                        message: error_str
                    });
                    vm.loading.splice('updating booking', 1);
                });
            }
        },
        finishBooking: function() {
            let vm = this;
            vm.$router.push({
                name: "booking-dashboard"
            });
        },
        isFormValid: function() {
            let vm = this;
            return (vm.validateParkEntry() && $(vm.bookingForm).valid());
        },
        validateParkEntry: function() {
            let vm = this;
            var isValid = true;
            let filled = 0;
            $('.vehicleLookup').each((i,d) => {
                $(d).val() != '' ? filled++ : '';  
            });
            if (vm.booking.parkEntry.vehicles > 0) {
                if (vm.booking.parkEntry.vehicles > filled) {
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
                    price_level: "required"
                },
                messages: {},
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
        addVehicleCount: function(park_entry) {

            let vm = this;
            var count = vm.booking.parkEntry.vehicles
            if (park_entry.amount < 10 && count < 10) {
                park_entry.amount = (park_entry.amount < 10) ? park_entry.amount += 1 : park_entry.amount;
                vm.booking.parkEntry.vehicles++;
                vm.parkEntryVehicles.push(JSON.parse(JSON.stringify(park_entry)));
            }
            vm.booking.price = vm.booking.price - vm.booking.entryFees.entry_fee;
            vm.updateParkEntryPrices();
            vm.booking.price = vm.booking.price + vm.booking.entryFees.entry_fee;
            vm.booking_price = vm.booking.price;

        },
        removeVehicleCount: function(park_entry) {
            let vm = this;
            var count = vm.booking.parkEntry.vehicles
            if (park_entry.amount > 0 && count > 0) {
                var found = false;
                for (var i = park_entry.amount - 1; i >= 0; i--) {
                    for (var j = vm.parkEntryVehicles.length - 1; j >= 0; j--) {
                        if (park_entry.description == vm.parkEntryVehicles[j].description) {
                            park_entry.amount = (park_entry.amount > 0) ? park_entry.amount -= 1 : park_entry.amount;
                            vm.parkEntryVehicles.splice(j, 1);
                            vm.booking.parkEntry.vehicles--;
                            found = true;
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
            vm.booking_price = vm.booking.price;
        },
        initBooking(response) {           
            let vm = this;
            vm.booking = JSON.parse(JSON.stringify(response.body));
            vm.booking.arrival = Moment(vm.booking.arrival).format('DD/MM/YYYY');
            vm.booking.departure = Moment(vm.booking.departure).format('DD/MM/YYYY');
            // set the campsite
            vm.selected_campsites = vm.booking.campsites;
            // Update dates
            vm.selected_arrival = vm.booking.arrival;
            vm.selected_departure = vm.booking.departure;
            // set the campground
            vm.campground = vm.booking.campground ? vm.campgrounds.find(c => parseInt(c.id) === parseInt(vm.booking.campground)) : null;
            // fetch park details
            vm.fetchPark();
            // fetch the sites
            vm.fetchSites();
            // Update guests
            let guests = vm.booking.guests;
            Object.keys(guests).forEach((key) => {
                vm.guestsPicker.map((p) => {
                    if (p.id == key) {
                        p.amount = guests[key];
                    }
                    return p;
                })
            });
            vm.generateGuestCountText();
            // Update Vehicles
            vm.booking.parkEntry = { 'vehicles': 0};
            vm.booking.entryFees = {
                vehicle : 0,
                motorbike: 0,
                concession:0,
                entry_fee: 0,
                regos:[]
            };
            $.each(vm.booking.regos,(i,v) => {
                vm.parkEntryPicker.map((vp) => {
                    if (vp.id == v.type){
                        vp.rego = v.rego;
                        vp.entry_fee = v.entry_fee;
                        vm.addVehicleCount(vp)
                    }
                    vp.rego = '';
                    vp.entry_fee = false;
                    return vp;
                });
            })

            vm.$nextTick(() => {
                vm.addEventListeners();
            });
            setTimeout(function(){
                vm.generateBookingPrice();
                vm.initialised = true;
            },2000);

        }
    },
    mounted: function() {
        let vm = this;
        vm.bookingForm = document.forms.bookingForm;
        vm.initSelectTwo();
        //vm.addEventListeners();
        //vm.addFormValidations();
    },
    beforeRouteEnter(to, from, next) {
        store.commit('SET_LOADER_STATE',true);
        store.commit('SET_LOADER_TEXT','Loading Booking');
        let initialisers = [
            store.dispatch('fetchCampgrounds'),
            booking_helpers.fetchBooking(to.params.booking_id)
        ]
        Promise.all(initialisers).then((response) => {
            store.commit('SET_LOADER_STATE',false);
            next(vm => {
                vm.initBooking(response[1]);
            });
        }) 
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

