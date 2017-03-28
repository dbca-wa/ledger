<template>
    <div id="sites-cal" class="f6inject">
        <a name="makebooking" />
        <div class="row" v-if="status == 'offline'">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Sorry, this campground doesn't yet support online bookings. Please visit the <a href="https://parks-oim.dpaw.wa.gov.au/campgrounds-status">Camp Site Availability checker</a> for expected availability.
                </div>
            </div>
        </div>
        <div class="row" v-if="errorMsg">
            <div class="columns small-12 medium-12 large-12">
                <div class="callout alert">
                    Sorry, there was an error placing the booking ({{ errorMsg }}). Please try again.
                </div>
            </div>
        </div>

        <div class="row" v-if="name">
            <div class="columns small-12">
                <h1>Book a campsite at {{ name }}</h1>
            </div>
        </div>
        <div class="row" v-show="status == 'online'">
            <div class="columns small-6 medium-6 large-3">
                <label>Arrival
                    <input id="date-arrival" type="text" placeholder="dd/mm/yyyy"/>
                </label>
            </div>
            <div class="columns small-6 medium-6 large-3">
                <label>Departure
                    <input id="date-departure" type="text" placeholder="dd/mm/yyyy"/>
                </label>
            </div>
            <div class="small-6 medium-6 large-3 columns">
                <label>
                    Guests 
                    <input type="button" class="button formButton" v-bind:value="numPeople" data-toggle="guests-dropdown"/>
                </label>
                <div class="dropdown-pane" id="guests-dropdown" data-dropdown data-auto-focus="true">
                    <div class="row">
                        <div class="small-6 columns">
                            <label for="num_adults" class="text-right">Adults</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numAdults" name="num_adults" @change="update()" v-model="numAdults" min="0" max="16"/>
                        </div>
                    </div><div class="row">
                        <div class="small-6 columns">
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
                    </div><div class="row">
                        <div class="small-6 columns">
                            <label for="num_children" class="text-right">Children (ages 6-15)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numChildren" name="num_children" @change="update()" v-model="numChildren" min="0" max="16"/>
                        </div>
                    </div><div class="row">
                        <div class="small-6 columns">
                            <label for="num_infants" class="text-right">Infants (ages 0-5)</label>
                        </div><div class="small-6 columns">
                            <input type="number" id="numInfants" name="num_infants" @change="update()" v-model="numInfants" min="0" max="16"/>
                        </div>
                    </div>
                </div>
            </div>
            <div class="columns small-6 medium-6 large-3">
                <label>Equipment
                    <select name="gear_type" v-model="gearType" @change="update()">
                        <option value="tent">Tent</option>
                        <option value="campervan">Campervan</option>
                        <option value="caravan">Caravan</option>
                    </select>
                </label>
            </div>
        </div>
        <div class="row" v-show="status == 'online'"><div class="columns table-scroll">
            <table class="hover">
                <thead>
                    <tr>
                        <th class="site">Campsite</th>
                        <th class="book">Book</th>
                        <th class="date" v-for="i in days">{{ getDateString(arrivalDate, i-1) }}</th>
                    </tr>
                </thead>
                <tbody><template v-for="site in sites">
                    <tr>
                        <td class="site">{{ site.name }}<span v-if="site.class"> - {{ classes[site.class] }}</span></td>
                        <td class="book">
                            <button v-if="site.price" @click="submitBooking(site)" class="button"><small>Book now</small><br/>{{ site.price }}</button>
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
        </div></div>
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

    .dropdown-pane {
        width: auto;
    }
}

</style>

<script>

