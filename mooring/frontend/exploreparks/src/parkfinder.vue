<!DOCTYPE html>
<template>
    <div v-cloak class="f6inject">
        <div class="row">
            <div class="small-12 medium-3 large-6 columns search-params">
                <div class="row">
                    <div class="small-12 columns">
                        <label>Search <input class="input-group-field" id="searchInput" type="text" placeholder="Search for mooring's..."/></label>
                    </div>
                </div>
                <div class="row">
                    <div class="small-12 medium-12 large-3 columns">
                        <label>Arrival <input id="dateArrival" autocomplete="off" name="arrival" type="text" placeholder="dd/mm/yyyy" v-on:change="updateDates"/></label>
                    </div>
                    <div class="small-12 medium-12 large-3 columns">
                        <label>Departure <input id="dateDeparture" autocomplete="off" name="departure" type="text" placeholder="dd/mm/yyyy" v-on:change="updateDates"/></label>
                    </div>
                    <div class="small-12 medium-12 large-3 columns" style='display:none'>
                        <label>
                            Guests <input type="button" class="button formButton" v-bind:value="numPeople" data-toggle="guests-dropdown"/>
                        </label>
                        <div class="dropdown-pane" id="guests-dropdown" data-dropdown data-auto-focus="true">
                            <div class="row">
                                <div class="small-6 columns">
                                    <label for="num_adults" class="text-right">path:::Adults (non-concessions)<label>
                                </div>
                                <div class="small-6 columns">
                                    <input type="number" id="numAdults" name="num_adults" v-model="numAdults" min="0" max="16"/></label>
                                </div>
                            </div>
                            <div class="row">
                                <div class="small-6 columns">
                                    <label for="num_concessions" class="text-right"><span class="has-tip" title="Holders of one of the following Australian-issued cards:
					- Seniors Card
					- Age Pension
					- Disability Support
					- Carer Payment
					- Carer Allowance
				        - Companion Card
- Department of Veterans' Affairs">Concessions</span>
			  	   </label>
                                </div><div class="small-6 columns">
                                    <input type="number" id="numConcessions" name="num_concessions" v-model="numConcessions" min="0" max="16"/></label>
                                </div>
                            </div>
                            <div class="row">
                                <div class="small-6 columns">
                                    <label for="num_children" class="text-right">Children (ages 6-15)<label>
                                </div>
                                <div class="small-6 columns">
                                    <input type="number" id="numChildren" name="num_children" v-model="numChildren" min="0" max="16"/></label>
                                </div>
                            </div>
                            <div class="row">
                                <div class="small-6 columns">
                                    <label for="num_children" class="text-right">Moorings<label>
                                </div>
                                <div class="small-6 columns">
                                    <input type="number" id="numMooring" name="num_mooring" v-model="numMooring" min="0" max="16"/></label>
                                </div>
                            </div>

                       </div>
                       </div>
                     <div class="small-12 medium-12 large-3 columns">
                        <label>Vessel Size (meters) <input id="vesselSize" name="vessel_size" type="number"  placeholder="35" /></label>
                      </div>
                     <div class="small-12 medium-12 large-3 columns">
                        <label>Vessel Draft (meters) <input id="vesselDraft" name="vessel_draft" type="number" placeholder="35" /></label>
                      </div>

                    <div class="small-12 medium-12 large-12 columns">
                        <label><input type="checkbox" v-model="bookableOnly"/> Show bookable moorings only</label>
                    </div>
                </div>
                <div class="row"><div class="small-12 columns">
                    <hr/>
                </div>
                </div>
                <div class="row">
                    <div class="small-12 medium-12 large-12 columns">
                        <label>Mooring</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="gear_type" value="all" v-model="gearType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC3"></i> All types</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="gear_type" value="rental-available" v-model="gearType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC20"></i> Rental (available)</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="gear_type" value="rental-notavailable" v-model="gearType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC20"></i> Rental (not available)</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="gear_type" value="public-notbookable" v-model="gearType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC20"></i> Public (not bookable)</label>
                    </div>
                </div>
                <div class="row"><div class="small-12 columns">
                    <hr class="search"/>
                </div>
                </div>
                <div class="row" style='display:none'>
                    <div class="small-12 medium-12 large-12 columns">
                        <label>Select features</label>
                    </div>
                    <template v-for="filt in filterList">
                        <div class="small-12 medium-12 large-4 columns">
                            <label><input type="checkbox" class="show-for-sr" :value="'filt_'+ filt.key" v-model="filterParams[filt.key]" v-on:change="updateFilter()"/> <i class="symb" :class="filt.symb"></i> {{ filt.name }}</label>
                        </div>
                    </template>
<!--
                    <template v-for="filt in extraFilterList">
                        <div class="small-12 medium-12 large-4 columns" v-bind:class="{'filter-hide': hideExtraFilters}">
                            <label><input type="checkbox" class="show-for-sr" :value="'filt_'+ filt.key" v-model="filterParams[filt.key]" v-on:change="updateFilter()"/> <i class="symb" :class="filt.symb"></i> {{ filt.name }}</label>
                        </div>
                    </template>
