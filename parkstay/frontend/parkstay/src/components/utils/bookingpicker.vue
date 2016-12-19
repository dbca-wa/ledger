<template lang="html" id="booking-picker">
    <div class="row">
        <div class="col-lg-12">
            <div class="well">
                <form class="" name="flsearch">
                    <div class="row">
                      <div class="col-md-3">
                          <div class="form-group">
                            <label for="where">Where</label>
                            <input type="text" class="form-control" name="where" placeholder="Region, Park" v-model="value.where">
                          </div>
                      </div>
                      <div class="col-lg-5 col-md-6">
                          <label for="When">When</label>
                          <form class="form-inline" name="when">
                              <div class="form-group">
                                <input type="text" class="form-control" name="checkin" placeholder="Check In">
                              </div>
                              <div class="form-group">
                                  <label for=""><i class="fa fa-arrow-right hidden-xs"></i></label>
                                  <input type="text" class="form-control" name="checkout" placeholder="Check Out">
                              </div>
                          </form>
                      </div>
                      <div class="col-lg-4 col-md-3">
                          <label for="guest">Guest</label>
                          <form class="form-inline" name="guest">
                              <div class="form-group">
                                <div class="dropdown">
                                    <input type="text" class="form-control dropdown-toggle" name="guests" placeholder="Guest" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
                                    <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                        <li>
                                            <a href="#" @click.prevent.stop="">
                                                <div class="row">
                                                    <div class="col-sm-8">
                                                        <span class="item">
                                                            {{value.guests.adults}} Adults (non concession)
                                                        </span>
                                                    </div>
                                                    <div class="col-sm-4">
                                                        <div class="btn-group btn-group-sm pull-right">
                                                          <button type="button" class="btn btn-default">+</button>
                                                          <button type="button" class="btn btn-default">-</button>
                                                        </div>
                                                    </div>
                                                </div>

                                            </a>

                                            <li role="separator" class="divider"></li>
                                        </li>
                                    </ul>
                                </div>
                              </div>
                              <div class="form-group">
                                 <button type="button" class="btn btn-primary"> Search</button>
                              </div>
                          </form>
                      </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import {$,daterangepicker}from '../../hooks.js'
export default {
    name:'booking-picker',
    data:function () {
        let vm = this;
        return {
            form : null
        }
    },
    props:{
        value:{
            default:function () {
                return{
                    where:"",
                    checkin:"",
                    checkout:"",
                    guests:{
                        adults:0,
                        concession:0,
                        children:0,
                        infants:0
                    }
                }
            }
        }
    },
    mounted:function () {
        let vm =this;
        vm.form = document.forms.flsearch;
        var checkInEl = document.forms.when.checkin;
        var checkOutEl = document.forms.when.checkout;
        var guest = document.forms.guest.guests;
        var rangepicker = $(checkInEl).daterangepicker({
            autoApply:true,
            minDate: new Date(),
            autoUpdateInput: false,
        });
        rangepicker.on('apply.daterangepicker', function(ev, picker) {
            $(checkInEl).val(picker.startDate.format('ddd MMM Do, YYYY'))
            $(checkOutEl).val(picker.endDate.format('ddd MMM Do, YYYY'));
            vm.value.checkin = picker.startDate.format('YYYY/MM/D');
            vm.value.checkout = picker.endDate.format('YYYY/MM/D');
        });
    }
}
</script>

<style lang="css" scoped>
    .form-control, .form-group .form-control {
        border: 0;
        background-image: -webkit-gradient(linear, left top, left bottom, from(#009688), to(#009688)), -webkit-gradient(linear, left top, left bottom, from(#D2D2D2), to(#D2D2D2));
        background-image: -webkit-linear-gradient(#009688, #009688), -webkit-linear-gradient(#D2D2D2, #D2D2D2);
        background-image: -o-linear-gradient(#009688, #009688), -o-linear-gradient(#D2D2D2, #D2D2D2);
        background-image: linear-gradient(#009688, #009688), linear-gradient(#D2D2D2, #D2D2D2);
        -webkit-background-size: 0 2px, 100% 1px;
        background-size: 0 2px, 100% 1px;
        background-repeat: no-repeat;
        background-position: center bottom, center -webkit-calc(100% - 1px);
        background-position: center bottom, center calc(100% - 1px);
        background-color: rgba(0, 0, 0, 0);
        -webkit-transition: background 0s ease-out;
        -o-transition: background 0s ease-out;
        transition: background 0s ease-out;
        float: none;
        -webkit-box-shadow: none;
        box-shadow: none;
        border-radius: 0;
    }
    .form-group .form-control:focus{
        background-image: linear-gradient(#337ab7,#337ab7);
        outline:none;
        background-size: 100% 2px,100% 1px;
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
    .dropdown-menu li a{
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .dropdown-menu .item{
        line-height: 2;
        font-weight: 700;
    }
</style>
