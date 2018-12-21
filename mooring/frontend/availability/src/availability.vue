<template>
    <div id="sites-cal" class="f6inject">
        <a name="makebooking" />
        <div class="row" v-if="status == 'offline'">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Sorry, this marine park doesn't yet support online bookings. Please visit the <a href="">Mooring Availability checker</a> for expected availability.
                </div>
            </div>
        </div>
        <div class="row" v-else-if="status == 'empty'">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Sorry, this marine park doesn't yet have any mooring assigned to it. Please visit the <a href="">Mooring Availability checker</a> for expected availability.
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

        <div class="row" v-if="name">
            <div class="columns small-12">
                <h1>Book mooring: {{ name }}</h1>
            </div>
        </div>
        <div v-if="ongoing_booking" class="row">
            <div class="columns small-12 medium-12 large-12">
                <div class="clearfix">
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
            <div v-if="long_description" class="columns small-12 medium-12 large-12">
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
            <div class="columns small-6 medium-6 large-2">
                <label>Vessel Size
                    <input id="vesselSize" type="number" placeholder="0" v-on:change="update" v-model="vesselSize"/>
                </label>
            </div>
            <div class="columns small-6 medium-6 large-2">
                <label>Vessel Draft 
                    <input id="vesselDraft" type="number" placeholder="0" v-on:change="update" v-model="vesselDraft"/>
                </label>
            </div>


            <div v-if="!useAdminApi" class="small-6 medium-6 large-3 columns" style='display:none'>
                <label>
                    Guests 
                    <input type="button" class="button formButton" v-bind:value="numPeople" data-toggle="guests-dropdown"/>
                </label>
                <div class="dropdown-pane" id="guests-dropdown" data-dropdown data-auto-focus="true">
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="num_adults" class="text-right">Adults (non-concessions)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numAdults" name="num_adults" @change="update()" v-model="numAdults" min="0" max="16"/>
                        </div>
                    </div>
                    <div class="row">
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
                            <input type="number" id="numConcessions" name="num_concessions" @change="update()" v-model="numConcessions" min="0" max="16"/>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="num_children" class="text-right">Children (ages 6-15)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numChildren" name="num_children" @change="update()" v-model="numChildren" min="0" max="16"/>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="num_infants" class="text-right">Infants (ages 0-5)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numInfants" name="num_infants" @change="update()" v-model="numInfants" min="0" max="16"/>
                        </div>
                    </div>
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="num_infants" class="text-right">Mooring</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numMooring" name="num_mooring" @change="update()" v-model="numMooring" min="0" max="16"/>
                        </div>
                    </div>
                </div>
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

        <div class="row" v-show="status == 'online'"><div class="columns table-scroll">
             <div v-if="mooring_vessel_size > vesselSize && mooring_vessel_draft > vesselDraft" class="small-12 medium-12 large-12">
            <table class="hover">
                <thead>
                    <tr>
                        <th class="site">Mooring &nbsp;<a class="float-right" target="_blank" :href="map" v-if="map" style='display: none;'>View Map</a> </th>
                        <th class="book">Book</th>
                        <th class="date" v-for="i in days">{{ getDateString(arrivalDate, i-1) }}</th>
                    </tr>
                </thead>
                <tbody><template v-for="site in sites" v-if="site.gearType[gearType]">
                    <tr>
                        <td class="site">{{ site.name }}<span v-if="site.warning" class="siteWarning"> - {{ site.warning }}</span></td>
                        <td class="book">
                            <template v-if="site.price">
                                <button v-if="!ongoing_booking" @click="submitBooking(site)" class="button"><small>Book now</small><br/>{{ site.price }}</button>
                                <button v-else disabled class="button has-tip" data-tooltip aria-haspopup="true" title="Please complete your current ongoing booking using the button at the top of the page."><small>Book now</small><br/>{{ site.price }}</button>
                            </template>
                            <template v-else>
                                <button v-if="site.breakdown" class="button warning" @click="toggleBreakdown(site)"><small>Show availability</small></button>
                                <button v-else class="button secondary disabled" disabled><small>Change dates</small></button>
                            </template>
                        </td>
                        <td class="date" v-for="day in site.availability" v-bind:class="{available: day[0]}" >{{ day[1] }}</td>
                    </tr>
                    <template v-if="site.showBreakdown"><tr v-for="line in site.breakdown" class="breakdown">
                        <td class="site">Site: {{ line.name }}</td>
                        <td></td>
                        <td class="date" v-for="day in line.availability" v-bind:class="{available: day[0]}" >{{ day[1] }}</td>
                    </tr></template>
                </template></tbody>
            </table>
            </div>
     <div v-if="mooring_vessel_size <= vesselSize || mooring_vessel_draft <= vesselDraft" class="small-12 medium-12 large-12">
          <table class="hover">
                <tbody>
                  <tr>

                     <td>
         Your vessel size does not suit the selected mooring,  Please choose a mooring suited to your vessel. Click <A HREF="/map/">here</A> to go back to map.
                     </td>
		  </tr>
	        </tbody>
          </table>
     </div>

     <div v-if="max_advance_booking_days > max_advance_booking" class="small-12 medium-12 large-12">
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

    // table font colour override
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
}

</style>

<script>