import 'foundation-sites';
import 'foundation-datepicker/js/foundation-datepicker';
import debounce from 'debounce';
import moment from 'moment';


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
            parkstayGroundId: global.parkstayGroundId || '1',
            days: 5,
            numAdults: parseInt(getQueryParam('num_adult', 2)),
            numChildren: parseInt(getQueryParam('num_children', 0)),
            numConcessions: parseInt(getQueryParam('num_concession', 0)),
            numInfants: parseInt(getQueryParam('num_infants', 0)),
            maxAdults: 30,
            maxChildren: 30,
            gearType: getQueryParam('gear_type', 'tent'),
            status: null,
            errorMsg: null,
            classes: {},
            sites: []
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
    },
    methods: {
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
            var submitData = {
                arrival: moment(vm.arrivalDate).format('YYYY/MM/DD'),
                departure: moment(vm.departureDate).format('YYYY/MM/DD'),
                num_adult: vm.numAdults,
                num_child: vm.numChildren,
                num_concession: vm.numConcessions,
                num_infant: vm.numInfants,
            };
            if (site.type == 0) { // per site listing
                submitData.campsite = site.id;
            } else {
                submitData.campground = vm.parkstayGroundId;
                submitData.campsite_class = site.type;
            }
            console.log(site);
            console.log(submitData);
            $.ajax({
                url: vm.parkstayUrl + '/api/create_booking',
                method: 'POST',
                data: submitData,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    console.log(data);
                    if (data.status == 'success') {
                        window.location.href = '/booking';
                    }
                },
                error: function(data, stat, xhr) {
                    console.log('POST error');
                    console.log(data);
                    vm.errorMsg = data.msg ? data.msg : 'Sorry, an error occurred when communicating with Parkstay. Please try again later.';
                    vm.update();
                }
            });
        },
        update: function() {
            var vm = this;
            debounce(function() {
                var url = vm.parkstayUrl + '/api/availability/'+ vm.parkstayGroundId +'/?'+$.param({
                    arrival: moment(vm.arrivalDate).format('YYYY/MM/DD'),
                    departure: moment(vm.departureDate).format('YYYY/MM/DD'),
                    num_adult: vm.numAdults,
                    num_child: vm.numChildren,
                    num_concession: vm.numConcessions,
                    num_infant: vm.numInfants,
                    gear_type: vm.gearType
                });
                console.log('AJAX '+url);
                $.ajax({
                    url: url,
                    dataType: 'json',
                    success: function(data, stat, xhr) {
                        vm.name = data.name;
                        vm.days = data.days;
                        vm.classes = data.classes;
                        data.sites.forEach(function(el) {
                            el.showBreakdown = false;
                        });
                        vm.sites = data.sites;
                        vm.status = 'online';
                    },
                    error: function(data, stat, xhr) {
                        vm.status = 'offline';
                    }
                });
            }, 500)();
        }
    },
    mounted: function () {
        var vm = this;
        $(document).foundation();

        var arrivalEl = $('#date-arrival');
        var arrivalData = arrivalEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                // disallow start dates before today
                //return date.valueOf() < now.valueOf() ? 'disabled': '';
                return '';
            }
        }).on('changeDate', function (ev) {
            console.log('arrivalEl changeDate');
            if (arrivalData.date.valueOf() >= departureData.date.valueOf()) {
                var newDate = moment(arrivalData.date).add(1, 'days').toDate();
                departureData.date = newDate;
                departureData.setValue();
                departureData.fill();
                departureEl.trigger('changeDate');
            }
            arrivalData.hide();
            vm.arrivalDate = moment(arrivalData.date);
            vm.days = Math.floor(moment.duration(vm.departureDate.diff(vm.arrivalDate)).asDays());
            vm.sites = [];
            vm.update();
        }).data('datepicker');

        var departureEl = $('#date-departure');
        var departureData = departureEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                return (date.valueOf() <= arrivalData.date.valueOf()) ? 'disabled': '';
            }
        }).on('changeDate', function (ev) {
            console.log('departureEl changeDate');
            departureData.hide();
            vm.departureDate = moment(departureData.date);
            vm.days = Math.floor(moment.duration(vm.departureDate.diff(vm.arrivalDate)).asDays());
            vm.sites = [];
            vm.update();
        }).data('datepicker');



        arrivalData.date = this.arrivalDate.toDate();
        arrivalData.setValue();
        arrivalData.fill();
        departureData.date = this.departureDate.toDate();
        departureData.setValue();
        departureData.fill();
        this.update();
    }
}
</script>


