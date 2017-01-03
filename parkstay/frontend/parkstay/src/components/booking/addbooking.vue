<template lang="html">
    <div id="addBooking">
        <form name="bookingForm">
            <div class="row">
                <div class="col-lg-12">
                    <div class="well">
                        <div class="row">
                            <div class="col-md-12">
                                <h3 class="text-primary">Nanga Brook</h3>
                            </div>
                            <div class="col-md-4">
                                  <img src="http://placehold.it/200x150" class="img-thumbnail img-responsive">
                                  <p class="pricing">
                                      <strong>$10.00</strong> <span class="text-muted">per/night</span>
                                  </p>
                            </div>
                            <div class="col-md-8">
                                    <div class="row form-horizontal">
                                        <div class="col-md-12">
                                            <div class="form-group">
                                                <label class="col-md-2 control-label pull-left"  for="Dates">Dates: </label>
                                                <div class="col-md-4">
                                                    <div class="input-group date" id="dateArrival">
                                                        <input type="text" class="form-control" name="arrival" placeholder="Arrival" v-model="booking.arrival" >
                                                        <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="col-md-4">
                                                    <div class="input-group date" id="dateDepature">
                                                        <input type="text" class="form-control" name="depature" placeholder="Depature" v-model="booking.depature">
                                                        <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <label class="col-md-2 control-label pull-left"  for="Campground">Guests: </label>
                                                <div class="col-md-8">
                                                      <div class="dropdown guests">
                                                          <input type="text" class="form-control dropdown-toggle" name="guests" placeholder="Guest" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" v-model="guestsText">
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
                                    Click here to open the map of the campground to help you select the preferred campsite
                                </p>
                                <div class="row">
                                  <div class="col-md-6">
                                      <div class="form-group">
                                        <label for="Campsite">Campsite</label>
                                        <select class="form-control" name="campsite" v-model="booking.campsite">
                                            <option value=""></option>
                                            <option v-for="campsite in campsites" :value="campsite.id">{{campsite.name}}</option>
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
                            <div class="col-lg-12">
                                <h3 class="text-primary">Personal Details</h3>
                            </div>
                        </div>
                        <div class="row">
                          <div class="col-md-3">
                              <div class="form-group">
                                <label for="Email">Email</label>
                                <input type="text" name="email" class="form-control" v-model="booking.email">
                              </div>
                          </div>
                          <div class="col-md-3">
                              <div class="form-group">
                                <label for="Confirm Email">Confirm Email</label>
                                <input type="text" name="confirm_email" class="form-control">
                              </div>
                          </div>
                        </div>
                        <div class="row">
                          <div class="col-md-3">
                              <div class="form-group">
                                <label for="First Name">First Name</label>
                                <input type="text" name="firstname" class="form-control" v-model="booking.firstname">
                              </div>
                          </div>
                          <div class="col-md-3">
                              <div class="form-group">
                                <label for="Surname">Surname</label>
                                <input type="text" name="surname" class="form-control" v-model="booking.surname">
                              </div>
                          </div>
                        </div>
                        <div class="row">
                          <div class="col-md-3">
                              <div class="form-group">
                                <label for="Postcode">Postcode</label>
                                <input type="text" name="postcode" class="form-control" v-model="booking.postcode">
                              </div>
                          </div>
                          <div class="col-md-3">
                              <div class="form-group">
                                <label for="Country">Country</label>
                                <input type="text" name="country" class="form-control" v-model="booking.country" >
                              </div>
                          </div>
                        </div>
                        <div class="row">
                          <div class="col-md-3">
                              <div class="form-group">
                                <label for="Phone">Phone <span class="text-muted">(mobile prefered)</span></label>
                                <input type="text" name="phone" class="form-control" v-model="booking.phone">
                              </div>
                          </div>
                          <div class="col-md-3">
                              <div class="form-group">
                                <label for="Vehicle Registration">Vehicle Registration</label>
                                <input type="text" name="vehicle" class="form-control" v-model="booking.vehicle">
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
                                  <input type="text" class="form-control" :placeholder="0.00|formatMoney(2)" :value="booking.price|formatMoney(2)">
                                </div>
                              </div>
                          </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <p class="text-muted">
                                    Payments will not be recorded against the booking once the booking is completed and the payment is received.
                                </p>
                            </div>
                            <div class="col-md-6">
                              <button type="button" class="btn btn-primary btn-lg pull-right"> Book</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>

</template>

<script>
import {$,awesomplete,api_endpoints} from "../../hooks.js";
export default {
    name:"addBooking",
    data:function () {
        return{
            bookingForm:null,
            countries:[],
            booking:{
                arrival:"",
                depature:"",
                guests:"",
                campground:120,
                campsite:"",
                email:"",
                firstname:"",
                surname:"",
                postcode:"",
                country:"",
                phone:"",
                vehicle:"",
                price:"12"
            },
            campsites:[],
            loading:[],
            campground:{},
            guestsText:"",
            guestsPicker:[
                {
                    id:"adults",
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
                    id:"children",
                    name:"Children",
                    amount:0,
                    description: "Ages 6-16"
                },
                {
                    id:"infants",
                    name:"Infants",
                    amount:0,
                    description: "Ages 0-5"
                },
            ]
        };
    },
    components:{
        loader
    },
    computed:{
        isLoading:function () {
            return this.loading.length > 0;
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
    methods:{
        fetchCountries:function (){
            let vm =this;
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
                });

            },(response)=>{
                console.log(response);
            });
        },
        fetchCampsites:function () {
            let vm = this;
            vm.$http.get(api_endpoints.campgroundCampsites(vm.booking.campground)).then((response)=>{
                vm.campsites = response.body;
            },(response)=>{
                console.log(response);
            });
        }
    },
    mounted:function () {
        let vm = this;
        vm.bookingForm = document.forms.bookingForm;
        vm.fetchCountries();
        vm.fetchCampsites();

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
</style>