import 'foundation-sites';
import 'foundation-datepicker/js/foundation-datepicker';
import debounce from 'debounce';
import moment from 'moment';
import swal from 'sweetalert2';
import 'sweetalert2/dist/sweetalert2.css';

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
            numAdults: parseInt(getQueryParam('num_adult', 0)),
            numChildren: parseInt(getQueryParam('num_children', 0)),
            numConcessions: parseInt(getQueryParam('num_concession', 0)),
            numInfants: parseInt(getQueryParam('num_infants', 0)),
            numMooring: parseInt(getQueryParam('num_mooring', 1)),
            vesselSize: parseInt(getQueryParam('vessel_size', 0)),
            vesselDraft: parseInt(getQueryParam('vessel_draft', 0)),
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
            showSecondErrorLine: true,
        };
    },
    computed: {
        numPeople: {
            cache: false,
            get: function() {
                var count = parseInt(this.numAdults) + parseInt(this.numConcessions) + parseInt(this.numChildren) + parseInt(this.numInfants) + parseInt(this.numMooring);
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
        submitBooking: function (site) {
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
                num_mooring: vm.numMooring,
                num_concession: vm.numConcessions,
                num_infant: vm.numInfants,
                vessel_size: vm.vesselSize,
                vessel_draft: vm.vesselDraft,
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
                    //console.log(data);
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
                num_mooring: vm.numMooring,
                vessel_size : vm.vesselSize,
                vessel_draft: vm.vesselDraft,
                
            });
            history.replaceState('', '', newHist);
        },
        update: function() {
            var vm = this;

            debounce(function() {
                var params = {
                        arrival: moment(vm.arrivalDate).format('YYYY/MM/DD'),
                        departure: moment(vm.departureDate).format('YYYY/MM/DD'),
                        num_adult: vm.numAdults,
                        num_child: vm.numChildren,
                        num_concession: vm.numConcessions,
                        num_infant: vm.numInfants,
                        num_mooring: vm.numMooring,
                        vessel_size: vm.vesselSize,
                        vessel_draft: vm.vesselDraft
                        
                    };

                if (parseInt(vm.parkstayGroundRatisId) > 0){
                    var url = vm.parkstayUrl + '/api/availability_ratis/'+ vm.parkstayGroundRatisId +'/?'+$.param(params);
                } else if (vm.useAdminApi) {
                    var url = vm.parkstayUrl + '/api/availability_admin/'+ vm.parkstayGroundId +'/?'+$.param(params);
                } else {
                    vm.updateURL();
                    var url = vm.parkstayUrl + '/api/availability/'+ vm.parkstayGroundId +'.json/?'+$.param(params);
                }
                
                $.ajax({
                    url: url,
                    dataType: 'json',
                    success: function(data, stat, xhr) {
                        vm.name = data.name;
                        vm.days = data.days;
                        vm.classes = data.classes;
                        vm.long_description = data.long_description;
                        vm.map = data.map;
                        vm.ongoing_booking = data.ongoing_booking;
                        vm.ongoing_booking_id = data.ongoing_booking_id;
                        vm.mooring_vessel_size = data.vessel_size;
                        vm.mooring_vessel_draft = data.vessel_draft;
                        vm.max_advance_booking = data.max_advance_booking;
                        vm.max_advance_booking_days = data.max_advance_booking_days;

                        if (data.error_type != null) {
                            vm.status = 'online';
                            return;
                        }

                        if (data.sites == null) { 
                          return;
			}

                        if (data.sites.length == 0) {
                            vm.status = 'empty';
                            return;
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

                        vm.sites = data.sites;
                        vm.status = 'online';
                        if (parseInt(vm.parkstayGroundRatisId) > 0){
                            vm.parkstayGroundId = data.id;
                            vm.updateURL();
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
                        else{
                            vm.status = 'offline';
                        }
                    }
                });
            }, 500)();
        }
    },
    mounted: function () {
        var vm = this;
        $(document).foundation();
        console.log('DATE PICKER'); 
        this.arrivalEl = $('#date-arrival');
        this.arrivalData = this.arrivalEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                // disallow start dates before today
                return date.valueOf() < now.valueOf() ? 'disabled': '';
                //return '';
            }
        }).on('changeDate', function (ev) {
            console.log('arrivalEl changeDate');
            ev.target.dispatchEvent(new CustomEvent('change'));
        }).on('change', function (ev) {
            console.log('arrivalEl change');
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
            console.log('departureEl changeDate');
            ev.target.dispatchEvent(new CustomEvent('change'));
        }).on('change', function (ev) {
            console.log('departureEl change');
            vm.departureData.hide();
            vm.departureDate = moment(vm.departureData.date);
            vm.days = Math.floor(moment.duration(vm.departureDate.diff(vm.arrivalDate)).asDays());
            vm.sites = [];
        }).on('keydown', function (ev) {
            if (ev.keyCode == 13) {
                ev.target.dispatchEvent(new CustomEvent('change'));
            }
        }).data('datepicker');
        console.log('DATE PICKER END');

        this.arrivalData.date = this.arrivalDate.toDate();
        this.arrivalData.setValue();
        this.arrivalData.fill();
        this.departureData.date = this.departureDate.toDate();
        this.departureData.setValue();
        this.departureData.fill();
        this.update();
    }
}
</script>


