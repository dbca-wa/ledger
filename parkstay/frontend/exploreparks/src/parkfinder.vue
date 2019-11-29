<template>
    <div v-cloak class="f6inject">
        <div class="row">
            <div class="small-12 medium-3 large-6 columns search-params">
                <div class="row">
                    <div class="small-12 columns">
                        <label>Search <input class="input-group-field" id="searchInput" type="text" placeholder="Search for campgrounds, parks, addresses..."/></label>
                    </div>
                </div><div class="row">
                    <div class="small-12 medium-12 large-4 columns">
                        <label>Arrival <input id="dateArrival" name="arrival" type="text" placeholder="dd/mm/yyyy" v-on:change="updateDates"/></label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label>Departure <input id="dateDeparture" name="departure" type="text" placeholder="dd/mm/yyyy" v-on:change="updateDates"/></label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label>
                            Guests <input type="button" class="button formButton" v-bind:value="numPeople" data-toggle="guests-dropdown"/>
                        </label>
                        <div class="dropdown-pane" id="guests-dropdown" data-dropdown data-auto-focus="true">
                            <div class="row">
                                <div class="small-6 columns">
                                    <label for="num_adults" class="text-right">Adults (non-concessions)</label>
                                </div><div class="small-6 columns">
                                   <label> <input type="number" id="numAdults" name="num_adults" v-model.number="numAdults" min="0" max="16"/></label>
                                </div>
                            </div><div class="row">
                                <div class="small-6 columns">
                                <!-- <a class="button" v-bind:href="f.info_url" target="_blank">More info</a> -->
                                    <label for="num_concessions" class="text-right"><span class="has-tip" title="Holders of one of the following Australian-issued cards:
