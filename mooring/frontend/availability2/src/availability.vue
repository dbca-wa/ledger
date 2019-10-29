<template>
    <div id="sites-cal" class="f6inject">

        <a name="makebooking" />
        <div class="row" v-if="status == 'offline'">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Sorry, this mooring doesn't yet support online bookings. Please visit the <a href="">Mooring Availability checker</a> for expected availability.
                </div>
            </div>
        </div>
        <div class="row" v-else-if="status == 'empty'">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Sorry, this mooring doesn't yet have any mooring assigned to it. Please visit the <a href="">Mooring Availability checker</a> for expected availability.
                </div>
            </div>
        </div>
        <div class="row" v-else-if="status == 'closed'">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Sorry, this mooring is closed for the selected period. Please visit the <a href="">Mooring Availability checker</a> for expected availability.
                </div>
            </div>
        </div>
        <div class="row" v-if="errorMsg">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Sorry, there was an error placing the booking: {{ errorMsg }} <br/>
                    <template v-if="showSecondErrorLine">
                    Please try again later. If this reoccurs, please contact <a href="">Parks and Visitor Services</a> with this error message, the mooring and the time of the request.
                    </template>
                </div>
            </div>
        </div>
        <div class="row" v-if="timeleft < 0">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Session Expired <br/>
                    <template v-if="showSecondErrorLine">
                    Sorry your Session has expired
                    </template>
                </div>
            </div>
        </div>

        <div class="columns small-12 medium-12 large-12" v-show="ongoing_booking">
        <div class="row">
                <div class="small-8 medium-9 large-10">

		<button v-show="ongoing_booking" style="color: #FFFFFF; background-color: rgb(255, 0, 0);" class="button small-12 medium-12 large-12" >Time Left {{ timeleft }} to complete booking.</button>
		<a type="button" :href="parkstayUrl+'/booking/abort'" class="button float-right warning continueBooking" style="color: #fff; background-color: #f0ad4e;  border-color: #eea236; border-radius: 4px;">
                      Cancel in-progress booking
                </a>
              </div>
	   </div>
	</div>
        <div class="columns small-12 medium-12 large-12">
        <div class="row">
                <div class="small-8 medium-9 large-10">
                        <div class="panel panel-default">
                             <div class="panel-heading"><h3 class="panel-title">Trolley: <span id='total_trolley'>${{ total_booking }}</span></h3></div>
                              <div class='columns small-12 medium-12 large-12'> 
                                 <div v-for="item in current_booking" class="row small-12 medium-12 large-12">
                                         <div class="columns small-12 medium-9 large-9">{{ item.item }}</div>
                                         <div class="columns small-12 medium-2 large-2">${{ item.amount }}</div>
                                         <div class="columns small-12 medium-1 large-1"><a v-show="item.past_booking == false" style='color: red; opacity: 1;' type="button" class="close" @click="deleteBooking(item.id, item.past_booking)">x</a></div>
                                 </div>
			      </div>
                        </div>
                </div>
                <div class="columns small-4 medium-3 large-2">
                        <div v-if="vesselRego.length < 0.1 || vesselRego == ' ' || vesselSize < 0.1 || vesselDraft < 0.1 ">
                            
                            <button title="Please enter vessel details" style="border-radius: 4px; border: 1px solid #2e6da4" class="button small-12 medium-12 large-12" @click="validateVessel()">Proceed to Check Out</button>
                        </div>
                        <div v-else>
                           <div v-if="vesselWeight == 0 && vesselBeam == 0 ">

                            <button title="Please enter vessel details" style="border-radius: 4px; border: 1px solid #2e6da4" class="button small-12 medium-12 large-12" @click="validateVessel()">Proceed to Check Out</button>
                           </div>
                           <div v-else>
                            <a  v-show="current_booking.length > 0 && booking_changed == true" class="button small-12 medium-12 large-12" :href="parkstayUrl+'/booking'" style="border-radius: 4px; border: 1px solid #2e6da4">Proceed to Check Out</a>
                            <button  title="Please add items into your trolley." v-show="current_booking.length == 0 || booking_changed == false" style="color: #000000; background-color: rgb(224, 217, 217); border: 1px solid #000; border-radius: 4px;" class="button small-12 medium-12 large-12" disabled >Add items to Proceed to Check Out</button>                
                            </div>


                            </div>
                        </div>
        </div>
        </div>
	<loader :isLoading.sync="isLoading">&nbsp;</loader>
        <div class="row" v-if="name">
            <div class="columns small-12">
                <h1>Book mooring:</h1>
            </div>
        </div>

        <div v-if="ongoing_booking" class="row" style='display:none'>
            <div class="columns small-12 medium-12 large-12">
                <div class="clearfix">
                    {{ timeleft }}
                    <a type="button" :href="parkstayUrl+'/booking'" class="button float-right warning continueBooking">
                        Complete in-progress booking
                    </a>
                    <template v-if="parseInt(parkstayGroundRatisId) > 0">
                        <a type="button" :href="parkstayUrl+'/booking/abort?change=true&change_ratis='+parkstayGroundRatisId" class="button float-right warning continueBooking">
                            Cancel in-progress booking
                        </a>
                    </template>
                    <template v-else>
                        <a type="button" :href="parkstayUrl+'/booking/abort?change=true&change_id='+parkstayGroundId" class="button float-right warning continueBooking">
                            Cancel in-progress booking
                        </a>
                    </template>
                </div>
            </div>
        </div>
        <div class="row" v-show="status == 'online'">
            <div v-if="long_description" class="columns small-12 medium-12 large-12" style='display:none'>
                <div class="row">
                    <div class="columns small-6 medium-6 large-3">
                        <button type="button" class="button formButton" @click="toggleMoreInfo">
                            More Information &nbsp;&nbsp;
                            <i style="font-size:large;" v-if="!showMoreInfo" class="fa fa-caret-down"></i>
                            <i style="font-size:large;" v-else class="fa fa-caret-up"></i>
                        </button>
                    </div>
                </div>
                <div class="row" style="margin-bottom:15px;" v-if="showMoreInfo">
                    <div class="columns small-12 medium-12 large-12">
                        <div v-html="long_description"></div>
                    </div>
                </div>
            </div>
            <div class="columns small-6 medium-6 large-2">
                <label>Arrival
                    <input id="date-arrival" type="text" placeholder="dd/mm/yyyy" v-on:change="update"/>
                </label>
            </div>
            <div class="columns small-6 medium-6 large-2">
                <label>Departure
                    <input id="date-departure" type="text" placeholder="dd/mm/yyyy" v-on:change="update"/>
                </label>
            </div>
            <div class="small-6 medium-6 large-2 columns" >
                <label>
                    Vessel Details
                    <input type="button" class="button formButton" value="Details ▼" data-toggle="measurements-dropdown"/>
                </label>
                <div style='position: relative;'>
                <div class="dropdown-pane" id="measurements-dropdown" data-dropdown data-auto-focus="true">
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="vesselRego" class="text-left">Vessel Rego</label>
                        </div><div class="small-6 columns">
                            <input type="text" id="vesselRego" ref="vesselRego" name="vessel_rego" @blur="searchRego()" v-model="vesselRego" style="text-transform:uppercase" :disabled="current_booking.length > 0" />
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="vesselSize" class="text-left">Vessel Size (Meters)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="vesselSize" ref="vesselSize" name="vessel_size" @change="checkDetails(false)" @blur="checkDetails(false)" v-model="vesselSize" step='0.01' :disabled="current_booking.length > 0"/>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="vesselDraft" class="text-left">Vessel Draft (Meters)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="vesselDraft" ref="vesselDraft" name="vessel_draft" @change="checkDetails(false)" @blur="checkDetails(false)" v-model="vesselDraft" step='0.01' :disabled="current_booking.length > 0"/>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="vesselBeam" class="text-left">Vessel Beams (Meters)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="vesselBeam" ref="vesselBeam" name="vessel_beam" @change="checkDetails(false)" @blur="checkDetails(false)" v-model="vesselBeam" step='0.01' :disabled="current_booking.length > 0" />
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="vesselWeight" class="text-left">Vessel Weight (Tonnes)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="vesselWeight" ref="vesselWeight" name="vessel_weight" @change="checkDetails(false)" @blur="checkDetails(false)" v-model="vesselWeight" step='0.01' :disabled="current_booking.length > 0"/>
                        </div>
                    </div>
                </div>
                </div>
            </div>
            <div class="small-6 medium-6 large-2 columns" >
                <label>
                    Guests 
                    <input type="button" class="button formButton" v-bind:value="numPeople" data-toggle="guests-dropdown" id='guests-button' />
                </label>
                <div style='iiiiposition: relative;'>
                <div class="dropdown-pane" id="guests-dropdown" data-dropdown data-auto-focus="true">
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="num_adults" class="text-right">Adults (ages 12+)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numAdults" name="num_adults" @change="checkGuests()" v-model="numAdults" min="0" max="16"/>
                        </div>
                    </div>
                    <div class="row" style="display:none;">
                        <div class="small-6 columns" >
                            <label for="num_concessions" class="text-right"><span class="has-tip" title="Holders of one of the following Australian-issued cards:
- Seniors Card
- Age Pension
- Disability Support
- Carer Payment
- Carer Allowance
- Companion Card
- Department of Veterans' Affairs">Concessions</span></label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numConcessions" name="num_concessions" @change="checkGuests()" v-model="numConcessions" min="0" max="16"/>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="num_children" class="text-right">Children (ages 4-12)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numChildren" name="num_children" @change="checkGuests()" v-model="numChildren" min="0" max="16"/>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="num_infants" class="text-right">Infants (ages 0-4)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numInfants" name="num_infants" @change="checkGuests()" v-model="numInfants" min="0" max="16"/>
                        </div>
                    </div>
                </div>
                </div>
            </div>
            <div class="columns small-6 medium-6 large-2">
                <label title="Distance to search from the original selected mooring.">Distance (radius KMs)
                    <input id="distanceRadius" type="number" placeholder="0" v-on:change="update" v-model="distanceRadius"/>
                </label>
            </div>

            <div class="columns small-6 medium-6 large-2">
            <span class='pull-right'>
               <a type="button" :href="/map/" class="button float-right warning">
                  Search Other Mooring
               </a>
	    </span>
	    </div>
            
            <div v-if="!useAdminApi" class="columns small-6 medium-6 large-3" style='display:none;'>
                <label>Equipment
                    <select name="gear_type" v-model="gearType" @change="update()">
                        <option value="tent" v-if="gearTotals.tent">Tent</option>
                        <option value="campervan" v-if="gearTotals.campervan">Campervan</option>
                        <option value="caravan" v-if="gearTotals.caravan">Caravan / Camper trailer</option>
                    </select>
                </label>
            </div>           
        </div>
        <div class="row" v-show="status == 'online'">
            <div class="columns table-scroll">
                 <div v-if="vesselSize > 0 && vesselDraft > 0" class="small-12 medium-12 large-12">
                      <div v-if="vesselDraft != 0 && vesselWeight != 0" class="small-12 medium-12 large-12">
                           <table class="hover">
                               <thead>
                                   <tr>
                                       <th class="site">Mooring &nbsp;<a class="float-right" target="_blank" :href="map" v-if="map" style='display: none;'>View Map</a></th>
                                       <th class="book">Book</th>
                                       <th class="date" v-for="i in days">{{ getDateString(arrivalDate, i-1) }}</th>
                                   </tr>
                               </thead>
                               <tbody><template v-for="(site, index) in sites" >
                                   <tr v-show="mooring_book_row_display[index] == 'show'" >
                                       <td class="site">{{ site.name }} - <i>{{ site.mooring_park }}</i><br>
	                       		<i v-if="site.distance_from_selection > 1" >Distance: {{ site.distance_from_selection }}km</i>
	                       		<i v-else >Distance: {{ site.distance_from_selection_meters }}m</i>
                                       </td>
                                       <td class="book">
                                           <template v-if="site.price">
                                               <button v-if="mooring_book_row[index] == true" :disabled="mooring_book_row_disabled[index] == true" @click="addBookingRow(index)" class="button"><small>Book now</small><br/> ${{ mooring_book_row_price[index] }}</button>
                                               <button style='display:none' v-else disabled class="button has-tip" data-tooltip aria-haspopup="true" title="Please complete your current ongoing booking using the button at the top of the page."><small>Book now</small><br/>{{ site.price }}</button>
                                           </template>
                                           <template v-else>
                                               <button v-if="site.breakdown" class="button warning" @click="toggleBreakdown(site)"><small>Show availability</small></button>
                                               <button v-else class="button secondary disabled" disabled><small>Change dates</small></button>
                                           </template>
                                       </td>
                                       <td class="date" v-for="day in site.availability" v-bind:class="{available: day[0]}" align='center'>
                                                    <div v-for="bp in day[1].booking_period" style='width:160px; '>

                                                       <div v-if="bp.status == 'open'" class='tooltip2'  align='left'>
                                                       <button class="button" style='width: 160px; margin-bottom: 2px;'  @click="addBooking(site.id,site.mooring_id,bp.id,bp.date)" >
                                                           <small>Book {{ bp.period_name }} <span v-if="site.mooring_class == 'small'">${{ bp.small_price }}</span> <span v-if="site.mooring_class == 'medium'">${{ bp.medium_price }}</span> <span v-if="site.mooring_class == 'large'">${{ bp.large_price }}</span></small>
                                                       </button><br>
                                                          
                                                          <span v-show="bp.caption.length > 1" class="tooltiptext">{{ bp.caption }}</span>
                                                       </div>
	                       			<div v-else-if="bp.status == 'selected'" >
                                                            <div style="position: relative; text-align: right; margin-right: 25px;"><a v-show="bp.past_booking == false" type="button" class="close" style="color: red; opacity: 1; position: absolute; padding-left: 5px;" @click="deleteBooking(bp.booking_row_id, bp.past_booking)" >x</a></div>
                                                       <button class="button" style='width: 160px; margin-bottom: 2px; background-color: #8bc8f1;' @click="deleteBooking(bp.booking_row_id, bp.past_booking)" > 
                                                           <small>Book {{ bp.period_name }} <span v-if="site.mooring_class == 'small'">${{ bp.small_price }}</span> <span v-if="site.mooring_class == 'medium'">${{ bp.medium_price }}</span> <span v-if="site.mooring_class == 'large'">${{ bp.large_price }} </span></small>
                                                       </button>
	                       			</div>
                                                       <div v-else-if="bp.status == 'perday'" >
                                                       <button class="button"  style='width: 160px; margin-bottom: 2px; background-color: rgb(255, 253, 199); color: #000;' >
                                                            <small>One Mooring Limit</small>
                                                       </button>
                                                       </div>

                                                       <div v-else-if="bp.status == 'maxstay'" >
                                                       <button class="button"  style='width: 160px; margin-bottom: 2px; background-color: rgb(255, 253, 199); color: #000;' >
                                                            <small>Max Stay Limit Reached</small>
                                                       </button>
                                                       </div>

	                       			<div v-else >
                                                       <button class="button"  style='width: 160px; margin-bottom: 2px; background-color: rgb(255, 236, 236); text-decoration: line-through;color: #000;' >
                                                            <small>{{ bp.period_name }}</small>
                                                       </button>
	                       			</div>
                                                    </div>
                                       </td>
                                   </tr>
                                   <template v-if="site.showBreakdown"><tr v-for="line in site.breakdown" class="breakdown">
                                       <td class="site">Site: {{ line.name }}</td>
                                       <td></td>
                                       <td class="date" v-for="day in line.availability" v-bind:class="{available: day[0]}" >{{ day[1] }}</td>
                                   </tr></template>
                               </template></tbody>
                           </table>
                       </div>
                 </div>
	    </div>
            <div class="small-12 medium-12 large-12">
            <div v-if="vesselSize > 0 && vesselDraft > 0 && vesselWeight == 0 && vesselBeam == 0" class="small-12 medium-12 large-12">
                <div class="columns small-12 medium-12 large-12" >
                    <div class="callout alert">
                      Please enter a beam length or weight depending on your mooring type.   
                    </div>
                </div>
	    </div>


            <div class="row" v-if="sites.length == 0 && isLoading == false">
                <div class="columns small-12 medium-12 large-12">
                    <div class="callout alert">
                        Sorry we couldn't find any mooring matching the query entered.
                    </div>
                </div>
            </div>

            </div>
     <div oldvif="max_advance_booking_days > max_advance_booking" class="small-12 medium-12 large-12" style='display:none'>
          <table class="hover">
                <tbody>
                  <tr>
                     <td>
          	Advanced booking is limited to {{ max_advance_booking }} day/s. 
                     </td>
                  </tr>
                </tbody>
          </table>
     </div>



        </div>
       </div>
    </div>