-->
		</div>
<!--
                <div class="row">
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
-->
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
                        <p><small>Vessel Size: <span id='vessel_size_popup'></span></p>
                        <p style='display:none'><small>Max Stay Period: <span id='max_stay_period'></span> day/s</p>
                        <a id="mapPopupInfo" class="button formButton" style="margin-bottom: 0; margin-top: 1em;" target="_blank">More info</a>
                        <a id="mapPopupBook" class="button formButton" style="margin-bottom: 0;" target="_blank"  v-on:click="BookNow()" >Book now</a>
                    </div>
                </div>
            </div>
        </div>
        <template v-if="extentFeatures.length > 0">
            <paginate name="filterResults" class="resultList" :list="extentFeatures" :per="9">
                <div class="row">
                    <div class="small-12 medium-4 large-4 columns" v-for="f in paginated('filterResults')" v-if="f.vessel_size_limit >= vesselSize && f.vessel_draft_limit >= vesselDraft">
                        <div class="row">
                            <div class="small-12 columns">
                                <span class="searchTitle">{{ f.name }}</span>
                            </div>
                            <div class="small-12 medium-12 large-12 columns" >
                                <img class="thumbnail" src="/static/exploreparks/mooring_photo_scaled.png"/>
                            </div>
                            <div class="small-12 medium-9 large-9 columns">
                                <div v-html="f.description"/>
                                <p v-if="f.price_hint && Number(f.price_hint)"><i><small>From ${{ f.price_hint }} per night</small></i></p>
                                <p style='display:none'><i><small>Vessel Size Limit: {{ f.vessel_size_limit }} </small></i></p>
                                <p ><i><small>Max Stay Period: {{ f.max_advance_booking }} day/s </small></i></p>
                                <a class="button" v-bind:href="f.info_url" target="_blank">More info</a>
                                 
                                <a v-if="f.mooring_type == 0 && vesselSize > 0" class="button" v-bind:href="parkstayUrl+'/availability/?site_id='+f.id+'&'+bookingParam" target="_blank">Book now</a>
                                <a v-else class="button" v-on:click="BookNow()">Book now</a> 
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
                    <h2 class="text-center">There are no moorings found matching your search criteria. Please change your search query.</h2>
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
    src: url('/static/exploreparks/fonts/boating.woff') format("woff"); 
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