- Seniors Card
- Age Pension
- Disability Support
- Carer Payment
- Carer Allowance
- Companion Card
- Department of Veterans' Affairs">Concessions</span></label>
                                </div><div class="small-6 columns">
                                  <label>  <input type="number" id="numConcessions" name="num_concessions" v-model.number="numConcessions" min="0" max="16"/></label>
                                </div>
                            </div><div class="row">
                                <div class="small-6 columns">
                                    <label for="num_children" class="text-right">Children (ages 6-15)</label>
                                </div><div class="small-6 columns">
                                   <label> <input type="number" id="numChildren" name="num_children" v-model.number="numChildren" min="0" max="16"/></label>
                                </div>
                            </div><div class="row">
                                <div class="small-6 columns">
                                    <label for="num_infants" class="text-right">Infants (ages 0-5)</label>
                                </div><div class="small-6 columns">
                                 <label>   <input type="number" id="numInfants" name="num_infants" v-model.number="numInfants" min="0" max="16"/></label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="small-12 medium-12 large-12 columns">
                        <label><input type="checkbox" v-model="bookableOnly"/> Show bookable campsites only</label>
                    </div>
                </div><div class="row"><div class="small-12 columns">
                    <hr/>
                </div></div><div class="row">
                    <div class="small-12 medium-12 large-12 columns">
                        <label>Select equipment</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="gear_type" value="all" v-model="gearType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC3"></i> All types</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="gear_type" value="tent" v-model="gearType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC2"></i> Tent</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="gear_type" value="campervan" v-model="gearType" class="show-for-sr" v-on:change="reload()"/><i class="symb RV10"></i> Campervan</label>
                    </div>
                    <div class="small-12 medium-12 large-5 columns">
                        <label><input type="radio" name="gear_type" value="caravan" v-model="gearType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC4"></i> Caravan / Camper trailer</label>
                    </div>
                </div><div class="row"><div class="small-12 columns">
                    <hr class="search"/>
                </div></div><div class="row">
                    <div class="small-12 medium-12 large-12 columns">
                        <label>Select features</label>
                    </div>
                    <template v-for="filt in filterList">
                        <div class="small-12 medium-12 large-4 columns">
                            <label><input type="checkbox" class="show-for-sr" :value="'filt_'+ filt.key" v-model="filterParams[filt.key]" v-on:change="updateFilter()"/> <i class="symb" :class="filt.symb"></i> {{ filt.name }}</label>
                        </div>
                    </template>
                    <template v-for="filt in extraFilterList">
                        <div class="small-12 medium-12 large-4 columns" v-bind:class="{'filter-hide': hideExtraFilters}">
                            <label><input type="checkbox" class="show-for-sr" :value="'filt_'+ filt.key" v-model="filterParams[filt.key]" v-on:change="updateFilter()"/> <i class="symb" :class="filt.symb"></i> {{ filt.name }}</label>
                        </div>
                    </template>
                </div><div class="row">
                    <div class="small-12 medium-12 large-4 columns" v-bind:class="{'filter-hide': hideExtraFilters}">
                        <label><input type="checkbox" v-model="sitesOnline" v-on:change="updateFilter()"/><img v-bind:src="sitesOnlineIcon" width="24" height="24"/> Online bookings</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns" v-bind:class="{'filter-hide': hideExtraFilters}">
                        <label><input type="checkbox" v-model="sitesInPerson" v-on:change="updateFilter()"/><img v-bind:src="sitesInPersonIcon" width="24" height="24"/> No online bookings</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns" v-bind:class="{'filter-hide': hideExtraFilters}">
                        <label><input type="checkbox" v-model="sitesAlt" v-on:change="updateFilter()"/><img v-bind:src="sitesAltIcon" width="24" height="24"/> Third-party site</label>
                    </div>
                    <div class="small-12 medium-12 large-12 columns filter-button">
                        <button class="button expanded" v-on:click="toggleShowFilters"><span v-if="hideExtraFilters">Show more filters ▼</span><span v-else>Hide filters ▲</span></button>
                    </div>
                </div>
            </div>
            <div class="small-12 medium-9 large-6 columns">
                <div id="map"></div>
                <div id="mapPopup" class="mapPopup" v-cloak>
                    <a href="#" id="mapPopupClose" class="mapPopupClose"></a>
                    <div id="mapPopupContent">
                        <h4 style="margin: 0"><b id="mapPopupName"></b></h4>
                        <p><i id="mapPopupPrice"></i></p>
                        <img class="thumbnail" id="mapPopupImage" />
                        <div id="mapPopupDescription" style="font-size: 0.75rem;"/>

                        <!-- Add line to join the 2 buttons into 1 -->
                       <!--  <a id="mapPopupBookInfo" class="button formButton" style="margin-bottom: 0;" target="_blank">More Info/Book now</a> -->

                         <a id="mapPopupBook" class="button formButton1" style="margin-bottom: 0; margin-top: 1em;" target="_blank">Book now</a>
                         <a id="mapPopupInfo" class="button formButton" style="margin-bottom: 0;" target="_blank">More Info</a>

                    </div>
                </div>
            </div>
        </div>
        <template v-if="extentFeatures.length > 0">
            <paginate name="filterResults" class="resultList" :list="extentFeatures" :per="9">
                <div class="row">
                    <div class="small-12 medium-4 large-4 columns" v-for="f in paginated('filterResults')">
                        <div class="row">
                            <div class="small-12 columns">
                                <span class="searchTitle">{{ f.name }}</span>
                            </div>
                            <div class="small-12 medium-12 large-12 columns" v-if="f.images && f.images[0] && f.images[0].image">
                                <img class="thumbnail" v-bind:src="f.images[0].image"/>
                            </div>
                            <div class="small-12 medium-9 large-9 columns">
                                <div v-html="f.description"/>
                                <p v-if="f.price_hint && Number(f.price_hint)"><i><small>From ${{ f.price_hint }} per night</small></i></p>

                                <!-- This line has to be changed to use a v-if/else clause
                                 Changed again to utilize changes in api to further enable forwarding offline sites to availability app
                                 -->

                                <!--<a class="button" v-bind:href="f.info_url" target="_blank">More info</a> -->

                                <!-- <a class="button formButton" v-bind:href="parkstayUrl+'/availability/?site_id='+f.id+'&'+bookingParam" target="_blank">More Info/Book now</a> -->


                                <a v-if="f.campground_type == 0  " class="button formButton1" v-bind:href="parkstayUrl+'/availability/?site_id='+f.id+'&'+bookingParam" target="_blank">Book now</a>

                                <a v-else-if="f.campground_type == 1  " class="button formButton" v-bind:href="parkstayUrl+'/availability/?site_id='+f.id+'&'+bookingParam" target="_blank">More Info</a>

                                <a v-else class="button formButton2" v-bind:href="f.info_url" target="_blank">More info</a>


                            <!-- End of change -->

                            </div>
                        </div>
                    </div>
                </div>
            </paginate>
            <div class="row">
                <paginate-links for="filterResults" :classes="{
                    'ul': 'pagination'
                }"></paginate-links>
            </div>
        </template>
        <template v-else>
            <div class="row align-center">
                <div class="small-12 medium-12 large-12 columns">
                    <h2 class="text-center">There are no campgrounds found matching your search criteria. Please change your search or click <a href="https://exploreparks.dbca.wa.gov.au/know/park-stay-search-tips">here</a> for more information.</h2>
                </div>
            </div>
        </template>
    </div>
</template>

<style lang="scss">

[v-cloak] {
    display: none;
}

@font-face {
    font-family: "DPaWSymbols";
    src: url("./assets/campicon.woff") format("woff");
}

.symb {
    font-family: "DPaWSymbols";
    font-style: normal;
    font-size: 1.5rem;
}

.symb.RC2:before {
    content: "a";
}

.symb.RC4:before {
    content: "b";
}

.symb.RV10:before {
    content: "c";
}

.symb.RG2:before {
    content: "d";
}

.symb.RG15:before {
    content: "e";
}

.symb.RV2:before {
    content: "f";
}

.symb.RF10:before {
    content: "g";
}

.symb.RF13:before {
    content: "h";
}

.symb.RF15:before {
    content: "i";
}

.symb.RF17:before {
    content: "j";
}

.symb.RF1:before {
    content: "k";
}

.symb.RF6:before {
    content: "l";
}