</template>

<style lang="scss">

.f6inject {
    th.site {
        width: 30%;
        min-width: 200px;
    }
    th.book {
        min-width: 100px;
    }
    th.date {
        min-width: 60px;
    }
    td.site {
        font-size: 0.8em;
    }
    .date, .book {
        text-align: center;
    }
    td .button {
        margin: 0;
    }
    .table-scroll table {
        width: 100%;
    }

    /* table font colour override */
    table thead tr {
        background: unset;
        color: unset;
    }

    td.available {
        color: #082d15;
    }
    table tbody tr > td.available {
        background-color: #edfbf3;
    }
    table tbody tr:hover > td.available {
        background-color: #ddf8e8;
    }
    table tbody tr:nth-child(2n) > td.available {
        background-color: #cef5dd;
    }
    table tbody tr:nth-child(2n):hover > td.available {
        background-color: #b8f0cd;
    }

    table tbody tr.breakdown, table tbody tr.breakdown:hover  {
        background-color: #656869;
        color: white;
    }
    table tbody tr.breakdown:nth-child(2n), 
    table tbody tr.breakdown:nth-child(2n):hover, 
    table.hover:not(.unstriped) tr.breakdown:nth-of-type(2n):hover {
        background-color: #454d50;
        color: white;
    }
    table tbody tr.breakdown > td.available {
        background-color: #468a05;
        color: white;
    }
    table tbody tr.breakdown:nth-child(2n) > td.available {
        background-color: #305e04;
        color: white;
    }

    .button.formButton {
        display: block;
        width: 100%;
    }

    .siteWarning {
        font-weight: bold;
        font-style: italic;
    }
    .continueBooking {
        text-decoration: none;
    }

    /* Tooltip */
    .tooltip2 {
      position: relative;
      display: inline-block;
    }
    
    /* Tooltip text */
    .tooltip2 .tooltiptext {
      visibility: hidden;
      width: 165px;
      background-color: black;
      color: #fff;
      text-align: center;
      padding: 8px;
      border-radius: 6px;
      text-align: left;
    
      /* Position the tooltip text - see examples below! */
      position: absolute;
      z-index: 1;
    }
    
    /* Show the tooltip text when you mouse over the tooltip container */
    .tooltip2:hover .tooltiptext {
      visibility: visible;
    }
    
    .tooltip2 .tooltiptext::after {
      content: " ";
      position: absolute;
      bottom: 100%;  /* At the top of the tooltip */
      left: 50%;
      margin-left: -5px;
      border-width: 5px;
      border-style: solid;
      border-color: transparent transparent black transparent;
    }

}