.symb.RC20:before {
    content: "v";
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

import Awesomplete from 'awesomplete';
import ol from 'openlayers';
//var ol = require('openlayers/dist/ol-debug');
import 'foundation-sites';
import 'foundation-datepicker/js/foundation-datepicker';
import debounce from 'debounce';
import moment from 'moment';
import swal from 'sweetalert2';
import 'sweetalert2/dist/sweetalert2.css';

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
//                {name: '2WD accessible', symb: 'RV2', key: 'twowheel', 'remoteKey': ['2WD/SUV ACCESS']},
//                {name: 'Campfires allowed', symb: 'RF10', key: 'campfire', 'remoteKey': ['FIREPIT']},
//                {name: 'Dogs allowed', symb: 'RG2', key: 'dogs', 'remoteKey': ['DOGS']}
            ],
            extraFilterList: [
                // {name: 'BBQ', symb: 'RF8G', key: 'bbq', 'remoteKey': ['BBQ']},
                // {name: 'Dish washing', symb: 'RF17', key: 'dishwashing', 'remoteKey': ['DISHWASHING']},
                // {name: 'Dump station', symb: 'RF19', key: 'sullage', 'remoteKey': ['DUMP STATION']},
                // {name: 'Generators allowed', symb: 'RG15', key: 'generators', 'remoteKey': ['GENERATORS PERMITTED']},
                // {name: 'Mains water', symb: 'RF13', key: 'water', 'remoteKey': ['MAINS WATER']},
                // {name: 'Picnic tables', symb: 'RF6', key: 'picnic', 'remoteKey': ['PICNIC TABLE']},
                // {name: 'Sheltered picnic tables', symb: 'RF7', key: 'picnicsheltered', 'remoteKey': ['TABLE - SHELTERED']},
                // {name: 'Showers', symb: 'RF15', key: 'showers', 'remoteKey': ['SHOWER']},
                // {name: 'Toilets', symb: 'RF1', key: 'toilets', 'remoteKey': ['TOILETS']},
                // {name: 'Walk trail', symb: 'RW3', key: 'walktrail', 'remoteKey': ['WALK TRAIL']},
                // {name: 'Powered sites', symb: 'MAINS', key: 'walktrail', 'remoteKey': ['POWERED SITES']},
                {name: 'Bookable Mooring', symb: 'MAINS', key: 'jettpenn', 'remoteKey': ['POWERED SITES']},
                {name: 'Non Bookable Mooring', symb: 'MAINS', key: 'mooring', 'remoteKey': ['POWERED SITES']},
            ],
            hideExtraFilters: true,
            suggestions: {},
            extentFeatures: [],
            arrivalDate: null,
            departureDate: null,
            dateCache: null,
            numAdults: 0,
            numConcessions: 0,
            numChildren: 0,
            numInfants: 0,
            numMooring: 1,
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
            boatingFont: require('./assets/fonts/boating.woff'),
            paginate: ['filterResults'],
            selectedFeature: null,
            current_map_scale: 1950001,
            anchorPins: null,
            anchorGroups: {},
            anchorPinsActive: [],
            vesselSize: 0,
            vesselDraft: 0,
            groupPinLevelChange: true,
            anchorPinLevelChange: true,
            mooring_map_data: null,
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
                // this.reload();
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
                var count = this.numAdults + this.numConcessions + this.numChildren + this.numInfants + this.numMooring;
                if (count === 1) {
                    return count +" person ▼";
                } else {
                    return count + " people ▼";
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
                    'num_mooring' : this.numMooring,
                    'gear_type': this.gearType,
                    'vessel_size' : this.vesselSize,
                    'vessel_draft' : this.vesselDraft,
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
                var view = this.olmap.getView();
                // zoom slightly closer in for campgrounds
                var resolution = vm.resolutions[10];
                if (target['properties']['type'] == 'MooringArea') {
                    resolution = vm.resolutions[14];
                }
                if ('zoom_level' in target['properties']) {
                        var zoom_level = target['properties']['zoom_level'];
			if (zoom_level > 0) {
			     resolution = vm.resolutions[target['properties']['zoom_level']];
			}
		}

                // pan to the spot, zoom slightly closer in for campgrounds
                view.animate({
                    center: ol.proj.fromLonLat(target['coordinates']),
                    resolution: resolution,
                    duration: 1000
                });

                // Open the popup
                /*let feature = this.groundsData.a.find(f => parseInt(f.a) == parseInt(target.properties.id));
                if (feature) {
                    setTimeout(() => {
                        vm.popup.setPosition(feature.getGeometry().getCoordinates());
                        // really want to make vue.js render this, except reactivity dies
                        // when you pass control of the popup element to OpenLayers :(
                        $("#mapPopupName")[0].innerHTML = feature.get('name');
                        if (feature.get('images')) {
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
                        $("#mapPopupInfo").attr('href', feature.get('info_url'));
                        $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);
                        if (feature.get('campground_type') == 0) {
                            $("#mapPopupBook").show();
                        } else {
                            $("#mapPopupBook").hide();
                        }
                    },1000);
                }*/

                return;
            }

            console.log('Load search');
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
        refreshPopup: function() {
            let vm = this;
            let feature = vm.selectedFeature;
            if (feature != null) {
                vm.popup.setPosition(feature.getGeometry().getCoordinates());
                // really want to make vue.js render this, except reactivity dies
                // when you pass control of the popup element to OpenLayers :(
                $("#mapPopupName")[0].innerHTML = feature.get('name');
                if (feature.get('images')) {
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
                $("#mapPopupInfo").attr('href', feature.get('info_url'));
                $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);
                if (feature.get('campground_type') == 0) {
                    $("#mapPopupBook").show();
                } else {
                    $("#mapPopupBook").hide();
                }
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
            // for the first time someone changes the dates, enable the
            // "Show bookable campsites only" flag
            if (this.dateSetFirstTime) {
                this.dateSetFirstTime = false;
                this.bookableOnly = true;
            }
            // this.reload();
        },
        reload: debounce(function () {
              this.groundsSource.loadSource();
              this.removePinAnchors();
              this.anchorPinLevelChange = true;

              this.buildmarkers();
         //   this.refreshPopup();
        }, 250),
        removePinGroups: function() {
                
               var layerRemoved = false;
               var map = this.olmap;
               var refArray = map.getLayers().getArray().slice();
               refArray.forEach(function(layer2) {
                       if (layer2 != null) {
                       var layer = layer2.I;
                       if (layer != null) {
                           // map.removeLayer(layer2);
                           if (layer.hasOwnProperty("markerGroup")) {
                                if (layer.markerGroup == 'circle') {
                                      map.removeLayer(layer2);
                                      layerRemoved = true;
                                }
                          }
                       }
                      }
                }); 
                if (layerRemoved == true) {
                    // We do this because when we call map.removeLayer it causes the layer 
                    // to go out of sync resulting in pins not being removed as foreach loop is 
                    // changed.  This loop ensure all pins have been removed

	            this.removePinGroups();
		}
                return layerRemoved; 
	},
        removePinAnchors: function() {
               var layerRemoved = false;
               var map = this.olmap;
               var refArray = map.getLayers().getArray().slice();
               refArray.forEach(function(layer2) {
                       if (layer2 != null) {
                       var layer = layer2.I;
                       if (layer != null) {
                           // map.removeLayer(layer2);
                           if (layer.hasOwnProperty("markerGroup")) {
                                if (layer.markerGroup == 'anchor') {
                                      map.removeLayer(layer2);
                                      layerRemoved = true;
                                }
                          }
                       }
                      }
               });
               if (layerRemoved == true) {
                    // We do this because when we call map.removeLayer it causes the layer
                    // to go out of sync resulting in pins not being removed as foreach loop is
                    // changed.  This loop ensure all pins have been removed

                   this.removePinAnchors();
               }
               return layerRemoved;
        },
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
                var campgroundType = el.get('mooring_type');
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
        buildmarkers: function() {
          var vm = this;
          var scale = Math.floor(this.current_map_scale);
          var map = this.olmap;
          var mooring_type =  $("input:radio[name=gear_type]:checked").val(); 

        if (scale >= 0 && scale <= 1300000) {
            
            if (vm.groupPinLevelChange == true) { 
                this.removePinGroups(); 
            } 
            vm.groupPinLevelChange = false;
            vm.anchorPinLevelChange = true;

            if (vm.anchorPins == null) {  
                 var response = this.mooring_map_data;
                 vm.anchorPins = response; 
	     }
//             this.groundsSource.loadSource();
             map.updateSize();
           
             var response = vm.anchorPins; 
             var pin_count = 0;
             for (var x in response) {
                        var mooring = response[x];
                        for (var m in mooring) {
                             for (var b in response[x][m]) {
				   if (b == 'geometry') {
                                      var vessel_size = $("#vesselSize").val();
                                      var vessel_draft = $("#vesselDraft").val();
                                      var show_marker = true;
                                      if (response[x][m]['properties']['vessel_size_limit'].length == 0) { 
						response[x][m]['properties']['vessel_size_limit'] = 0;
				      }
                                     
                                      if (parseInt(vessel_size) > 0 || parseInt(vessel_draft) > 0) {
                                          show_marker = false;
                                          if (parseInt(response[x][m]['properties']['vessel_size_limit']) >= parseInt(vessel_size) && parseInt(response[x][m]['properties']['vessel_draft_limit']) >= parseInt(vessel_draft)) {
                                               show_marker = true;
                                          }
                                      }

                                      if (show_marker == true) {
                                                var array_search = vm.anchorPinsActive.indexOf(response[x][m]['id']);
  				                if (array_search > 0) {
				                } else {
                                                      var marker_id = response[x][m]['id'];
		                                      pin_count =  pin_count + 1;
                		                      if (response[x][m]['properties']['mooring_type'] == 0) {

                                                           if (mooring_type == 'all' || mooring_type == 'rental-available' || mooring_type == 'rental-notavailable') {
                                                                if (mooring_type == 'rental-available' || mooring_type == 'rental-notavailable') { 
                                                                      
                                                                      if (this.groundsIds.has(marker_id)) { 
                                                                           
                                                                           if (mooring_type == 'rental-available') {
                                                                              if (response[x][m]['geometry'] != null ) {
                                                                                     if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
                                		           map.addLayer(vm.buildMarkerBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                                                     }
                                                                               }
                                                                           }
                                                 
                                                                      } else {
                                                                            if (mooring_type == 'rental-notavailable') {
                                                                                 if (this.groundsIds.has(marker_id)) {
                                                                                 } else {
                                                                                        if (response[x][m]['geometry'] != null ) {
                                                                                            if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
											map.addLayer(vm.buildMarkerBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                                                            }
                                                                                         }
										 }

                                                                            }
								      }
                                                                
                                                                } else {
                                                                      if (response[x][m]['geometry'] != null ) {
                                                                          if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
                                                                      map.addLayer(vm.buildMarkerBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                                           }
                                                                      }
							        }
		                                           vm.updateFilter();
                                                           }
						      }
 
                                		      if (response[x][m]['properties']['mooring_type'] == 1) {
                                                           if (mooring_type == 'all') {
                                                              if (response[x][m]['geometry'] != null ) {
                                                                  if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
							   map.addLayer(vm.buildMarkerNotBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                                  }
                                                              }
                        		                   vm.updateFilter();
							   }
						      }

                                                      if (response[x][m]['properties']['mooring_type'] == 2) {
                                                           if (mooring_type == 'all' || mooring_type == 'public-notbookable') {
                                                            if (response[x][m]['geometry'] != null ) {
                                                               if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
                                                           map.addLayer(vm.buildMarkerNotBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                           vm.updateFilter();
                                                               }
                                                            }
                                                           }
                                                      }

						}
                                      }
                                      
                                   }
		   	      }
			}
             }
      } else if (scale >= 1300001) {
	      var center = map.getView().getCenter();
              if (center) {
	                var latLon = ol.proj.transform([center[0],center[1]], 'EPSG:3857', 'EPSG:4326');
	      }
              if (vm.anchorPinLevelChange == true) { 
                   this.removePinAnchors();
	      }
              vm.groupPinLevelChange = true;
              vm.anchorPinLevelChange = false;

       var response = this.mooring_map_data;
       vm.anchorGroups = {};
       var vessel_size = $('#vesselSize').val();
       var vessel_draft = $('#vesselDraft').val();

            var mooring = response['features'];
            for (var m in mooring) {
                 var mooring_vessel_size = response['features'][m]['properties']['vessel_size_limit'];
                 var mooring_vessel_draft = response['features'][m]['properties']['vessel_draft_limit'];
                 if (mooring_vessel_size >= vessel_size && mooring_vessel_draft >= vessel_draft) { 
                 if (vm.anchorGroups[response['features'][m]['properties']['park']['district']['region']['id']] == null) { 
                      vm.anchorGroups[response['features'][m]['properties']['park']['district']['region']['id']] = {};
                      vm.anchorGroups[response['features'][m]['properties']['park']['district']['region']['id']]['total'] = 1;
                      vm.anchorGroups[response['features'][m]['properties']['park']['district']['region']['id']]['name'] = response['features'][m]['properties']['park']['district']['region']['name'];
                      vm.anchorGroups[response['features'][m]['properties']['park']['district']['region']['id']]['zoom_level'] = response['features'][m]['properties']['park']['district']['region']['zoom_level'];
                      vm.anchorGroups[response['features'][m]['properties']['park']['district']['region']['id']]['geometry'] = response['features'][m]['properties']['park']['district']['region']['wkb_geometry']['coordinates'];
   		 } else {
			vm.anchorGroups[response['features'][m]['properties']['park']['district']['region']['id']]['total'] = vm.anchorGroups[response['features'][m]['properties']['park']['district']['region']['id']]['total'] + 1;
		 }
                 }
            }

         for (var g in vm.anchorGroups) { 
                var longitude = vm.anchorGroups[g]['geometry'][0];
                var latitude = vm.anchorGroups[g]['geometry'][1];

                var total = vm.anchorGroups[g]['total'];
                var name = vm.anchorGroups[g]['name'];
                var zoom_level = vm.anchorGroups[g]['zoom_level'];
                map.addLayer(vm.buildMarkerGroup(parseFloat(longitude),parseFloat(latitude),total,name, zoom_level));
	 }

     } else {
        scale = Math.round(scale);
     }
//        document.getElementById('scale').innerHTML = "Scale = 1 : " + scale;
     },
     buildMarkerBookable: function(lat,lon,props,name,marker_id) {
            var mooring_type =  $("input:radio[name=gear_type]:checked").val();

            var pin_type=require('assets/map_pins/pin_red.png'); 
            var bookable = false;
            if (this.groundsIds.has(marker_id)) {
                 pin_type=require('assets/map_pins/pin_orange.png');
                 var bookable = true;
	    }

                //this.anchorPinsActive.push(marker_id);
            var iconFeature = new ol.Feature({
                  marker_group: 'mooring_marker',
                  geometry: new ol.geom.Point(ol.proj.transform([lat, lon], 'EPSG:4326', 'EPSG:3857')),
                  name: name,
//                  population: 4000,
//                  rainfall: 500,
                  bookable: bookable,
                  marker_id: marker_id,
                  props: props

            });

            var iconStyle = new ol.style.Style({
                  image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                  imgSize: [32, 32],
                  snapToPixel: true,
                  anchor: [0.5, 1.0],
                  anchorXUnits: 'fraction',
                  anchorYUnits: 'fraction',
                  opacity: 0.95,
                  src: pin_type 
                 })),
            });

            iconFeature.setStyle(iconStyle);

            var vectorSource = new ol.source.Vector({
                features: [iconFeature]
            });

            var vectorLayer = new ol.layer.Vector({
               canDelete: "yes",
               markerGroup: "anchor",
               source: vectorSource
            });

            return vectorLayer;
    },
    buildMarkerNotBookable: function(lat,lon,props,name,marker_id) {

		var iconFeature = new ol.Feature({
                  marker_group: 'mooring_marker',
		  geometry: new ol.geom.Point(ol.proj.transform([lat, lon], 'EPSG:4326', 'EPSG:3857')),
		  name: name,
		  population: 4000,
		  rainfall: 500,
                  marker_id: marker_id,
                  props: props
		});

		var iconStyle = new ol.style.Style({
		  image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                    imgSize: [32, 32],
                    snapToPixel: true,
                    anchor: [0.5, 1.0],
			//    anchor: [115.864627, -32.007385],
		    anchorXUnits: 'fraction',
                    anchorYUnits: 'fraction',
		    opacity: 0.95,
		    src: require('assets/map_pins/pin_gray.png')

	         }))
	    });

	    iconFeature.setStyle(iconStyle);
	
	    var vectorSource = new ol.source.Vector({
	        features: [iconFeature]
	    });

	    var vectorLayer = new ol.layer.Vector({
	       canDelete: "yes",
               markerGroup: "anchor",
	       source: vectorSource
	    });

	    return vectorLayer;
    },
    buildMarkerGroup:function(lat,lon,text, name, zoom_level) {

              var iconFeature = new ol.Feature({
                  marker_group: 'group_marker',
                  geometry: new ol.geom.Point(ol.proj.transform([lat, lon], 'EPSG:4326', 'EPSG:3857')),
                  name: name,
                  zoom_level: zoom_level
              });

              var icon = require('assets/map_pins/geo_group_red.png');
              if (text > 30) {
                       icon = require('assets/map_pins/geo_group2.png');
              } else if (text > 10) {
                       icon = require('assets/map_pins/geo_group_orange.png');
              } else {
                       icon = require('assets/map_pins/geo_group_red.png');
              }

              var iconStyle = new ol.style.Style({
                        image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                          anchor: [0.5, 24],
                          anchorXUnits: 'fraction',
                          anchorYUnits: 'pixels',
                          opacity: 15,
                          src: icon
                        })),

                        text: new ol.style.Text({
                          text: text.toString(),
                          scale: 1.2,
                          fill: new ol.style.Fill({
                            color: '#000000'
                          }),
                        //          stroke: new ol.style.Stroke({
                        //            color: '#FFFF99',
                        //            width: 3.5
                        //          })
                        })
              });

              iconFeature.setStyle(iconStyle);

              var vectorSource = new ol.source.Vector({
                  features: [iconFeature]
              });

              var vectorLayer = new ol.layer.Vector({
                   canDelete: "yes",
                   markerGroup: "circle",
                   source: vectorSource
              });
              return vectorLayer;
      },
      BookNow: function() { 
       var vessel_size = $('#vesselSize').val();
       var veseel_draft = $('#vesselDraft').val();

       if (vessel_size > 0 && veseel_draft > 0) {
       } else {
                swal({
                  title: 'Missing Vessel Draft or Size',
                  text: "Please enter vessel draft or size:",
                  type: 'warning',
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  showLoaderOnConfirm: true,
                  allowOutsideClick: false
                })
       }
      },
      loadMap: function() {

        var vm = this;

        console.log('Loading map...');
        var nowTemp = new Date();
        var now = moment.utc({year: nowTemp.getFullYear(), month: nowTemp.getMonth(), day: nowTemp.getDate(), hour: 0, minute: 0, second: 0}).toDate();

        this.arrivalEl = $('#dateArrival');
        this.departureEl = $('#dateDeparture');

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
                    this.blur();
                });

                autocomplete.list = response['features'].map(function (el) {
                    return el['properties']['name'];
                });
            }
        });

        // wire up search box
        $(search).on('blur', function(ev) {
            vm.search(ev.target.value);
        }).on('keypress', function(ev) {
            if (!ev) {
                ev = window.event;
            }
            // intercept enter keys
            var keyCode = ev.keyCode || ev.which;
            if (keyCode == '13') {
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
            canDelete: "no",
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
            canDelete: "no",
            opacity: 0.6,
            source: new ol.source.WMTS({
                url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
                format: 'image/png',
                layer: 'public:dpaw_lands_and_waters',
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
            url: vm.parkstayUrl+'/api/mooring_map/?format=json',
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

            if (vm.dateCache != vm.arrivalDateString+vm.departureDateString) {
            var urlBase = vm.parkstayUrl+'/api/mooring_map_filter/?';
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
                params.num_mooring = vm.numMooring;
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
                    vm.dateCache = vm.arrivalDateString+vm.departureDateString;
                },
                dataType: 'json'
            });
            }
        };

        this.grounds = new ol.layer.Vector({
            source: this.groundsSource,
            style: function (feature) {
                var style = feature.get('style');
                //if (!style) {
                //    var icon = vm.sitesInPersonIcon;
                //    var campgroundType = feature.get('mooring_type');
                //    switch (campgroundType) {
                //        case 0:
                //        icon = vm.sitesOnlineIcon;
                //       break;
                //        case 2:
                //        icon = vm.sitesAltIcon;
                //        break;
                //        default:
                //        break;
                //    }
                //    style = new ol.style.Style({
                //        image: new ol.style.Icon({
                //            src: icon,
                //            imgSize: [32, 32],
                //            snapToPixel: true,
                //            anchor: [0.5, 1.0],
                //            anchorXUnits: 'fraction',
                //            anchorYUnits: 'fraction'
                //        }),
                //       zIndex: -feature.getGeometry().getCoordinates()[1]
                //    });
                //   feature.set('style', style);
                //}
                //console.log(style);
                return style;
            }
        });

        // Marker Popup Code
        $('#mapPopupClose').on('click', function(ev) {
            $('#mapPopup').hide();
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

      }

    },
    mounted: function() {
        var vm = this;

        $(document).foundation();
        console.log('Loading map...');
        // enable arrival/departure date pickers
        var nowTemp = new Date();
        var now = moment.utc({year: nowTemp.getFullYear(), month: nowTemp.getMonth(), day: nowTemp.getDate(), hour: 0, minute: 0, second: 0}).toDate();

        this.arrivalEl = $('#dateArrival');
        this.departureEl = $('#dateDeparture');

        this.arrivalData = this.arrivalEl.fdatepicker({
            format: 'dd/mm/yyyy',
            onRender: function (date) {
                // disallow start dates before today
                return date.valueOf() < now.valueOf() ? 'disabled': '';
                //return '';
            }
        }).on('changeDate', function (ev) {
            //console.log('arrivalEl changeDate');
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
                    this.blur();
                });

                autocomplete.list = response['features'].map(function (el) {
                    return el['properties']['name'];
                });
            }
        });

        // wire up search box
        $(search).on('blur', function(ev) {
            vm.search(ev.target.value);
        }).on('keypress', function(ev) {
            if (!ev) {
                ev = window.event;
            }
            // intercept enter keys 
            var keyCode = ev.keyCode || ev.which;
            if (keyCode == '13') {
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
            canDelete: "no",
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
            canDelete: "no",
            opacity: 0.6,
            source: new ol.source.WMTS({
                url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
                format: 'image/png',
                layer: 'public:dpaw_lands_and_waters',
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
            url: vm.parkstayUrl+'/api/mooring_map/?format=json',
            dataType: 'json',
            success: function (response, stat, xhr) {
               vm.mooring_map_data = response;
               var features = vm.geojson.readFeatures(response);
               vm.groundsData.clear();
               vm.groundsData.extend(features);
               vm.groundsSource.loadSource();
               vm.buildmarkers();
 
            }
        });

        this.groundsSource = new ol.source.Vector({
            features: vm.groundsFilter   
        });

        this.groundsSource.loadSource = function (onSuccess) {
            if (vm.dateCache != vm.arrivalDateString+vm.departureDateString) {
                    vm.removePinAnchors();
                    vm.anchorPinLevelChange = true;

            var urlBase = vm.parkstayUrl+'/api/mooring_map_filter/?';
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
                params.num_mooring = vm.numMooring;
                params.gear_type = vm.gearType;
            }
            $.ajax({
                url: urlBase+$.param(params),
                success: function (response, stat, xhr) {
                    vm.groundsIds.clear();
                    response.forEach(function(el) {
                        vm.groundsIds.add(el.id);
                        vm.dateCache = vm.arrivalDateString+vm.departureDateString;
                    });
                    vm.updateFilter();
               //     vm.removePinAnchors();
               //     vm.anchorPinLevelChange = true;
                    vm.buildmarkers();

                },
                dataType: 'json'
            });
          }
       };
       this.grounds = new ol.layer.Vector({
           source: this.groundsSource,
            style: function (feature) {
             var style = feature.get('style');
             //   if (!style) {
             //       var icon = vm.sitesInPersonIcon;
             //       var campgroundType = feature.get('mooring_type');
             //       switch (campgroundType) {
             //          case 0:
             //           icon = vm.sitesOnlineIcon;
             //           break;
             //           case 2:
             //           icon = vm.sitesAltIcon;
             //           break;
             //           default:
             //          break;
             //      }
             //      style = new ol.style.Style({
             //           image: new ol.style.Icon({
             //               src: icon,
             //               imgSize: [32, 32],
             //               snapToPixel: true,
             //               anchor: [0.5, 1.0],
             //             anchorXUnits: 'fraction',
             //               anchorYUnits: 'fraction'
             //           }),
             //           zIndex: -feature.getGeometry().getCoordinates()[1]
             //      });
             //      feature.set('style', style);
             //   }
             //   //console.log(style);
                return style;
            }
        });

	// Marker Popup Code
        $('#mapPopupClose').on('click', function(ev) {
            $('#mapPopup').hide();
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
	// End of Marker Popup Code


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

        // JASON ADDED
        var map = this.olmap;

        this.olmap.getView().on('change:resolution', function(evt) {
               var resolution = evt.target.get('resolution');
               var units = map.getView().getProjection().getUnits();
               var dpi = 25.4 / 0.28;
               var mpu = ol.proj.METERS_PER_UNIT[units];
 
               var scale_res = resolution * mpu * 39.37 * dpi;
               vm.current_map_scale = scale_res;
               setTimeout(function() { if (scale_res == vm.current_map_scale) { vm.buildmarkers(); vm.updateViewport(); }}, 400);
        });

        $('#vesselSize').blur(function() { 
               // vm.olmap.zoomOut();
               // vm.olmap.zoomIn();
               vm.vesselSize = this.value;
               vm.removePinAnchors();
               vm.removePinGroups();
	       vm.buildmarkers();
	});

        $('#vesselDraft').blur(function() {
               // vm.olmap.zoomOut();
               // vm.olmap.zoomIn();
               vm.vesselDraft = this.value;
               vm.removePinAnchors();
               vm.removePinGroups();
               vm.buildmarkers();
        });

        $('#dateArrival').change(function() {
               vm.groundsSource.loadSource();
               //vm.removePinAnchors();
               //vm.anchorPinLevelChange = true;
               //vm.buildmarkers();
        });

        $('#dateDeparture').change(function() {
               vm.groundsSource.loadSource();
               //vm.removePinAnchors();
               //vm.anchorPinLevelChange = true;
               //vm.buildmarkers();
        });

        //$("input[type=radio][name=gear_type]").click(function() {
         //      vm.removePinAnchors();
         //      vm.anchorPinLevelChange = true;
         //      vm.buildmarkers();
        //});

        $('#vesselSize').val('0');
        $('#vesselDraft').val('0');
 
 
        // loop to change the pointer when mousing over a vector layer
        this.olmap.on('pointermove', function(ev) {
            if (ev.dragging) {
                return;
            }
            var result = map.forEachFeatureAtPixel(ev.pixel, function(feature, layer) {
               $('#map').attr('title', feature.get('name'));
               return feature;
            });
            if (result) {
                    // console.log($('#map').hasClass('click'));
                    if ($('#map').hasClass('click')) { 
                    } else {
			$('#map').addClass('click', result);
		    }
	    } else {
                   $('#map').removeClass('click', result);
            }
            if (!result) {
                $('#map').removeAttr('title');
            }
         
 
        });


       var element = document.getElementById('mapPopup');

       var popup = new ol.Overlay({
          element: element,
          positioning: 'bottom-center',
          stopEvent: false
       });

       map.addOverlay(popup);

       // another loop to spawn the popup on click
       this.olmap.on('singleclick', function(ev) {
          var feature = ev.map.forEachFeatureAtPixel(ev.pixel, 
             function(feature, layer) {
                return feature;
             });

          if (feature) {
            var geometry = feature.getGeometry();
            var coord = geometry.getCoordinates();
            var properties = feature.getProperties();
            if (properties.marker_group == 'mooring_marker') {

                $('#mapPopupName').html(properties.props.name);

                if (properties.props.mooring_type == 0) {
                   if (properties.bookable == true) { 
                      $('#mapPopupBook').show();
                   } else {
                      $('#mapPopupBook').hide();
		   }
                   $("#mapPopupImage").show();
                   if (properties.props.images.length > 0) { 
			$("#mapPopupImage").attr('src',  properties.props.images[0].image);
		   } else {
	                   $("#mapPopupImage").attr('src',  '/static/exploreparks/mooring_photo_scaled.png');
		   }
                   $("#vessel_size_popup").html(properties.props.vessel_size_limit);
		   //  $("#max_stay_period").html(properties.props.max_advance_booking);
                   var vessel_size = $('#vesselSize').val();
                   var vessel_draft = $('#vesselDraft').val();
                   if (vessel_size > 0 && vessel_draft > 0) {
                       $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability/?site_id='+properties.marker_id+'&'+vm.bookingParam);
                       $("#mapPopupBook").attr('target','_blank');
                   } else {
		       $("#mapPopupBook").attr('href','javascript:void(0);');
                       $("#mapPopupBook").attr('target','');
		   }
                } else {
		   $("#vessel_size_popup").html(properties.props.vessel_size_limit);
                   $('#mapPopupBook').hide();
                }

                popup.setPosition(coord);

                $(element).show();

                } else if (properties.marker_group == 'group_marker') {
                    var view = vm.olmap.getView();
                    var resolution = vm.resolutions[properties.zoom_level];
                    view.animate({
                          center: coord,
                          resolution: resolution,
                          duration: 1000
                    }); 
                     
                    if (properties.props.mooring_type == 0) {
                        $('#mapPopupBook').show();
                        $("#mapPopupImage").hide();
                        var vessel_size = $('#vesselSize').val();
                        var vessel_draft = $('#vesselDraft').val();

                        if (vessel_size > 0 && vessel_draft > 0) {
                               $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability/?site_id='+properties.marker_id+'&'+vm.bookingParam);
                        } else {
				 $("#mapPopupBook").attr('href','javascript:void;');
			}
                    } else {
                        $('#mapPopupBook').hide();
                    }
	        } 

          } else {
             $(element).hide();
 //            $(element).popover('destroy');
          }
     //      this.buildmarkers();

        });


//function(feature, layer) {
//                console.log('loading results');
//                vm.selectedFeature = feature;
//                vm.popup.setPosition(feature.getGeometry().getCoordinates());
//                // really want to make vue.js render this, except reactivity dies
//                // when you pass control of the popup element to OpenLayers :(
//                $("#mapPopupName")[0].innerHTML = feature.get('name');
//                if (feature.get('images')) {
//                   // console.log(feature.get('images')[0].image);
//                    $("#mapPopupImage").attr('src', feature.get('images')[0].image);
//                    $("#mapPopupImage").show();
//                } else {
//                    $("#mapPopupImage").hide();
//                }
//                if (feature.get('price_hint') && Number(feature.get('price_hint'))) {
//                    $("#mapPopupPrice")[0].innerHTML = '<small>From $' + feature.get('price_hint') + ' per night</small>';
//                } else {
//                    $("#mapPopupPrice")[0].innerHTML = '';
//                }
//                $("#mapPopupDescription")[0].innerHTML = feature.get('description');
//                $("#mapPopupInfo").attr('href', feature.get('info_url'));
//                $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability/?site_id='+feature.getId()+'&'+vm.bookingParam);
//                if (feature.get('campground_type') == 0) {
//                    $("#mapPopupBook").show();
//                } else {
//                    $("#mapPopupBook").hide();
//                }
//                return feature;
 //           }, {
//                layerFilter: function (layer) {
//                    console.log('did not make it');
//                    console.log(layer);
 //                   return layer === vm.grounds;
//                }
 //           });

//            // if just single-clicking the map, hide the popup
//            if (!result) {
//                vm.popup.setPosition(undefined);
//            }
//        });

        // hook to update the visible feature list on viewport change
        this.olmap.getView().on('propertychange', function(ev) {
            vm.updateViewport();
            vm.buildmarkers();
        });
	this.reload();
    }
};
</script>