.symb.RF7:before {
    content: "m";
}

.symb.RF19:before {
    content: "n";
}

.symb.RF8G:before {
    content: "o";
}

.symb.RC1:before {
    content: "p";
}

.symb.RC3:before {
    content: "q";
}

.symb.LOC:before {
    content: "r";
}

.symb.RW3:before {
    content: "s";
}

.symb.MAINS:before {
    content: "t";
}

.f6inject {

    .search-params hr {
        margin: 0;
    }

    .search-params label {
        cursor: pointer;
        font-size: 0.8em;
    }

    /* filter hiding on small screens */
    @media print, screen and (max-width: 63.9375em) {
        .filter-hide {
            display: none;
        }
    }

    @media print, screen and (min-width: 64em) {
        .filter-button {
            display: none;
        }
    }

    #map {
        height: 75vh;
    }

    /* set on the #map element when mousing over a feature */
    .click {
        cursor: pointer;
    }

    input + .symb {
        color: #000000;
        transition: color 0.25s ease-out;
    }

    input:checked + .symb {
        color: #2199e8;
    }

    .button.formButton {
        display: block;
        width: 100%;
    }

    .button.formButton1{
      display: block;
      background-color: green;
      width: 100%;
    }

    .button.formButton2{
      display: block;
      background-color: purple;
      width: 100%;
    }

    .button.selector {
        background-color: #fff;
        border: 1px solid #777;
        border-radius: 4px;
        color: #000;
    }

    .button.selector:hover {
        background-color: #d6eaff;
        border: 1px solid #729fcf;
    }

    .button.selector ~ input:checked {
        color: #fff;
        background-color: #0060c4;
        border: 1px solid #00366e;
    }

    .button.selector:hover ~ input:checked {
        color: #fff;
        background-color: #0e83ff;
        border: 1px solid #004d9f;
    }

    .pagination {
        padding: 0;
        text-align: center;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 1em;
    }

    .pagination .active {
        background: #2199e8;
        color: #fefefe;
        cursor: default;
    }

    .pagination li {
        display: inline-block;
        cursor: pointer;
    }

    .tooltip {
        position: relative;
        border-radius: 4px;
        background-color: #ffcc33;
        color: black;
        padding: 4px 8px;
        opacity: 0.7;
        white-space: nowrap;
    }

    .tooltip:before {
        border-top: 6px solid rgba(0, 0, 0, 0.5);
        border-right: 6px solid transparent;
        border-left: 6px solid transparent;
        content: "";
        position: absolute;
        bottom: -6px;
        margin-left: -7px;
        left: 50%;
    }

    .mapPopup {
        position: absolute;
        background-color: white;
        -webkit-filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
        filter: drop-shadow(0 1px 4px rgba(0,0,0,0.2));
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #cccccc;
        bottom: 32px;
        left: -140px;
        width: 280px;
    }

    .mapPopup:after, .mapPopup:before {
        top: 100%;
        border: solid transparent;
        content: " ";
        height: 0;
        width: 0;
        position: absolute;
        pointer-events: none;
    }

    .mapPopup:after {
        border-top-color: white;
        border-width: 10px;
        left: 138px;
        margin-left: -10px;
    }

    .mapPopup:before {
        border-top-color: #cccccc;
        border-width: 11px;
        left: 138px;
        margin-left: -11px;
    }

    .mapPopupClose {
        text-decoration: none;
        position: absolute;
        top: 2px;
        right: 8px;
    }

    .mapPopupClose:after {
        content: "✖";
    }

    .searchTitle {
        font-size: 150%;
        font-weight: bold;
    }

    .resultList {
        padding: 0;
    }
}

/* hacks to make awesomeplete play nice with F6 */
div.awesomplete {
    display: block;
}

div.awesomplete > input {
    display: table-cell;
}

/* hacks to make openlayers widgets more accessible */
.ol-control button {
    height: 2em;
    width: 2em;
}
</style>

<script>
import Vue from 'vue'
import Awesomplete from 'awesomplete';
import ol from 'openlayers';
//var ol = require('openlayers/dist/ol-debug');
import 'foundation-sites/dist/js/foundation.min';
import 'foundation-datepicker/js/foundation-datepicker';
import debounce from 'debounce';
import moment from 'moment' ;