</style>

<script>

import 'foundation-sites';
import 'foundation-datepicker/js/foundation-datepicker';
import debounce from 'debounce';
import moment from 'moment';
import swal from 'sweetalert2';
import 'sweetalert2/dist/sweetalert2.css';
import loader from './loader.vue';

var nowTemp = new Date();
var now = moment.utc({year: nowTemp.getFullYear(), month: nowTemp.getMonth(), day: nowTemp.getDate(), hour: 0, minute: 0, second: 0}).toDate();

var siteType = {
    NOBOOKINGS: 0,
    ONLINE: 1,
    PHONE: 2,
    OTHER: 3
};

function getQueryParam(name, fallback) {
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)");
    var results = regex.exec(window.location.href);
    if (!results) return fallback;
    if (!results[2]) return fallback;
    return decodeURIComponent(results[2].replace(/\+/g, " "));
};

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

export default {
    el: '#availability',
    components: {
        loader,
    },
    data: function () {
        return {
            name: '',
            arrivalDate: moment.utc(getQueryParam('arrival', moment.utc(now).format('YYYY/MM/DD')), 'YYYY/MM/DD'),
            departureDate:  moment.utc(getQueryParam('departure', moment.utc(now).add(5, 'days').format('YYYY/MM/DD')), 'YYYY/MM/DD'),
            parkstayUrl: global.parkstayUrl || process.env.PARKSTAY_URL,
            useAdminApi: global.useAdminApi || false,
            // order of preference:
            // - GET parameter 'site_id'
            // - global JS var 'parkstayGroundId'
            // - '1'
            parkstayGroundId: parseInt(getQueryParam('site_id', global.parkstayGroundId || '1')),
            parkstayGroundRatisId: parseInt(getQueryParam('parkstay_site_id', '0')),
            days: 5,
            numAdults: parseInt(getQueryParam('num_adult', 2)),
            numChildren: parseInt(getQueryParam('num_children', 0)),
            numConcessions: parseInt(getQueryParam('num_concession', 0)),
            numInfants: parseInt(getQueryParam('num_infant', 0)),
            vesselSize: parseFloat(getQueryParam('vessel_size', 0)),
            vesselDraft: parseFloat(getQueryParam('vessel_draft', 0)),
            vesselBeam: parseFloat(getQueryParam('vessel_beam', 0)),
            vesselWeight: parseFloat(getQueryParam('vessel_weight', 0)),
            vesselRego: getQueryParam('vessel_rego', ''),
            searchedRego: getQueryParam('vessel_rego', ''),
            distanceRadius: parseInt(getQueryParam('distance_radius', 100)),
            maxAdults: 30,
            maxChildren: 30,
            gearType: getQueryParam('gear_type', 'tent'),
            mooring_vessel_size: 0,
            max_advance_booking: 0,
            max_advance_booking_days: 0,
            gearTotals: {
                tent: 0,
                campervan: 0,
                caravan: 0
            },
            status: null,
            errorMsg: null,
            classes: {},
            sites: [],
            long_description: '',
            map: null,
            showMoreInfo: false,
            ongoing_booking: false,
            ongoing_booking_id: null,
            current_booking: [],
            booking_changed: true,
            total_booking: '0.00',
            showSecondErrorLine: true,
            timer: -1,
            expiry: null,
            booking_expired_notification: false,
            mooring_book_row: [],
            mooring_book_row_price: [],
            mooring_book_row_disabled: [],
            mooring_book_row_display: [],
            loadingID: 0 
        };
    },
    computed: {
        numPeople: {
            cache: false,
            get: function() {
                var count = parseInt(this.numAdults) + parseInt(this.numConcessions) + parseInt(this.numChildren) + parseInt(this.numInfants);
                if (count === 1) {
                    return count +" person ▼";
                } else {
                    return count + " people ▼";
                }
            }
        },
        arrivalDateString: {
            cache: false,
            get: function() {
                return this.arrivalEl[0].value ? moment(this.arrivalData.getDate()).format('YYYY/MM/DD') : null; 
            }
        },
        departureDateString: {
            cache: false,
            get: function() {
                return this.departureEl[0].value ? moment(this.departureData.getDate()).format('YYYY/MM/DD') : null; 
            }
        },
        timeleft: {
                cache: false,
                get: function get() {
                    // Minutes and seconds
                    var mins = ~~(this.timer / 60);
                    var secs = this.timer % 60;

                    // Hours, minutes and seconds
                    var hrs = ~~(this.timer / 3600);
                    var mins = ~~((this.timer % 3600) / 60);
                    var secs = this.timer % 60;

                    // Output like "1:01" or "4:03:59" or "123:03:59"
                    var ret = "";

                    if (hrs > 0) {
                        ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
                    }

                    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
                    ret += "" + secs;
                    if (this.ongoing_booking) {
                       
                       if (this.timer < 0) {
                            if (this.booking_expired_notification == false) { 
   		   	   console.log('TIMED OUT');
                           clearInterval(this.timer);
//                         var loc = window.location;
//                         window.location = loc.protocol + '//' + loc.host + loc.pathname;
                           this.bookingExpired();
                           this.booking_expired_notification = true;
			}
		       }
                    }
                    return ret;
                }
        }

    },
    methods: {
        toggleMoreInfo: function(){
            this.showMoreInfo ? this.showMoreInfo = false: this.showMoreInfo = true;
        },
        getDateString: function (date, offset) {
            return moment(date).add(offset, 'days').format('ddd MMM D');
        },
        toggleBreakdown: function (site) {
            if (site.showBreakdown) {
                site.showBreakdown = false;
            } else {
                this.sites.forEach(function(el) {
                    el.showBreakdown = false;
                });
                site.showBreakdown = true;
            }
        },
        bookingExpired: function() {
                swal({
                  title: 'Booking Expired',
                  text: "Please click start again to begin booking again:",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'Start Again',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                }).then((value) => {
                        var loc = window.location;
//                        window.location = loc.protocol + '//' + loc.host + loc.pathname;
                        window.location = loc.protocol + '//' + loc.host + '/map/';
		});

	},
        createBookingError: function(message) {
                swal({
                  title: 'Error',
                  text: message,
                  type: 'error',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                })
                return;
        },
        deleteBooking: function(booking_item_id, past_booking) {
             if (past_booking == true) { 
                swal({
                  title: 'Error',
                  text: "Unable to delete past booking",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                })
                return;
	     }


              var vm = this;
              vm.loadingID = vm.loadingID + 1;
              var submitData = {
                  booking_item: booking_item_id,
              };

              $.ajax({
                  loadID: vm.loadingID,
                  url: vm.parkstayUrl + '/api/booking/delete',
                  dataType: 'json',
                  method: 'POST',
                  data: submitData,
                  success: function(data, stat, xhr) {
                     if (data.result == 'error') { 
                         swal({
                            title: 'Error',
                            text: data.message,
                            type: 'warning',
                            showCancelButton: false,
                            confirmButtonText: 'OK',
                            showLoaderOnConfirm: true,
                            allowOutsideClick: false
                         })
                     }


                      vm.update();
                  },
                  error: function(data, stat, err) {
                     swal({
	                  title: 'Error',
        	          text: 'Uknown Error',
                	  type: 'warning',
	                  showCancelButton: false,
        	          confirmButtonText: 'OK',
	                  showLoaderOnConfirm: true,
	                  allowOutsideClick: false
        	        })



                       vm.update();
                  }
              });

	},
	addBookingRow: function(site_index_id) {
                        var vm = this;
                        var avail_index;
                        // vm.sites = data.sites;
                        for (avail_index = 0; avail_index < vm.sites[site_index_id].availability.length; ++avail_index) {
                                        var booking_period = vm.sites[site_index_id].availability[avail_index][1].booking_period;
                                        //if (booking_period.length > 1) {
                                        //        vm.mooring_book_row[index] = false;
                                        //}
                                        vm.addBooking(vm.sites[site_index_id].id, vm.sites[site_index_id].mooring_id, booking_period[0].id, booking_period[0].date);
                                        //if (vm.ongoing_booking == false) {
                                           
                                        //}
                        }


	},
        addBooking: function (site_id, mooring_id,bp_id,date) {
              var vm = this;
              vm.loadingID = vm.loadingID + 1;
              vm.isLoading =true;
              $('#spinnerLoader').show();

              var booking_start = $('#date-arrival').val();
              var booking_finish = $('#date-departure').val();

              var submitData = {
                  site_id: site_id,
                  mooring_id: mooring_id,
                  bp_id: bp_id,
                  date: date,
                  booking_start: booking_start,
                  booking_finish: booking_finish,
                  num_adult: vm.numAdults,
                  num_children : vm.numChildren,
                  num_infant: vm.numInfants
              };

              $.ajax({
                  loadID: vm.loadingID,
                  url: vm.parkstayUrl + '/api/booking/create', 
                  dataType: 'json',
                  method: 'POST',
                  //async: false,
                  data: submitData, 
                  success: function(data, stat, xhr) {
                     if (this.loadID == vm.loadingID) { 
                         vm.isLoading =false;
                         $('#spinnerLoader').hide();
	             }
                     if (data.result == 'error') { 
                          vm.createBookingError(data.message); 
                     }
                     vm.update();
                  },
                  error: function(xhr, stat, err) {
                       if (this.loadID == vm.loadingID) {
                           vm.isLoading =false;
                           $('#spinnerLoader').hide();
                       }
                       vm.update();
                  }
              });
        },
        submitBooking: function (site) {
            alert('not working yet');
            return;
            var vm = this;
            if (vm.vesselSize > 0 ) { 
            } else {
                swal({
                  title: 'Missing Vessel Size',
                  text: "Please enter vessel size:",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                })
                return;
            }

            var submitData = {
                arrival: vm.arrivalDateString,
                departure: vm.departureDateString,
                num_adult: vm.numAdults,
                num_child: vm.numChildren,
                num_concession: vm.numConcessions,
                num_infant: vm.numInfants,
                vessel_size: vm.vesselSize
            };
            if (site.type == 0) { // per site listing
                submitData.campsite = site.id;
            } else {
                submitData.campground = vm.parkstayGroundId;
                submitData.campsite_class = site.type;
            }
            $.ajax({
                url: vm.parkstayUrl + '/api/create_booking',
                method: 'POST',
                data: submitData,
                dataType: 'json',
                crossDomain: true,
                xhrFields: {
                    withCredentials: true
                },
                success: function(data, stat, xhr) {
                    if (data.status == 'success') {
                        window.location.href = vm.parkstayUrl + '/booking';
                    }
                },
                error: function(xhr, stat, err) {
                    console.log('POST error');
                    //console.log(xhr);
                    vm.errorMsg = (xhr.responseJSON && xhr.responseJSON.msg) ? xhr.responseJSON.msg : '"'+err+'" response when communicating with Mooring.';
                    vm.update();
                }
            });
        },
        updateURL: function () {
            // update browser history
            var vm = this;
            var newHist = window.location.href.split('?')[0] +'?'+ $.param({
                site_id: vm.parkstayGroundId,
                arrival: moment(vm.arrivalDate).format('YYYY/MM/DD'),
                departure: moment(vm.departureDate).format('YYYY/MM/DD'),
                gear_type: vm.gearType,
                num_adult: vm.numAdults,
                num_child: vm.numChildren,
                num_concession: vm.numConcessions,
                num_infant: vm.numInfants,
                vessel_size : vm.vesselSize,
                vessel_draft: vm.vesselDraft,
                vessel_beam: vm.vesselBeam,
                vessel_weight: vm.vesselWeight,
                vessel_rego: vm.vesselRego,
            });
            history.replaceState('', '', newHist);
        },
        searchRego: function(rego){
            let vm = this;
            if (rego){
                var reg = rego;
            } else {
                var reg = vm.vesselRego
            }
            var not_null = true
            if (reg == null || reg == "" || reg == " "){
                not_null = false;
            }
            var data = {
                'rego': reg
            }
            if(reg && not_null && vm.searchedRego != reg){
                $.ajax({
                    url: "/api/registeredVessels/",
                    dataType: 'json',
                    data: data,
                    method: 'GET',
                    success: function(data, stat, xhr) {
                        vm.searchedRego = reg;
                        if(data[0]){
                            vm.vesselSize = parseFloat(data[0].vessel_size);
                            vm.vesselWeight = parseFloat(data[0].vessel_weight);
                            vm.vesselDraft = parseFloat(data[0].vessel_draft);
                            vm.vesselBeam = parseFloat(data[0].vessel_beam);  
                        } else {
                            console.log("Registration was not found.");
                        }
                    }
                });
                vm.update();
            }
        },
        checkDetails: function(from_update){
            let vm = this;
            if (vm.vesselSize == null || vm.vesselSize.length == 0){
                console.log("size empty");
                vm.vesselSize = 0;
            }
            if (vm.vesselDraft == null || vm.vesselDraft.length == 0){
                console.log("draft empty");
                vm.vesselDraft = 0;
            }
            if (vm.vesselBeam == null || vm.vesselBeam.length == 0){
                console.log("beam empty");
                vm.vesselBeam = 0;
            } 
            if (vm.vesselWeight == null || vm.vesselWeight.length == 0){
                console.log("weigth empty");
                vm.vesselWeight = 0;
            }
            if (from_update){
                return true;
            } else {
                vm.update();
            }
        },
        checkGuests: function(){
            let vm = this;
            if (vm.numAdults < 0 || vm.numChildren < 0 || vm.numInfants < 0){
                swal({
                    title: 'Invalid Guest Amount',
                    text: "Number of guests cannot be a negative value.",
                    type: 'warning',
                    showCancelButton: false,
                    confirmButtonText: 'OK',
                    showLoaderOnConfirm: true,
                    allowOutsideClick: false
                });
            } else {
                vm.update();
            }
        },
        validateVessel: function(){
            let vm = this;
            if (vm.vesselRego.length < 1 || vm.vesselRego == ' '){
                swal({
                  title: 'Invalid Vessel Registration',
                  text: "Please enter a valid vessel registration",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                });
            }
            if (vm.vesselSize < 0.1){
                swal({
                  title: 'Invalid Vessel Size',
                  text: "Please enter a valid vessel size",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                });
            }
            if (vm.vesselDraft < 0.1){
                swal({
                  title: 'Invalid Vessel Draft',
                  text: "Please enter a valid vessel draft",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                });
            }
            if (vm.vesselBeam < 0.1){
                swal({
                  title: 'Invalid Vessel Beam',
                  text: "Please enter a valid vessel beam",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                });
            }
            if (vm.vesselWeight < 0.1){
                swal({
                  title: 'Invalid Vessel Weight',
                  text: "Please enter a valid vessel weight",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                });
            }

        },
        update: function() {
            var vm = this;
            vm.loadingID = vm.loadingID + 1;
            vm.sites = [];
            var ready = vm.checkDetails(true);
            if (ready){
                vm.isLoading =true;
                $('#spinnerLoader').show();
                debounce(function() {
                    var params = {
                            arrival: moment(vm.arrivalDate).format('YYYY/MM/DD'),
                            departure: moment(vm.departureDate).format('YYYY/MM/DD'),
                            num_adult: vm.numAdults,
                            num_child: vm.numChildren,
                            num_concession: vm.numConcessions,
                            num_infant: vm.numInfants,
                            vessel_size: vm.vesselSize,
                            vessel_draft: vm.vesselDraft,
                            vessel_beam: vm.vesselBeam,
                            vessel_weight: vm.vesselWeight,
                            vessel_rego: vm.vesselRego,
                            distance_radius: vm.distanceRadius
                        };
                    if (parseInt(vm.parkstayGroundRatisId) > 0) {
                        var url = vm.parkstayUrl + '/api/availability_ratis/'+ vm.parkstayGroundRatisId +'/?'+$.param(params);
                    } else if (vm.useAdminApi) {
                        var url = vm.parkstayUrl + '/api/availability_admin/'+ vm.parkstayGroundId +'/?'+$.param(params);
                    } else {
                        vm.updateURL();
                        var url = vm.parkstayUrl + '/api/availability2/'+ vm.parkstayGroundId +'.json/?'+$.param(params);
                    }

                    // var options = [null, "", " "]
                    var search = true;
                    // if(options.indexOf(vm.vesselRego) >= 0 || options.indexOf(vm.vesselSize) >= 0 || options.indexOf(vm.vesselDraft) >= 0 || options.indexOf(vm.vesselBeam) >= 0 || options.indexOf(vm.vesselWeight) >= 0){
                    //     search = false;
                    // }
                    if (search){
                        $.ajax({
                            loadID: vm.loadingID,
                            url: url,
                            dataType: 'json',
                            // async: false,
                            success: function(data, stat, xhr) {
                                vm.name = data.name;
                                vm.days = data.days;
                                vm.classes = data.classes;
                                vm.long_description = data.long_description;
                                vm.map = data.map;
                                vm.ongoing_booking = data.ongoing_booking;
                                vm.ongoing_booking_id = data.ongoing_booking_id;
                                vm.mooring_vessel_size = data.vessel_size;
                                vm.max_advance_booking = data.max_advance_booking;
                                vm.max_advance_booking_days = data.max_advance_booking_days;
                                vm.current_booking = data.current_booking;
                                vm.booking_changed = data.booking_changed;
                                vm.total_booking = data.total_booking;
                                vm.timer = data.timer;
                                vm.expiry = data.expiry;
                
                                if (data.error_type != null) {
                                    vm.status = 'online';
                                    return;
                                }

                                if (data.sites == null) { 
                                return;
                                }

                                if (data.sites.length == 0) {
                                    // vm.status = 'empty';
                                    // return;
                                }

                                vm.gearTotals.tent = 0
                                vm.gearTotals.campervan = 0
                                vm.gearTotals.caravan = 0
                                data.sites.forEach(function(el) {
                                    el.showBreakdown = false;
                                    vm.gearTotals.tent += el.gearType.tent ? 1 : 0;
                                    vm.gearTotals.campervan += el.gearType.campervan ? 1 : 0;
                                    vm.gearTotals.caravan += el.gearType.caravan ? 1 : 0;
                                });
                                if (!vm.gearTotals[vm.gearType]) {
                                    if (vm.gearTotals.tent) {
                                        vm.gearType = 'tent';
                                    } else if (vm.gearTotals.campervan) {
                                        vm.gearType = 'campervan';
                                    } else if (vm.gearTotals.caravan) {
                                        vm.gearType = 'caravan';
                                    } else {
                                        // no campsites at all!
                                        vm.gearType = 'tent';
                                    }
                                }

                                // Booking Whole Row Index
                                var index;
                                var avail_index;
                                var filtered_sites = [];
                                vm.sites = data.sites;
                                vm.mooring_book_row = [];
                                vm.mooring_book_row_disabled = [];
                                vm.mooring_book_row_price = [];
                                vm.mooring_book_row_display = [];

                                for (index = 0; index < vm.sites.length; ++index) {
                                    vm.mooring_book_row[index] = true;
                                    vm.mooring_book_row_disabled[index] = false;
                                    vm.mooring_book_row_price[index] = '0.00';
                                    vm.mooring_book_row_display[index] = 'show';

                                    if (vm.sites[index].vessel_size_limit > 0){
                                        if (vm.sites[index].vessel_size_limit < vm.vesselSize){
                                            if (!filtered_sites.indexOf(vm.sites[index].id) >= 0){
                                            filtered_sites.push(vm.sites[index].id); 
                                            }
                                        }
                                    } 
                                    if (vm.sites[index].vessel_draft_limit > 0){
                                        if (vm.sites[index].vessel_draft_limit < vm.vesselDraft){
                                            if (!filtered_sites.indexOf(vm.sites[index].id) >= 0){
                                            filtered_sites.push(vm.sites[index].id); 
                                            }
                                        }
                                    }
                                    if (vm.sites[index].vessel_beam_limit > 0){
                                        if (vm.sites[index].vessel_beam_limit < vm.vesselBeam){
                                            if (!filtered_sites.indexOf(vm.sites[index].id) >= 0){
                                            filtered_sites.push(vm.sites[index].id); 
                                            }
                                        }
                                    }
                                    if (vm.sites[index].vessel_weight_limit > 0){
                                        if (vm.sites[index].vessel_weight_limit < vm.vesselWeight){
                                            if (!filtered_sites.indexOf(vm.sites[index].id) >= 0){
                                            filtered_sites.push(vm.sites[index].id); 
                                            }
                                        }
                                    }
                                    for (avail_index = 0; avail_index < vm.sites[index].availability.length; ++avail_index) {
                                        var booking_period = vm.sites[index].availability[avail_index][1].booking_period;  
                                        if (booking_period.length > 0) { 
                                            if (vm.sites[index].mooring_class == 'small') {
                                                var total = parseFloat(vm.mooring_book_row_price[index]) + parseFloat(booking_period[0].small_price);
                                                vm.mooring_book_row_price[index] = total.toFixed(2);
                                            } else if (vm.sites[index].mooring_class == 'medium') {
                                                var total = parseFloat(vm.mooring_book_row_price[index]) + parseFloat(booking_period[0].medium_price);
                                                vm.mooring_book_row_price[index] = total.toFixed(2);
                                            } else if (vm.sites[index].mooring_class == 'large') {
                                                var total = parseFloat(vm.mooring_book_row_price[index]) + parseFloat(booking_period[0].large_price);
                                                vm.mooring_book_row_price[index] = total.toFixed(2);
                                            }
                                            if (booking_period.length > 1) {
                                                    vm.mooring_book_row[index] = false;
                                            } else {      
                                                if (booking_period[0].status == 'closed' || booking_period[0].status == 'selected' || booking_period[0].status == 'perday' || booking_period[0].status == 'maxstay' || booking_period[0].status == 'toofar' || booking_period[0].status == 'maxstay') {
                                                    // vm.mooring_book_row[index] = 'disabled';
                                                    vm.mooring_book_row_disabled[index] = true;	
                                                }
                                            }
                                        } else {
                                            vm.mooring_book_row[index] = false;
                                        }
                                    }
                                }
                                var i;
                                for (i = 0; i < filtered_sites.length; i++){
                                    var index;
                                    for (index = 0; index < vm.sites.length; index++){
                                        if (vm.sites[index].id == filtered_sites[i]){
                                            console.log("removed one");
                                            vm.mooring_book_row_display[index] = 'hide';
                                        //    vm.sites.splice(index, 1); 
                                        }
                                    }
                                }

                                console.log("done");

                                // End of booking whole row index
                                vm.status = 'online';
                                if (parseInt(vm.parkstayGroundRatisId) > 0){
                                    vm.parkstayGroundId = data.id;
                                    vm.updateURL();
                                }
	                        if (this.loadID == vm.loadingID) {
          	                  vm.isLoading =false;
                	          $('#spinnerLoader').hide();
                                }

                            },
                            error: function(xhr, stat, err) {
                                vm.showSecondErrorLine = true;
                                var max_error = 'Maximum number of people exceeded for the selected campsite';
                                var min_error = 'Number of people is less than the minimum allowed for the selected campsite';
                                if (xhr.responseJSON.hasOwnProperty('closed')){
                                    vm.status = 'closed';
                                }
                                else if (xhr.responseJSON.hasOwnProperty('error') && (xhr.responseJSON.error == max_error || xhr.responseJSON.error == min_error)){
                                    vm.status = 'offline';
                                    vm.showSecondErrorLine = false;
                                }
                                else {
		                      swal({
                		          title: 'Error',
		                          text: 'Uknown Error',
                		          type: 'warning',
                		          showCancelButton: false,
		                          confirmButtonText: 'OK',
	        	                  showLoaderOnConfirm: true,
	       	        	           allowOutsideClick: false
        	                	})

                                    vm.status = 'offline';
                                }
                                if (this.loadID == vm.loadingID) {
                                  vm.isLoading =false;
                                  $('#spinnerLoader').hide();
                                }
                            }
                        });
                    }
                }, 500)();
            }
            
        }
    },
    mounted: function () {
        var vm = this;

        $(document).foundation();
        this.arrivalEl = $('#date-arrival');
        this.arrivalData = this.arrivalEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                // disallow start dates before today
                return date.valueOf() < now.valueOf() ? 'disabled': '';
                //return '';
            }
        }).on('changeDate', function (ev) {
            ev.target.dispatchEvent(new CustomEvent('change'));
        }).on('change', function (ev) {
            if (vm.arrivalData.date.valueOf() >= vm.departureData.date.valueOf()) {
                var newDate = moment(vm.arrivalData.date).add(1, 'days').toDate();
                vm.departureData.date = newDate;
                vm.departureData.setValue();
                vm.departureData.fill();
                vm.departureEl.trigger('changeDate');
            }
            vm.arrivalData.hide();
            vm.arrivalDate = moment(vm.arrivalData.date);
            vm.days = Math.floor(moment.duration(vm.departureDate.diff(vm.arrivalDate)).asDays());
            vm.sites = [];
        }).on('keydown', function (ev) {
            if (ev.keyCode == 13) {
                ev.target.dispatchEvent(new CustomEvent('change'));
            }
        }).data('datepicker');

        this.departureEl = $('#date-departure');
        this.departureData = this.departureEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                return (date.valueOf() <= vm.arrivalData.date.valueOf()) ? 'disabled': '';
            }
        }).on('changeDate', function (ev) {
            ev.target.dispatchEvent(new CustomEvent('change'));
        }).on('change', function (ev) {
            vm.departureData.hide();
            vm.departureDate = moment(vm.departureData.date);
            vm.days = Math.floor(moment.duration(vm.departureDate.diff(vm.arrivalDate)).asDays());
            vm.sites = [];
        }).on('keydown', function (ev) {
            if (ev.keyCode == 13) {
                ev.target.dispatchEvent(new CustomEvent('change'));
            }
        }).data('datepicker');


        this.arrivalData.date = this.arrivalDate.toDate();
        this.arrivalData.setValue();
        this.arrivalData.fill();
        this.departureData.date = this.departureDate.toDate();
        this.departureData.setValue();
        this.departureData.fill();
        this.update();

            var saneTz = (0 < Math.floor((vm.expiry - moment.now())/1000) < vm.timer);
            var timer = setInterval(function (ev) {
                // fall back to the pre-encoded timer
                if (!saneTz) {
                    vm.timer -= 1;
                } else {
                    // if the timezone is sane, do live updates
                    // this way unloaded tabs won't cache the wrong time.
                    var newTimer = Math.floor((vm.expiry - moment.now())/1000);
                    vm.timer = newTimer;
                }

                if ((vm.timer <= -1)) {
//                   clearInterval(timer);
//                    var loc = window.location;
//                    window.location = loc.protocol + '//' + loc.host + loc.pathname;
               }
            }, 1000);
        // Fix white space which appears on the right of the availablity screen START
        $('#guests-button').click();
        $('#guests-button').click();
        // Fix white space which appears on the right of the availablity screen END



    }
}
</script>

