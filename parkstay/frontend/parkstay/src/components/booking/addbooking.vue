<template lang="html">
    <div id="addBooking">
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
                                  <strong>$10.00 per/night</strong>
                              </p>
                        </div>
                        <div class="col-md-8">
                            <form class="form-horizontal">
                                <div class="row">
                                    <div class="col-md-12">
                                        <div class="form-group">
                                            <label class="col-md-2 control-label pull-left"  for="Dates">Dates: </label>
                                            <div class="col-md-4">
                                                <div class="input-group">
                                                    <input type="text" class="form-control" name="arrival" placeholder="DD/MM/YYYY"  readonly="readonly">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="col-md-4">
                                                <div class="input-group">
                                                    <input type="text" class="form-control" name="depature" placeholder="DD/MM/YYYY" readonly="readonly">
                                                    <span class="input-group-addon">
                                                        <span class="glyphicon glyphicon-calendar"></span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label class="col-md-2 control-label pull-left"  for="Campground">Campground: </label>
                                            <div class="col-md-4">
                                                <input type="text" name="guests" class="form-control" placeholder="guests" readonly="readonly">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
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
                                    <select class="form-control" name="campsite" >
                                        <option value=""></option>
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
                            <input type="text" name="email" class="form-control">
                          </div>
                      </div>
                      <div class="col-md-3">
                          <div class="form-group">
                            <label for="Confirm Email">Confirm Email</label>
                            <input type="text" name="" class="form-control">
                          </div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-3">
                          <div class="form-group">
                            <label for="First Name">First Name</label>
                            <input type="text" name="" class="form-control">
                          </div>
                      </div>
                      <div class="col-md-3">
                          <div class="form-group">
                            <label for="Surname">Surname</label>
                            <input type="text" name="" class="form-control">
                          </div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-3">
                          <div class="form-group">
                            <label for="Postcode">Postcode</label>
                            <input type="text" name="" class="form-control">
                          </div>
                      </div>
                      <div class="col-md-3">
                          <div class="form-group">
                            <label for="Country">Country</label>
                            <input type="text" name="" class="form-control" id="countriesList" >
                            <!--datalist id="countriesList">
                                <option v-for="c in countries" :value="c.name">{{c.name}}</option>
                            </datalist-->
                          </div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-3">
                          <div class="form-group">
                            <label for="Phone">Phone <span class="text-muted">(mobile prefered)</span></label>
                            <input type="text" name="" class="form-control">
                          </div>
                      </div>
                      <div class="col-md-3">
                          <div class="form-group">
                            <label for="Vehicle Registration">Vehicle Registration</label>
                            <input type="text" name="" class="form-control">
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
                              <input type="text" class="form-control" placeholder="0.00">
                            </div>
                          </div>
                      </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <p class="text-muted">
                                Payments will ne recorded against the booking once the booking is completed and the payment is received.
                            </p>
                        </div>
                        <div class="col-md-6">
                          <button type="button" class="btn btn-primary btn-lg pull-right"> Book</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
import {$,awesomplete,bus} from "../../hooks.js";
export default {
    name:"addBooking",
    data:function () {
        return{
            countries:[]
        };
    },
    methods:{
        fetchCountries:function (){
            let vm =this;
            vm.$http.get("https://restcountries.eu/rest/v1/?fullText=true").then((response)=>{
                vm.countries = response.body;
                var list = [];
                $.each(vm.countries,function (i,c) {
                    list.push(c.name);
                });
                vm.$nextTick(function () {
                    var input = document.getElementById("countriesList");
                    new awesomplete(input, {
                        list,
                        minChars: 1,
                    });
                });

            },(response)=>{

            });
        }
    },
    mounted:function () {
        let vm = this;
        vm.fetchCountries();

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