export default {
    name: 'parkfinder',
    el: '#parkfinder',
    data: function () {
        return {
            parkstayUrl: process.env.PARKSTAY_URL || global.parkstayUrl,
            defaultCenter: [13775786.985667605, -2871569.067879858], // [123.75, -24.966],
            defaultLayers: [
                ['dpaw:mapbox_outdoors', {}],
                ['cddp:dpaw_tenure', {}],
            ],
            filterList: [
                {name: '2WD accessible', symb: 'RV2', key: 'twowheel', 'remoteKey': ['2WD/SUV ACCESS']},
                {name: 'Campfires allowed', symb: 'RF10', key: 'campfire', 'remoteKey': ['FIREPIT']},
                {name: 'Dogs allowed', symb: 'RG2', key: 'dogs', 'remoteKey': ['DOGS']}
            ],
            extraFilterList: [
                {name: 'BBQ', symb: 'RF8G', key: 'bbq', 'remoteKey': ['BBQ']},
                {name: 'Dish washing', symb: 'RF17', key: 'dishwashing', 'remoteKey': ['DISHWASHING']},
                {name: 'Dump station', symb: 'RF19', key: 'sullage', 'remoteKey': ['DUMP STATION']},
                {name: 'Generators allowed', symb: 'RG15', key: 'generators', 'remoteKey': ['GENERATORS PERMITTED']},
                {name: 'Mains water', symb: 'RF13', key: 'water', 'remoteKey': ['MAINS WATER']},
                {name: 'Picnic tables', symb: 'RF6', key: 'picnic', 'remoteKey': ['PICNIC TABLE']},
                //{name: 'Sheltered picnic tables', symb: 'RF7', key: 'picnicsheltered', 'remoteKey': ['TABLE - SHELTERED']},
                {name: 'Showers', symb: 'RF15', key: 'showers', 'remoteKey': ['SHOWER']},
                {name: 'Toilets', symb: 'RF1', key: 'toilets', 'remoteKey': ['TOILETS']},
                //{name: 'Walk trail', symb: 'RW3', key: 'walktrail', 'remoteKey': ['WALK TRAIL']},
                {name: 'Powered sites', symb: 'MAINS', key: 'walktrail', 'remoteKey': ['POWERED SITES']},
            ],
            hideExtraFilters: true,
            suggestions: {},
            extentFeatures: [],

            //Added to store values of api date
            currentDate: null,

            arrivalDate: null,
            departureDate: null,
            numAdults: 2,
            numConcessions: 0,
            numChildren: 0,
            numInfants: 0,
            gearType: 'all',
            filterParams: {
            },
            dateSetFirstTime: true,
            sitesOnline: true,
            sitesInPerson: true,
            sitesAlt: true,
            sitesOnlineIcon: require('./assets/pin.svg'),
            sitesInPersonIcon: require('./assets/pin_offline.svg'),
            sitesAltIcon: require('./assets/pin_alt.svg'),
            locationIcon: require('./assets/location.svg'),
            paginate: ['filterResults'],
            selectedFeature: null
        }
    },
    computed: {
        bookableOnly: {
            cache: false,
            get: function() {
                return this.sitesOnline && (!this.sitesInPerson) && (!this.sitesAlt);
            },
            set: function(val) {
                this.sitesOnline = true;
                this.sitesInPerson = !val;
                this.sitesAlt = !val;
                this.reload();
            }
        },
        extent: {
            cache: false,
            get: function() {
                return this.olmap.getView().calculateExtent(this.olmap.getSize());
            }
        },
        center: {
            cache: false,
            get: function() {
                return this.olmap.getView().getCenter();
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
        numPeople: {
            cache: false,
            get: function() {
                // annoying wrapper to deal with vue.js' weak number casting
                var count = (this.numAdults ? this.numAdults : 0) +
                            (this.numConcessions ? this.numConcessions : 0) +
                            (this.numChildren ? this.numChildren : 0) +
                            (this.numInfants ? this.numInfants : 0);
                if (count === 1) {
                    return `${count} person ▼`;
                } else {
                    return `${count} people ▼`;
                }
            }
        },
        bookingParam: {
            cache: false,
            get: function() {
                var params = {
                    'num_adult': this.numAdults,
                    'num_concession': this.numConcessions,
                    'num_children': this.numChildren,
                    'num_infants': this.numInfants,
                    'gear_type': this.gearType,
                };
                if (this.arrivalDate && this.departureDate) {

                    params['arrival'] = this.arrivalDate.format('YYYY/MM/DD');
                    params['departure'] = this.departureDate.format('YYYY/MM/DD');

                }
                return $.param(params);
            }
        }
    },
    methods: {
        toggleShowFilters: function() {
            this.hideExtraFilters = !this.hideExtraFilters;
        },
        search: function(place) {
            if (!place) {
                return;
            }
            var vm = this;
            // search through the autocomplete list first
            var target = this.suggestions['features'].find(function (el) {
                return el['properties']['name'] == place;
            });
            if (target) {
                //console.log('Search suggestion!')
                var view = this.olmap.getView();
                // zoom slightly closer in for campgrounds
                var resolution = vm.resolutions[10];
                if (target['properties']['type'] == 'Campground') {
                    resolution = vm.resolutions[12];
                }
                // pan to the spot, zoom slightly closer in for campgrounds
                view.animate({
                    center: ol.proj.fromLonLat(target['coordinates']),
                    resolution: resolution,
                    duration: 1000
                });

                // Open the popup
                /*
                let feature = this.groundsData.a.find(f => parseInt(f.a) == parseInt(target.properties.id));
                if (feature){
                    setTimeout(() => {
                        vm.popup.setPosition(feature.getGeometry().getCoordinates());
                        // really want to make vue.js render this, except reactivity dies
                        // when you pass control of the popup element to OpenLayers :(
                        $("#mapPopupName")[0].innerHTML = feature.get('name');
                        if (feature.get('images')) {
                            // console.log(feature.get('images')[0].image);
                            $("#mapPopupImage").attr('src', feature.get('images')[0].image);
                            $("#mapPopupImage").show();
                        } else {
                            $("#mapPopupImage").hide();
                        }
                        if (feature.get('price_hint') && Number(feature.get('price_hint'))) {
                            $("#mapPopupPrice")[0].innerHTML = '<small>From $' + feature.get('price_hint') + ' per night</small>';
                        } else {
                            $("#mapPopupPrice")[0].innerHTML = '';
                        }
                        $("#mapPopupDescription")[0].innerHTML = feature.get('description');

                        // Disabled below line,as api is being used to differentiate btw offline and online site
                        $("#mapPopupInfo").attr('href', feature.get('info_url'));


                        // Made changes to show only one button -->
                        $("#mapPopupBookInfo").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);

                        // if (feature.get('campground_type') == 0) {
                        //    $("#mapPopupBook").show();
                        // } else {
                        //    $("#mapPopupBook").hide();
                        // }

                    }, 1000);
                } */


                return;
            }

            // no match, forward on to mapbox geocode query
            var center = ol.proj.toLonLat(vm.center);
            $.ajax({
                url: 'https://mapbox.dpaw.wa.gov.au/geocoding/v5/mapbox.places/'+encodeURIComponent(place)+'.json?'+ $.param({
                    country: 'au',
                    proximity: ''+center[0]+','+center[1],
                    bbox: '112.920934,-35.191991,129.0019283,-11.9662455',
                    types: 'region,postcode,place,locality,neighborhood,address'
                }),
                dataType: 'json',
                success: function(data, status, xhr) {
                    if (data.features && data.features.length > 0) {
                        //console.log('Mapbox!');
                        //console.log(data.features[0]);
                        var view = vm.olmap.getView();
                        view.animate({
                            center: ol.proj.fromLonLat(data.features[0].geometry.coordinates),
                            resolution: vm.resolutions[12],
                            duration: 1000
                        });

                    }
                }
            })

        },
        refreshPopup: function(){
            let vm = this;
            let feature = vm.selectedFeature;
            if (feature != null){
                vm.popup.setPosition(feature.getGeometry().getCoordinates());
                // really want to make vue.js render this, except reactivity dies
                // when you pass control of the popup element to OpenLayers :(
                $("#mapPopupName")[0].innerHTML = feature.get('name');
                if (feature.get('images')) {
                    // console.log('feature.get('images')[0].image ' + feature.get('images')[0].image);
                   $("#mapPopupImage").attr('src', feature.get('images')[0].image);
                    $("#mapPopupImage").show();
                } else {
                    $("#mapPopupImage").hide();
                }
                if (feature.get('price_hint') && Number(feature.get('price_hint'))) {
                    $("#mapPopupPrice")[0].innerHTML = '<small>From $' + feature.get('price_hint') + ' per night</small>';
                } else {
                    $("#mapPopupPrice")[0].innerHTML = '';
                }
                $("#mapPopupDescription")[0].innerHTML = feature.get('description');

                //Need to change this portion for the new button

                //$("#mapPopupInfo").attr('href', feature.get('info_url'));

               // if/else used to diffrentiate campground type(if covers type 0 and 1) ,diffrentiated at api - backend
                if (feature.get('campground_type') == 0) {

                $("#mapPopupBook").show();
                $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);
                $("#mapPopupInfo").hide();
                } else if( feature.get('campground_type') == 1 ){

                $("#mapPopupBook").hide();
                $("#mapPopupInfo").show();
                $("#mapPopupInfo").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);

                } else {
                  $("#mapPopupInfo").attr('href', feature.get('info_url'));
                }

               /* if (feature.get('campground_type') == 0) {
                    $("#mapPopupBook").show();
                } else {
                    $("#mapPopupBook").hide();
                } */

            }
        },
        groundFilter: function(feature) {
            return true;
        },
        updateViewport: function(runNow) {
            var vm = this;
            var updateViewportFunc = function() {
                // this object is going to be hammered by vue.js introspection, strip openlayers stuff
                vm.extentFeatures = vm.groundsSource.getFeaturesInExtent(vm.extent).filter(vm.groundFilter).map(function (el) {
                    var props = el.getProperties();
                    props.style = undefined;
                    props.geometry = props.geometry.getCoordinates();
                    props.distance = Math.sqrt(Math.pow(props.geometry[0]-vm.center[0], 2) + Math.pow(props.geometry[1]-vm.center[1], 2));
                    props.id = el.getId();
                    return props;
                }).sort(function (a, b) {
                    /* distance from map center sort */
                    if (a.distance < b.distance) {
                        return -1;
                   }
                    if (a.distance > b.distance) {
                        return 1;
                    }
                    return 0;

                    /* alphabet sort
                    var nameA = a.name.toUpperCase();
                    var nameB = b.name.toUpperCase();
                    if (nameA < nameB) {
                        return -1;
                    }
                    if (nameA > nameB) {
                        return 1;
                    }
                    return 0; */
                });

            };
            if (runNow) {
                updateViewportFunc();
            } else {
                if (!vm._updateViewport) {
                    vm._updateViewport = debounce(function() {
                        updateViewportFunc();
                    }, 100);
                }
                vm._updateViewport();
            }
        },
        updateDates: function(ev) {
           // console.log('BANG');
           // console.log(ev);
            // for the first time someone changes the dates, enable the
            // "Show bookable campsites only" flag
            if (this.dateSetFirstTime) {
                this.dateSetFirstTime = false;
                this.bookableOnly = true;
            }
            this.reload();
        },
        reload: debounce(function () {
            this.groundsSource.loadSource();
            this.refreshPopup();
        }, 250),

        // TODO Added these methods to use server date extracted from an api call
        // Needs to be implemented in the system, have to use server date to restrict arrival date instead of today
        // Currently this function is not used
        setData: function(datestring) {
          let vm = this
             var tempDate = datestring.body;
              vm.currentDate = vm.currentDate = moment({year: tempDate.getFullYear(), month: tempDate.getMonth(), day: tempDate.getDate(), hour: 0, minute: 0, second: 0});
             // console.log('In setdata ,Function Date currentDate:'+vm.currentDate);

        },

        fetchServerDate: function() {
          let vm = this;

          vm.$http.get(vm.parkstayUrl+'/api/server-date').then(function(response)  {
            this.setData(response.body)
          })
        },

        // End of change

        updateFilter: function() {
            var vm = this;
            // make a lookup table of campground features to filter on
            var legit = new Set();
            var filterCb = function (el) {
                if (vm.filterParams[el.key] === true) {
                    el.remoteKey.forEach(function (fl) {
                        legit.add(fl);
                    });
                }
            };
            this.filterList.forEach(filterCb);
            this.extraFilterList.forEach(filterCb);

            this.groundsFilter.clear();
            this.groundsData.forEach(function (el) {
                // first pass filter against the list of IDs returned by search

                var campgroundType = el.get('campground_type');
                switch (campgroundType) {
                    case 0:
                    if (!vm.sitesOnline) {
                        return;
                    }
                    break;
                    case 1:
                    if (!vm.sitesInPerson) {
                        return;
                    }
                    break;
                    case 2:
                    if (!vm.sitesAlt) {
                        return;
                    }
                    break;
                    default:
                    break;
                }

                if (vm.groundsIds.has(el.getId())) {
                    if (legit.size) { // if we have a feature filter list
                        // check that all parameters are present
                        var feats = new Set(el.get('features').map(function(x) {
                            return x.name;
                        }));
                        for (var x of legit) {
                            if (!feats.has(x)) {
                                return;     // missing a feature!
                            }
                        }
                        vm.groundsFilter.push(el);

                    } else {  // no features, return all results
                        vm.groundsFilter.push(el);
                    }
                }
            });
            this.updateViewport(true);
        },

    },
    mounted: function () {
        var vm = this;
        $(document).foundation();
        console.log('Loading map...');

        var nowTemp = new Date();
        var now = moment.utc({year: nowTemp.getFullYear(), month: nowTemp.getMonth(), day: nowTemp.getDate(), hour: 0, minute: 0, second: 0}).toDate();

        // Added this portion from availability to solve datepicker utc - issue

        var today = moment.utc().add(8, 'hours');
        today = moment.utc({year: today.year(), month: today.month(), day: today.date()})

        //End of change

        this.arrivalEl = $('#dateArrival');
        this.departureEl = $('#dateDeparture');
        this.arrivalData = this.arrivalEl.fdatepicker({
            format: 'dd/mm/yyyy',
            //value: vm.currentDate which you got from server
            startDate: moment(today).toDate(),
            endDate: moment.utc(this.arrivalEl).add(180, 'days').toDate(),
            onRender: function (date) {
                // disallow start dates before today

                return date.valueOf() < today.valueOf() ? 'disabled': '';

                //return '';
            }
        }).on('changeDate', function (ev) {
           // console.log('arrivalEl changeDate');
            ev.target.dispatchEvent(new CustomEvent('change'));
        }).on('change', function (ev) {

            if (vm.arrivalData.date.valueOf() >= vm.departureData.date.valueOf()) {
                var newDate = moment(vm.arrivalData.date).add(1, 'days').toDate();
                vm.departureData.date = newDate;
                vm.departureData.setValue();
                vm.departureData.fill();
                vm.departureEl.trigger('changeDate');

            }

            vm.arrivalDate = moment(vm.arrivalData.date);

        }).on('keydown', function (ev) {
            if (ev.keyCode == 13) {
                ev.target.dispatchEvent(new CustomEvent('change'));
            }
        }).data('datepicker');

        this.departureData = this.departureEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                return (date.valueOf() <= vm.arrivalData.date.valueOf()) ? 'disabled': '';
            }
        }).on('changeDate', function (ev) {
            //console.log('departureEl changeDate');
            ev.target.dispatchEvent(new CustomEvent('change'));
        }).on('change', function (ev) {
            vm.departureData.hide();
            vm.departureDate = moment(vm.departureData.date);

        }).on('keydown', function (ev) {
            if (ev.keyCode == 13) {
                ev.target.dispatchEvent(new CustomEvent('change'));
            }
        }).data('datepicker');

        // load autosuggest choices
        var search = document.getElementById('searchInput');
        var autocomplete = new Awesomplete(search);
        autocomplete.autoFirst = true;

        $.ajax({
            url: vm.parkstayUrl+'/api/search_suggest',
            dataType: 'json',
            success: function (response, stat, xhr) {
                vm.suggestions = response;
                $(search).on('awesomplete-selectcomplete', function(ev) {
                    //console.log('autoselect');
                    //console.log(ev);
                    this.blur();
                    //vm.search(ev.target.value);
                });

                autocomplete.list = response['features'].map(function (el) {
                    return el['properties']['name'];
                });
            }
        });

        // wire up search box
        $(search).on('blur', function(ev) {
            //console.log('blur');
            //console.log(ev);
            vm.search(ev.target.value);
        }).on('keypress', function(ev) {
            if (!ev) {
                ev = window.event;
            }
            // intercept enter keys
            var keyCode = ev.keyCode || ev.which;
            if (keyCode == '13') {
                //console.log('enter');
                this.blur();
                return false;
            }
        });


        // generate WMTS tile grid
        this.projection = ol.proj.get('EPSG:3857');
        this.projectionExtent = this.projection.getExtent();
        var size = ol.extent.getWidth(this.projectionExtent) / 256;
        this.matrixSet = 'mercator';
        this.resolutions = new Array(21);
        this.matrixIds = new Array(21);
        for (var z = 0; z < 21; ++z) {
            // generate resolutions and matrixIds arrays for this WMTS
            this.resolutions[z] = size / Math.pow(2, z);
            this.matrixIds[z] = this.matrixSet + ':' + z;
        }
        var tileGrid = new ol.tilegrid.WMTS({
            origin: ol.extent.getTopLeft(this.projectionExtent),
            resolutions: this.resolutions,
            matrixIds: this.matrixIds
        });

        this.streets = new ol.layer.Tile({
            source: new ol.source.WMTS({
                url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
                format: 'image/png',
                layer: 'public:mapbox-streets',
                matrixSet: this.matrixSet,
                projection: this.projection,
                tileGrid: tileGrid
            })
        });

        this.tenure = new ol.layer.Tile({
            opacity: 0.6,
            source: new ol.source.WMTS({
                url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
                format: 'image/png',
                layer: 'public:dbca_legislated_lands_and_waters',
                matrixSet: this.matrixSet,
                projection: this.projection,
                tileGrid: tileGrid
            })
        });

        this.geojson = new ol.format.GeoJSON({
            featureProjection: 'EPSG:3857'
        });

        this.groundsData = new ol.Collection();
        this.groundsIds = new Set();
        this.groundsFilter = new ol.Collection();
        $.ajax({
            url: vm.parkstayUrl+'/api/campground_map/?format=json',
            dataType: 'json',
            success: function (response, stat, xhr) {
                var features = vm.geojson.readFeatures(response);
                vm.groundsData.clear();
                vm.groundsData.extend(features);
                vm.groundsSource.loadSource();
            }
        });

        this.groundsSource = new ol.source.Vector({
            features: vm.groundsFilter
        });

        this.groundsSource.loadSource = function (onSuccess) {
            var urlBase = vm.parkstayUrl+'/api/campground_map_filter/?';
            var params = {format: 'json'};
            var isCustom = false;
            if ((vm.arrivalData.date) && (vm.departureData.date)) {
                isCustom = true;
                var arrival = vm.arrivalDateString;

                if (arrival) {
                    params.arrival = arrival;
                }
                var departure = vm.departureDateString;
                if (departure) {
                    params.departure = vm.departureDateString;
                }
                params.num_adult = vm.numAdults;
                params.num_concessions = vm.numConcessions;
                params.num_children = vm.numChildren;
                params.num_infants = vm.numInfants;
                params.gear_type = vm.gearType;
            }
            $.ajax({
                url: urlBase+$.param(params),
                success: function (response, stat, xhr) {
                    vm.groundsIds.clear();
                    response.forEach(function(el) {
                        vm.groundsIds.add(el.id);
                    });
                    vm.updateFilter();
                },
                dataType: 'json'
            });
        };


        this.grounds = new ol.layer.Vector({
            source: this.groundsSource,
            style: function (feature) {
                var style = feature.get('style');
                if (!style) {
                    var icon = vm.sitesInPersonIcon;
                    var campgroundType = feature.get('campground_type');
                    switch (campgroundType) {
                        case 0:
                        icon = vm.sitesOnlineIcon;
                        break;
                        case 2:
                        icon = vm.sitesAltIcon;
                        break;
                        default:
                        break;
                    }
                    style = new ol.style.Style({
                        image: new ol.style.Icon({
                            src: icon,
                            imgSize: [32, 32],
                            snapToPixel: true,
                            anchor: [0.5, 1.0],
                            anchorXUnits: 'fraction',
                            anchorYUnits: 'fraction'
                        }),
                        zIndex: -feature.getGeometry().getCoordinates()[1]
                    });
                    feature.set('style', style);
                }
                //console.log(style);
                return style;
            }
        });

        $('#mapPopupClose').on('click', function(ev) {
            vm.popup.setPosition(undefined);
            vm.selectedFeature = null;
            return false;
        });
        this.popupContent = document.getElementById('mapPopupContent');
        this.popup = new ol.Overlay({
            element: document.getElementById('mapPopup'),
            autoPan: true,
            autoPanAnimation: {
                duration: 250
            }
        });


        this.posFeature = new ol.Feature();
        this.posFeature.setStyle(new ol.style.Style({
            image: new ol.style.Icon({
                src: vm.locationIcon,
                snapToPixel: true,
                anchor: [0.5, 0.5],
                anchorXUnits: 'fraction',
                anchorYUnits: 'fraction'
            })
        }));

        this.posLayer = new ol.layer.Vector({
            source: new ol.source.Vector({
                features: [this.posFeature]
            })
        });

        // create OpenLayers map object, prefill with all the stuff we made
        this.olmap = new ol.Map({
            logo: false,
            renderer: 'canvas',
            target: 'map',
            view: new ol.View({
                projection: 'EPSG:3857',
                center: vm.defaultCenter,
                zoom: 5,
                maxZoom: 21,
                minZoom: 5
            }),
            controls: [
                new ol.control.Zoom(),
                new ol.control.ScaleLine(),
            ],
            interactions: ol.interaction.defaults({
                altShiftDragRotate: false,
                pinchRotate: false,
            }),
            layers: [
                this.streets,
                this.tenure,
                this.grounds,
                this.posLayer
            ],
            overlays: [this.popup]
        });

        // spawn geolocation tracker
        this.geolocation = new ol.Geolocation({
            tracking: true,
            projection: this.olmap.getView().getProjection()
        });
        this.geolocation.on('change:position', function() {
            var coords = vm.geolocation.getPosition();
            vm.posFeature.setGeometry(coords ? new ol.geom.Point(coords) : null);
        });

        // sad loop to change the pointer when mousing over a vector layer
        this.olmap.on('pointermove', function(ev) {
            if (ev.dragging) {
                return;
            }
            var result = ev.map.forEachFeatureAtPixel(ev.pixel, function(feature, layer) {
                $('#map').attr('title', feature.get('name'));
                return true;
            }, {
                layerFilter: function (layer) {
                    return layer === vm.grounds;
                }
            }) === true;
            if (!result) {
                $('#map').removeAttr('title');
            }
            $('#map').toggleClass('click', result);
        });

        // another loop to spawn the popup on click
        this.olmap.on('singleclick', function(ev) {
            var result = ev.map.forEachFeatureAtPixel(ev.pixel, function(feature, layer) {
                vm.selectedFeature = feature;
                vm.popup.setPosition(feature.getGeometry().getCoordinates());
                // really want to make vue.js render this, except reactivity dies
                // when you pass control of the popup element to OpenLayers :(
                $("#mapPopupName")[0].innerHTML = feature.get('name');
                if (feature.get('images')) {
                    // console.log(feature.get('images')[0].image);
                    $("#mapPopupImage").attr('src', feature.get('images')[0].image);
                    $("#mapPopupImage").show();
                } else {
                    $("#mapPopupImage").hide();
                }
                if (feature.get('price_hint') && Number(feature.get('price_hint'))) {
                    $("#mapPopupPrice")[0].innerHTML = '<small>From $' + feature.get('price_hint') + ' per night</small>';
                } else {
                    $("#mapPopupPrice")[0].innerHTML = '';
                }
                $("#mapPopupDescription")[0].innerHTML = feature.get('description');

                // This portion needs to be modified to accomodate the new button
                // Online/Offline sites is determined by the backend api
               if (feature.get('campground_type') == 0) {

                $("#mapPopupBook").show()
                $("#mapPopupInfo").hide()
                $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);

                } else if (feature.get('campground_type') == 1 ) {

                $("#mapPopupBook").hide ()
                $("#mapPopupInfo").show()
                $("#mapPopupInfo").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);

                }
                // Now,this section is used for the partner accomadation
                else {
                $("#mapPopupInfo").show()
                $("#mapPopupBook").hide()
                $("#mapPopupInfo").attr('href', feature.get('info_url'));
                }

                /* $("#mapPopupInfo").attr('href', feature.get('info_url'));
                $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);
                if (feature.get('campground_type') == 0) {
                    $("#mapPopupBook").show();
                } else {
                    $("#mapPopupBook").hide();
                } */

                return true;
            }, {
                layerFilter: function (layer) {
                    return layer === vm.grounds;
                }
            });
            // if just single-clicking the map, hide the popup
            if (!result) {
                vm.popup.setPosition(undefined);
            }
        });

        // hook to update the visible feature list on viewport change
        this.olmap.getView().on('propertychange', function(ev) {
            vm.updateViewport();
        });

        this.reload();
    }
};
</script>
