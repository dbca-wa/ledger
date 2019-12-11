<!DOCTYPE html>
<template>
    <div v-cloak class="f6inject">
       <div class="row">
        <div class="small-12 medium-3 large-6 columns search-params">
        <div class="columns small-12 medium-12 large-12" v-show="current_booking.length > 0">
             
        <div class="row">
                <div class="columns small-12 medium-12 large-12" >
                      <button  title="Please add items into your trolley." v-show="ongoing_booking" style="color: #FFFFFF; background-color: rgb(255, 0, 0);" class="button small-12 medium-12 large-12" >Time Left {{ timeleft }}</button>  <a  v-show="current_booking.length > 0" class="button small-12 medium-12 large-12" :href="parkstayUrl+'/booking'" style="border-radius: 4px; border: 1px solid #2e6da4">Proceed to Check Out</a> <a type="button" :href="parkstayUrl+'/booking/abort'" class="button float-right warning continueBooking" style="color: #fff; background-color: #f0ad4e;  border-color: #eea236; border-radius: 4px;">
                            Cancel in-progress booking
                        </a>
		</div>
                <div class="small-12 medium-12 large-12">
                        <div class="panel panel-default">
                             <div class="panel-heading"><h3 class="panel-title">Trolley: <span id='total_trolley'>${{ total_booking }}</span></h3></div>
                              <div class='columns small-12 medium-12 large-12'>
                                 <div v-for="item in current_booking" class="row small-12 medium-12 large-12">
                                         <div class="columns small-12 medium-9 large-9">{{ item.item }}</div>
                                         <div class="columns small-12 medium-2 large-2">${{ item.amount }}</div>
                                         <div class="columns small-12 medium-1 large-1"><a v-show="item.past_booking == false" style='color: red; opacity: 1;' type="button" class="close" @click="deleteBooking(item.id)">x</a></div>
                                 </div>
                              </div>
                        </div>
                </div>
        </div>
        </div>

                <div class="row">
                    <div class="small-12 columns">
                        <label>Search <input class="input-group-field" id="searchInput" type="text" placeholder="Search for a mooring..."/></label>
                    </div>
                </div>
                <div class="row">
                    <div class="small-12 medium-12 large-6 columns">
                        <label>Arrival <input id="dateArrival" autocomplete="off" name="arrival" type="text" placeholder="dd/mm/yyyy" v-on:change="updateDates"/></label>
                    </div>
                    <div class="small-12 medium-12 large-6 columns">
                        <label>Departure <input id="dateDeparture" autocomplete="off" name="departure" type="text" placeholder="dd/mm/yyyy" v-on:change="updateDates"/></label>
                    </div>
                    
                    <div class="small-12 medium-12 large-12 columns" style="display:none;">
                        <label><input type="checkbox" v-model="bookableOnly"/> Show bookable moorings only</label>
                    </div>
                </div>
                <div class="row"><div class="small-12 columns">
                    <hr/>
                </div>
                </div>
                <div class="row">
                    <div class="small-12 medium-12 large-6 columns">
                    <label>Vessel Registration  <input v-model="vesselRego" id="vesselRego" name="vessel_rego" type="text" placeholder="REGO134" style="text-transform:uppercase" :disabled="current_booking.length > 0" step='0.01' /></label>
                    </div>
                    <div class="small-12 medium-12 large-6 columns">
                    <label>Vessel Size (Meters) <input v-model="vesselSize" id="vesselSize" name="vessel_size" type="number" placeholder="35" :disabled="current_booking.length > 0" step='0.01' /></label>
                    </div>
                    <div class="small-12 medium-12 large-6 columns">
                    <label>Vessel Draft (Meters) <input v-model="vesselDraft" id="vesselDraft" name="vessel_draft" type="number" placeholder="10" :disabled="current_booking.length > 0" step='0.01' /></label>
                    </div>
                    <div class="small-12 medium-12 large-6 columns">
                    <label>Vessel Beams (Meters)  <input v-model="vesselBeam" id="vesselBeam" name="vessel_beams" type="number" placeholder="3" :disabled="current_booking.length > 0" step='0.01' /></label>
                    </div>
                    <div class="small-12 medium-12 large-6 columns">
                    <label>Vessel Weight (Tonnes)  <input v-model="vesselWeight" id="vesselWeight" name="vessel_weight" type="number" placeholder="2" :disabled="current_booking.length > 0" step='0.01' /></label>
                    </div>
                    <div class="small-12 medium-12 large-6 columns" >
                        <label>
                            Guests <input type="button" class="button formButton" v-bind:value="numPeople" data-toggle="guests-dropdown"/>
                        </label>
                        <div class="dropdown-pane" id="guests-dropdown" data-dropdown data-auto-focus="true">
                            <div class="row">
                                <div class="small-6 columns">
                                    <label for="num_adults" class="text-right">Adults (ages 12+)<label>
                                </div>
                                <div class="small-6 columns">
                                    <input type="number" id="numAdults" name="num_adults" v-model="numAdults" min="0" max="16"/></label>
                                </div>
                            </div>
                            <div class="row" style="display:none;">
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
                                    <label for="num_children" class="text-right">Children (ages 4-12)<label>
                                </div>
                                <div class="small-6 columns">
                                    <input type="number" id="numChildren" name="num_children" v-model="numChildren" min="0" max="16"/></label>
                                </div>
                            </div>
                            <div class="row">
                                <div class="small-6 columns">
                                    <label for="num_children" class="text-right">Infants (ages 0-4)<label>
                                </div>
                                <div class="small-6 columns">
                                    <input type="number" id="numInfants" name="num_infants" v-model="numInfants" min="0" max="16"/></label>
                                </div>
                            </div>
                            <div class="row" style="display:none;">
                                <div class="small-6 columns">
                                    <label for="num_children" class="text-right">Moorings<label>
                                </div>
                                <div class="small-6 columns">
                                    <input type="number" id="numMooring" name="num_mooring" v-model="numMooring" min="0" max="16"/></label>
                                </div>
                            </div>

                       </div>
                    </div>
                </div>
                <div class="row">
                    <div class="small-12 columns">
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

                <div class="row">
                     <div class="small-12 columns">
                        <hr/>
                     </div>
                 </div>
                 <div class="row">
                    <div class="small-12 medium-12 large-12 columns">
                        <label>Types</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="pen_type" value="all" v-model="penType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC3"></i> All types</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="pen_type" value="0" v-model="penType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC20"></i> Moorings</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="pen_type" value="1" v-model="penType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC20"></i> Jetty Pens</label>
                    </div>
                    <div class="small-12 medium-12 large-4 columns">
                        <label><input type="radio" name="pen_type" value="2" v-model="penType" class="show-for-sr" v-on:change="reload()"/><i class="symb RC20"></i> Beach Pens</label>
                    </div>
                </div>

                <!-- <div class="row"><div class="small-12 columns"> -->
                    <hr class="search"/>
                <!-- </div>  -->

                <div class="row" id="legend" style="margin-bottom:10px;">
                    <div class="small-12 medium-12 large-12 columns">
                        <label>Availability</label>
                    </div>
                    <div class="small-12 medium-12 large-3 columns">
                        <label>Public:
                            <img class="publicPin" src="./assets/map_pins/pin_gray.png" />
                        </label>
                    </div>
                    <div class="small-12 medium-12 large-3 columns">
                        <label>Available:
                            <img class="availablePin" src="./assets/map_pins/pin_orange.png" />
                        </label>
                    </div>
                    <div class="small-12 medium-12 large-3 columns">
                        <label>Partial Dates:
                            <img class="partialPin" src="./assets/map_pins/pin_orange_red.png" />
                        </label>
                    </div>
                    <div class="small-12 medium-12 large-3 columns">
                        <label>Unavailable:
                            <img class="unavailablePin" src="./assets/map_pins/pin_red.png" />
                        </label>
                    </div>
                </div>


                <div class="row"><div class="small-12 columns">
                    <hr class="search"/>
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
            </div>
<!-- here -->
            <div class="small-12 medium-9 large-6 columns">
                <div class="alert alert-warning" style='text-align: center' role="alert" v-if="admissions_key" id="admissions_link"> <strong style='font-size: 16px;' ></span><a :href='"/admissions/" + admissions_key + "/"'>Click here for paying admission fees only</a></strong><br></div>
                <div style='width: 100%; height: 1px;' align='right'>
                       <div v-show='mapLoading == true' class='map-loading' style='border: 1px solid #00000' ><img style='width:20px; height: 20px;' src='/static/common/img/ajax-loader-spinner.gif'>&nbsp;&nbsp;Please Wait</div>
                </div>
                <div id="map"></div>
                <div style='width: 100%' align='right'>
	                <img id='satellite-toggle' class='map-toggle-white'  type='button'  @click="toggleMap('satellite');" src='./assets/img/satellite_icon.png'  >
                        <img id='map-toggle' class='map-toggle-black'  type='button'  @click="toggleMap('map');" src='./assets/img/map_icon.png'  >
		</div>
                <div id="mapPopup" class="mapPopup" v-cloak>
                    <a href="#" id="mapPopupClose" class="mapPopupClose"></a>
                    <div id="mapPopupContent">
                        <h4 style="margin: 0"><b id="mapPopupName"></b></h4>
                        <p><i id="mapPopupPrice"></i></p>
                        <img class="thumbnail" id="mapPopupImage" style='width: 230px; height: 230px;' />
                        <div id="mapPopupDescription" style="font-size: 0.75rem;"/>
                        <p>Mooring Limits</p>
                        <div class="row">
                            <div class="col-md-7"  style='display:none'>
                                <small>Max Stay: <span id='max_stay_period'></span> day/s</small>
                            </div>
                            <div class="col-md-5">
                                <small>Max Size: <span id='vessel_size_popup'></span></small>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-7">
                                <small>Max Draft: <span id='vessel_draft_popup'></span></small>
                            </div>
                            <div class="col-md-5">
                                <small><span id='vessel_beam_weight_popup'></span></small>
                            </div>
                        </div>
                        <input id='mapPopupMooringType' type='hidden' >
                        <a id="mapPopupInfo" class="button formButton" style="margin-bottom: 0; margin-top: 1em;" target="_blank">More info</a>
                        <a id="mapPopupBook" class="button formButton" style="margin-bottom: 0;" v-on:click="BookNowCheck()" >Book now</a>
                    </div>
                </div>
            </div>
        </div>
        <template v-if="extentFeatures.length > 0">
            <paginate name="filterResults" class="resultList" :list="extentFeatures" :per="9">
                <div class="row">
                    <div class="small-12 medium-4 large-4 columns" v-for="f in paginated('filterResults')" v-if="f.vessel_size_limit >= vesselSize && f.vessel_draft_limit >= vesselDraft && weightBeam(f) == true">
                        <div class="row">
                            <div class="small-12 columns">
                                <span class="searchTitle">{{ f.name }}</span>
                            </div>
                            <div class="small-12 medium-12 large-12 columns" >
                                <img v-if="f.images[0]" class="thumbnail" v-bind:src="f.images[0].image" style='width: 230px; height: 230px;' />
                                <img v-else class="thumbnail" src="/static/exploreparks/mooring_photo_scaled.png" style='width: 230px; height: 230px;'/>
                            </div>
                            <div class="small-12 medium-9 large-9 columns">
                                <div v-html="f.description"/>
                                <p v-if="f.price_hint && Number(f.price_hint)"><i><small>From ${{ f.price_hint }} per night</small></i></p>
                                <!-- <p style='display:none'><i><small>Vessel Size Limit: {{ f.vessel_size_limit }} </small></i></p>
                                <p ><i><small>Max Stay Period: {{ f.max_advance_booking }} day/s </small></i></p> -->
                                <p>Mooring Limits</p>
                                <div class="row">
                                    <div class="col-md-6"  style='display:none'>
                                        <small>Max Stay: {{ f.max_advance_booking }} day/s</small>
                                    </div>
                                    <div class="col-md-6">
                                        <small>Max Size: {{ f.vessel_size_limit }}</small>
                                    </div>
                                </div>
                                <div class="row">

                                    <div class="col-md-6">
                                        <small>Max Draft: {{ f.vessel_draft_limit }}</small>
                                    </div>
                                    <div class="col-md-6">
                                        <small v-if="f.mooring_physical_type == 0"> Max Weight: {{ f.vessel_weight_limit }}</small>
                                        <small v-else> Max Beam: {{ f.vessel_beam_limit }}</small>
                                    </div>
                                </div>


                                <a class="button" v-bind:href="f.info_url" target="_blank">More info</a>
                                 
                                <a v-if="f.mooring_type == 0 && vesselSize > 0 && vesselDraft > 0 && vesselWeight > 0 && vesselRego != '' && vesselRego !== ' '" class="button" v-bind:href="parkstayUrl+'/availability2/?site_id='+f.id+'&'+bookingParam">Book now</a>
                                <a v-else-if="f.mooring_type == 1 && vesselSize > 0 && vesselDraft > 0 && vesselBeam > 0 && vesselRego != '' && vesselRego !== ' '" class="button" v-bind:href="parkstayUrl+'/availability2/?site_id='+f.id+'&'+bookingParam">Book now</a>
				<a v-else-if="f.mooring_type == 2 && vesselSize > 0 && vesselDraft > 0 && vesselBeam > 0 && vesselRego != '' && vesselRego !== ' '" class="button" v-bind:href="parkstayUrl+'/availability2/?site_id='+f.id+'&'+bookingParam">Book now</a>
                                <a v-else-if="f.mooring_type == 0" class="button" v-on:click="BookNow('mooring')">Book now</a>
                                <a v-else-if="f.mooring_type == 1 || f.mooring_type == 2 " class="button" v-on:click="BookNow('jettybeach')">Book now</a>
                                <a v-else /> 
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

    .map-toggle-black {
       width: 80px;
       height: 80px;
       background-color: #FFFFFF;
       color: black;
       position: relative;
       right: 10px;
       top: -90px;
       z-index: 300;
       border: 2px solid #FFFFFF;
       cursor: pointer;
       border-radius: 2px;
       box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.3);
    }
    .map-toggle-white {
       width: 80px;
       height: 80px;
       background-color: #FFFFFF;
       color: black;
       position: relative;
       right: 10px;
       top: -90px;
       z-index: 300;
       border: 2px solid #000000;
       cursor: pointer;
       border-radius: 2px;
       box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.3);
    }
    .map-loading {
       position: relative;
       top: 14px;
       background-color: #FFFFFF;
       border: 1px solid #bab9b9;
       z-index: 5;
       width: 110px;
       text-align: center;
       opacity: 0.7;
       margin-right: 8px;
       font-size: 12px;
       padding: 4px;
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

var nowTemp = new Date();
var now = moment.utc({year: nowTemp.getFullYear(), month: nowTemp.getMonth(), day: nowTemp.getDate(), hour: 0, minute: 0, second: 0}).toDate();
var fivedays = new Date();
fivedays.setDate(fivedays.getDate() + 5);
fivedays = moment.utc({year: fivedays.getFullYear(), month: fivedays.getMonth(), day: fivedays.getDate(), hour: 0, minute: 0, second: 0}).toDate();

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
            arrivalDate: now,
            departureDate: fivedays,
            dateCache: null,
            numAdults: 2,
            numConcessions: 0,
            numChildren: 0,
            numInfants: 0,
            numMooring: 1,
            gearType: 'all',
            penType: 'all',
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
            vesselRego: '',
            vesselSize: 0,
            vesselDraft: 0,
            vesselBeam: 0,
            vesselWeight: 0,
            groupPinLevelChange: true,
            anchorPinLevelChange: true,
            mooring_map_data: null,
            markerAvail: [],
            current_booking: [],
            total_booking: "0.00",
            timer: -1,
            expiry: null,
            booking_expired_notification: false,
            ongoing_booking: false,
            admissions_key: null,
            pinsCache:{},
            mapLoading: false,
            loadingID: 0,
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
                // var count = this.numAdults + this.numConcessions + this.numChildren + this.numInfants + this.numMooring;
                var count = this.numAdults + this.numConcessions + this.numChildren + this.numInfants;
                if (count === 1) {
                    return count +" person ▼";
                } else {
                    return count + " people ▼";
                }
            }
        },
        timeleft: {
                cache: false,
                get: function() {
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
                           this.bookingExpired();
                           this.booking_expired_notification = true;
                        }
                       }
                    }
                    return ret;
                }
        },
        bookingParam: {
            cache: false,
            get: function() {
                if (this.vesselSize % 1 != 0){
                    this.vesselSize = parseFloat(this.vesselSize);
//                    this.vesselSize = Math.ceil(this.vesselSize);
                }
                if (this.vesselDraft % 1 != 0){
                    this.vesselDraft = parseFloat(this.vesselDraft);
//                    this.vesselDraft = Math.ceil(this.vesselDraft);
                }
                if (this.vesselBeam % 1 != 0){
                    this.vesselBeam = parseFloat(this.vesselBeam);
//                    this.vesselBeam = Math.ceil(this.vesselBeam);
                }
                if (this.vesselWeight % 1 != 0){
                    this.vesselWeight = parseFloat(this.vesselWeight);
//                    this.vesselWeight = Math.ceil(this.vesselWeight);
                }
                var params = {
                    'num_adult': this.numAdults,
                    'num_children': this.numChildren,
                    'num_infant': this.numInfants,
                    'num_mooring' : this.numMooring,
                    'gear_type': this.gearType,
                    'pen_type': this.penType,
                    'vessel_size' : this.vesselSize,
                    'vessel_draft': this.vesselDraft,
                    'vessel_beam': this.vesselBeam,
                    'vessel_weight': this.vesselWeight,
                    'vessel_rego': this.vesselRego,
                };
                if (this.arrivalDate && this.departureDate) {
                    params['arrival'] = this.arrivalDateString;
                    params['departure'] = this.departureDateString;
                }
                return $.param(params);
            }
        }
    },
    methods: {
        searchRego: function(){
            let vm = this;
            vm.vesselRego = vm.vesselRego.replace(/ /g, "");
            
            var reg = vm.vesselRego;
            var data = {
                'rego': reg
            }
            if(reg){
                $.ajax({
                    url: process.env.PARKSTAY_URL + "/api/registeredVessels/",
                    dataType: 'json',
                    data: data,
                    method: 'GET',
                    success: function(data, stat, xhr) {
                        if(data[0]){
                            vm.vesselWeight =  parseFloat(data[0].vessel_weight);
                            vm.vesselBeam = parseFloat(data[0].vessel_beam);
                            vm.vesselSize = parseFloat(data[0].vessel_size);
                            vm.vesselDraft = parseFloat(data[0].vessel_draft);
                            $("#vesselSize").val(data[0].vessel_size);
                            $("#vesselWeight").val(data[0].vessel_weight);
                            $("#vesselBeam").val(data[0].vessel_beam);
                            $("#vesselDraft").val(data[0].vessel_draft);
                            vm.removePinAnchors();
                            vm.removePinGroups();

                            vm.buildmarkers();

                        } else {
                            console.log("Registration was not found.");
                        }
                    }
                });
            } else {
                vm.vesselWeight = 0;
                vm.vesselBeam = 0;
                vm.vesselSize = 0;
                vm.vesselDraft = 0;
            }
        },
        weightBeam: function(f){
            if (f.mooring_physical_type == 0){
                if (f.vessel_weight_limit >= this.vesselWeight){
                    return true;
                } else {
                    return false;
                }
            } else {
                if (f.vessel_beam_limit >= this.vesselBeam){
                    return true;
                } else {
                    return false;
                }
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
                        window.location = loc.protocol + '//' + loc.host + '/map/';
                });

        },
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
                        $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability2/?site_id='+feature.getId()+'&'+vm.bookingParam);
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
                $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability2/?site_id='+feature.getId()+'&'+vm.bookingParam);
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
              // this.removePinAnchors();
              this.anchorPinLevelChange = true;
              this.buildmarkers();
         //   this.refreshPopup();
        }, 250),
        removePinGroups: function() {
                // this.pinsCache = {};
                var layerRemoved = false;
                var map = this.olmap;
                var refArray = map.getLayers().getArray().slice();
//              refArray.forEach(function(layer2) {
                for (var i = 0; i < refArray.length; i++) {
                    var layer2 = refArray[i];
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
                }
//              });
                if (layerRemoved == true) {
                    // We do this because when we call map.removeLayer it causes the layer 
                    // to go out of sync resulting in pins not being removed as foreach loop is 
                    // changed.  This loop ensure all pins have been removed

	            this.removePinGroups();
		}
                return layerRemoved; 
	},
        removePinAnchors: function() {
                // return false;
                // this.pinsCache = {};
                var layerRemoved = false;
                var map = this.olmap;
                var refArray = map.getLayers().getArray().slice();
                for (var i = 0; i < refArray.length; i++) {
                        var layer2 = refArray[i];
                    if (layer2 != null) {
                        var layer = layer2.I;
                        if (layer != null) {
                            // map.removeLayer(layer2);
                            if (layer.hasOwnProperty("markerGroup")) {
                                if (layer.markerGroup == 'anchor') {
                                    layer2.setVisible(false);
                                    // map.removeLayer(layer2);
                                    // layerRemoved = true;
                                }
                            }
                        }
                    }

                }

//                refArray.forEach(function(layer2) {
//                    if (layer2 != null) {
//                        var layer = layer2.I;
//                        if (layer != null) {
//                            // map.removeLayer(layer2);
//                            if (layer.hasOwnProperty("markerGroup")) {
//                                if (layer.markerGroup == 'anchor') {
//                                    map.removeLayer(layer2);
//                                    layerRemoved = true;
//                                }
//                            }
//                        }
//                    }
//                });

                // var layersToRemove = [];

                // map.getLayers().forEach(function(layer) {
                //     if (layer.I.hasOwnProperty("markerGroup")){
                //         layersToRemove.push(layer);
                //     }
                // });
                // var len = layersToRemove.length;
                // for (var i=0; i < len; i++){
                //     map.removeLayer(layersToRemove[i]);
                //     layerRemoved = true;
                // }

                if (layerRemoved == true) {
                    // We do this because when we call map.removeLayer it causes the layer
                    // to go out of sync resulting in pins not being removed as foreach loop is
                    // changed.  This loop ensure all pins have been removed

                    // this.removePinAnchors();
                }
                return layerRemoved;
        },
        toggleMap: function(current_selection) {
	   var vm = this;
           var map = this.olmap;
           map.getLayers().forEach(function (layer) {
             var name = layer.get('name');
             if (name != undefined) {
                var visible = layer.getVisible();
                if (visible == false) {
                    layer.setVisible(true);
		}
                if (visible == true) {
                    layer.setVisible(false);
                }

             }
   
           });
                if (current_selection == 'satellite') {
                  $('#satellite-toggle').hide();
                  $('#map-toggle').show();
                } else {
                  $('#satellite-toggle').show();
                  $('#map-toggle').hide();
                }


	},
        updateFilter: function() {
            var vm = this;
            // make a lookup table of campground features to filter on
            var legit = new Set();
            var filterCb = function (el) {
                if (vm.filterParams[el.key] === true) {
                    for (var i = 0; i < el.remoteKey.length; i++) {
                         console.log(i);
                         console.log(el.remoteKey[i]);
                         legit.add(el.remoteKey[i]);
		    }                  
 

                    // el.remoteKey.forEach(function (fl) {
                    //   legit.add(fl);
                    // });
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
            this.removePinAnchors();
            this.removePinGroups();
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



//          map.updateSize();
           
            var response = vm.anchorPins;
            var pin_count = 0;
            for (var x in response) {
                var mooring = response[x];
                for (var m in mooring) {
                    for (var b in response[x][m]) {
		        if (b == 'geometry') {
                            var vessel_size = $("#vesselSize").val();
                            var vessel_draft = $("#vesselDraft").val();
                            var vessel_beam = $("#vesselBeam").val();
                            var vessel_weight = $("#vesselWeight").val();
                            var type_filter = $("input[name=pen_type]:checked").val();
                            var show_marker = true;
                            if (response[x][m]['properties']['vessel_size_limit'].length == 0) { 
                                response[x][m]['properties']['vessel_size_limit'] = 0;
                            }

                          
                            if (response[x][m]['properties']['mooring_physical_type'] == 0) { 
                                     if (parseFloat(vessel_size) > 0) {
                                         show_marker = false;
                                         if (parseFloat(response[x][m]['properties']['vessel_size_limit']) >= parseFloat(vessel_size)) {
                                             show_marker = true;
                                         }
                                     }

                                     if (parseFloat(vessel_draft) > 0) {
                                         if (show_marker == true) { 
                                            show_marker = false;
                                            if (parseFloat(response[x][m]['properties']['vessel_draft_limit']) >= parseFloat(vessel_draft)) {
                                               show_marker = true;
                                            }
                                         }
                                     }
                                     if (parseFloat(vessel_weight) > 0) {
                                         if (show_marker == true) {
                                            show_marker = false;
                                            if (parseFloat(response[x][m]['properties']['vessel_weight_limit']) >= parseFloat(vessel_weight)) {
                                               show_marker = true;
                                            }
                                         }
                                     }

                            } else if (response[x][m]['properties']['mooring_physical_type'] == 1 || response[x][m]['properties']['mooring_physical_type'] == 2) { 
                                     if (parseFloat(vessel_size) > 0) {
                                         show_marker = false;
                                         if (parseFloat(response[x][m]['properties']['vessel_size_limit']) >= parseFloat(vessel_size)) {
                                             show_marker = true;
                                         }
                                     }
                                     if (parseFloat(vessel_draft) > 0) {
                                         if (show_marker == true) {
                                             show_marker = false;
                                             if (parseFloat(response[x][m]['properties']['vessel_draft_limit']) >= parseFloat(vessel_draft)) {
                                                 show_marker = true;
                                             }
                                         }
                                     }
                                     if (parseFloat(vessel_beam) > 0) {
                                         if (show_marker == true) {
                                            show_marker = false;
                                            if (parseFloat(response[x][m]['properties']['vessel_beam_limit']) >= parseFloat(vessel_beam)) {
                                               show_marker = true;
                                            }
                                         }
                                     }
			    } else {
                                    show_marker = false;
			    }
                            if (show_marker == true) {
                                     if (type_filter == 'all') { 
				     } else { 
                                         show_marker = false;
                                         if (type_filter == 0) {
						if (parseInt(response[x][m]['properties']['mooring_physical_type']) == 0) {
							show_marker = true;
						}
					 }
                                         if (type_filter == 1) {
                                                if (parseInt(response[x][m]['properties']['mooring_physical_type']) == 1) {
                                                        show_marker = true;
                                                }

                                         }
                                         if (type_filter == 2) {
                                                if (parseInt(response[x][m]['properties']['mooring_physical_type']) == 2) {
                                                        show_marker = true;
                                                }

                                         }

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
                                                                     if (vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]] == null) { 
                                		                     map.addLayer(vm.buildMarkerBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
								     } else {
		                                                            var layer2 = vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]];
                		                                            layer2.setVisible(true);
		
                		                                     }

                                                            }
                                                        }
                                                    
                                                    } else {
                                                        if (mooring_type == 'rental-notavailable') {
                                                            // if (this.groundsIds.has(marker_id)) {
                                                            // } else {
                                                            if (response[x][m]['geometry'] != null ) {
                                                                if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
                                                                   if (vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]] == null) {
                                                                   map.addLayer(vm.buildMarkerBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                                   } else {
		                                                            var layer2 = vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]];
                		                                            layer2.setVisible(true);
			
                        		                             }

                                                                }
                                                            }
                                                        }
                                                    }
				                }
                                            } else {
                                                if (response[x][m]['geometry'] != null ) {
                                                    if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
                                                       if (vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]] == null) {
                                                          map.addLayer(vm.buildMarkerBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                       } else {
                                                            var layer2 = vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]];
                                                            layer2.setVisible(true);

                                                     }

                                                    }
                                                }
							                }
                                        }
			            }
 
                                    if (response[x][m]['properties']['mooring_type'] == 1) {
                                        if (mooring_type == 'all') {
                                            if (response[x][m]['geometry'] != null ) {
                                                if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
                                                        if (vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]] == null) {
						                      map.addLayer(vm.buildMarkerBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                        } else {
                                                            var layer2 = vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]];
                                                            layer2.setVisible(true);

                                                     }

                                                }
                                            }
							            }
						            }
                                    if (response[x][m]['properties']['mooring_type'] == 2) {
                                        if (mooring_type == 'all' || mooring_type == 'public-notbookable') {
                                            if (response[x][m]['geometry'] != null ) {
                                                if (response[x][m]['geometry'].hasOwnProperty('coordinates')) {
                                                     if (vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]] == null) {
                                                     map.addLayer(vm.buildMarkerNotBookable(response[x][m]['geometry']['coordinates'][0],response[x][m]['geometry']['coordinates'][1],response[x][m]['properties'],response[x][m]['properties']['name'],response[x][m]['id']));
                                                     } else {
                                                            var layer2 = vm.pinsCache[response[x][m]['id']+'-'+vm.markerAvail[response[x][m]['id']]];
                                                            layer2.setVisible(true);
                                                            
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
            var pen_filter = $("input[name=pen_type]:checked").val();
            if (response) { 
                if (response.hasOwnProperty('features')) {

                    var mooring = response['features'];
                    for (var m in mooring) {
                        var mooring_id = response['features'][m]['id'];
                        var mooring_vessel_size = response['features'][m]['properties']['vessel_size_limit'];
                        var mooring_vessel_draft = response['features'][m]['properties']['vessel_draft_limit'];
                        var mooring_physical_type = response['features'][m]['properties']['mooring_physical_type'];
//                        if (mooring_vessel_size >= vessel_size && mooring_vessel_draft >= vessel_draft && this.weightBeam(response['features'][m]['properties']) && ((pen_filter != 'all' && pen_filter == mooring_physical_type) || pen_filter == 'all') && vm.groundsIds['_c'].has(mooring_id)) {
                        if (mooring_vessel_size >= vessel_size && mooring_vessel_draft >= vessel_draft && this.weightBeam(response['features'][m]['properties']) && ((pen_filter != 'all' && pen_filter == mooring_physical_type) || pen_filter == 'all') && vm.groundsIds.has(mooring_id)) {
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
                }
            }
            if (Object.keys(vm.anchorGroups).length == 0){
                // vm.removePinGroups();
            } else {
                for (var g in vm.anchorGroups) {
                    var longitude = vm.anchorGroups[g]['geometry'][0];
                    var latitude = vm.anchorGroups[g]['geometry'][1];

                    var total = vm.anchorGroups[g]['total'];
                    var name = vm.anchorGroups[g]['name'];
                    var zoom_level = vm.anchorGroups[g]['zoom_level'];
                    map.addLayer(vm.buildMarkerGroup(parseFloat(longitude),parseFloat(latitude),total,name, zoom_level));
                }
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
            var vectorLayer;
            var vm = this;
            if (vm.pinsCache[marker_id] == null) { 
            if (this.groundsIds.has(marker_id)) {
                if (vm.markerAvail[marker_id] == 'free') { 
                     pin_type=require('assets/map_pins/pin_orange.png');
                     bookable = true;
                } else if (vm.markerAvail[marker_id] == 'partial') {
                     pin_type=require('assets/map_pins/pin_orange_red.png');
                     bookable = true;
                } else {
                     pin_type=require('assets/map_pins/pin_red.png');
                     bookable = false;
	            }	
	        }

                //this.anchorPinsActive.push(marker_id);
            var iconFeature = new ol.Feature({
                marker_group: 'mooring_marker',
                geometry: new ol.geom.Point(ol.proj.transform([lat, lon], 'EPSG:4326', 'EPSG:3857')),
                name: name,
                bookable: bookable,
                marker_id: marker_id,
                props: props
            });

            var iconStyle = new ol.style.Style({
                image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                    imgSize: [32, 32],
                    size: [32,32],
                    snapToPixel: true,
                    anchor: [0.5, 1.0],
                    anchorXUnits: 'fraction',
                    anchorYUnits: 'fraction',
                    opacity: 0.95,
                    src: pin_type 
                })),
            });
            // console.log("SET buildMarkerBookable");
            iconFeature.setStyle(iconStyle);

            var vectorSource = new ol.source.Vector({
                features: [iconFeature]
            });

            vectorLayer = new ol.layer.Vector({
               canDelete: "yes",
               markerGroup: "anchor",
               source: vectorSource
            });
             vm.pinsCache[marker_id+'-'+vm.markerAvail[marker_id]] = vectorLayer; 
            } else {
              vectorLayer = vm.pinsCache[marker_id+'-'+vm.markerAvail[marker_id]];
	    }
            return vectorLayer;
        },
    buildMarkerNotBookable: function(lat,lon,props,name,marker_id) {
                var vm = this; 
                if (vm.pinsCache[marker_id+'-'+vm.markerAvail[marker_id]] == null) {
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
                    size: [32,32], 
                    snapToPixel: true,
                    anchor: [0.5, 1.0],
			//    anchor: [115.864627, -32.007385],
		    anchorXUnits: 'fraction',
                    anchorYUnits: 'fraction',
		    opacity: 0.95,
		    src: require('assets/map_pins/pin_gray.png')

	         }))
	    });
            // console.log("SET buildMarkerNotBookable");
	    iconFeature.setStyle(iconStyle);
	
	    var vectorSource = new ol.source.Vector({
	        features: [iconFeature]
	    });

	    var vectorLayer = new ol.layer.Vector({
	       canDelete: "yes",
               markerGroup: "anchor",
	       source: vectorSource
	    });
            vm.pinsCache[marker_id+'-'+vm.markerAvail[marker_id]] = vectorLayer;
            } else {
                 vectorLayer = vm.pinsCache[marker_id+'-'+vm.markerAvail[marker_id]];
            }
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
                          imgSize: [48, 46],
                          size: [48,46],
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
              // console.log("SET buildMarkerGroup");
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
      deleteBooking: function(booking_item_id) {
              var vm = this;
              var submitData = {
                  booking_item: booking_item_id,
              };

              $.ajax({
                  url: vm.parkstayUrl + '/api/booking/delete',
                  dataType: 'json',
                  method: 'POST',
                  data: submitData,
                  success: function(data, stat, xhr) {
                      vm.updateBooking();
                  },
                  error: function(xhr, stat, err) {
                       vm.updateBooking();
                  }
              });  
      },
      updateBooking: function() {
        var vm = this;
        $.ajax({
            url: vm.parkstayUrl+'/api/current_booking',
            dataType: 'json',
            // async: false,
            success: function (response, stat, xhr) {
                vm.current_booking = response.current_booking.current_booking;
                vm.total_booking = response.current_booking.total_price;
                vm.timer = response.current_booking.timer;
                vm.ongoing_booking = response.current_booking.ongoing_booking[0];
                if (response.current_booking.details != null) {  
                     vm.numAdults = parseInt(response.current_booking.details[0].num_adults) > 0 ? parseInt(response.current_booking.details[0].num_adults) : 2;
                     vm.numChildren = parseInt(response.current_booking.details[0].num_children) > 0 ? parseInt(response.current_booking.details[0].num_children) : 0;
                     vm.numInfants =  parseInt(response.current_booking.details[0].num_infants) > 0 ? parseFloat(response.current_booking.details[0].num_infants) : 0;
                     vm.vesselSize = parseFloat(response.current_booking.details[0].vessel_size) > 0 ? parseFloat(response.current_booking.details[0].vessel_size) : 0;
                     vm.vesselDraft = parseFloat(response.current_booking.details[0].vessel_draft) > 0 ? parseFloat(response.current_booking.details[0].vessel_draft) : 0;
                     vm.vesselBeam = parseFloat(response.current_booking.details[0].vessel_beam) > 0 ? parseFloat(response.current_booking.details[0].vessel_beam) : 0;
                     vm.vesselWeight = parseFloat(response.current_booking.details[0].vessel_weight) > 0 ? parseFloat(response.current_booking.details[0].vessel_weight) : 0;
                     vm.vesselRego = response.current_booking.details[0].vessel_rego ? response.current_booking.details[0].vessel_rego : "";
		}

            }
        });

      },
      BookNowCheck: function() {
         var mooring_type = $('#mapPopupMooringType').val();
         if (mooring_type == 0) { 
             this.BookNow('mooring');
	 } else {
             this.BookNow('jettybeach');
	 }

      },
      BookNow: function(mooring_type) { 
        var vessel_size = $('#vesselSize').val();
        var vessel_draft = $('#vesselDraft').val();
        var vessel_beam = $('#vesselBeam').val();
        var vessel_weight = $('#vesselWeight').val();
        var vessel_rego = $('#vesselRego').val();
        if (!(vessel_draft > 0)){
            swal({
            title: 'Missing Vessel Draft',
            text: "Please enter vessel draft:",
            type: 'warning',
            showCancelButton: false,
            confirmButtonText: 'OK',
            showLoaderOnConfirm: true,
            allowOutsideClick: false
            })
        }
        if (!(vessel_size > 0) ) {
            swal({
            title: 'Missing Vessel Size',
            text: "Please enter vessel size:",
            type: 'warning',
            showCancelButton: false,
            confirmButtonText: 'OK',
            showLoaderOnConfirm: true,
            allowOutsideClick: false
            })
        }
        if (mooring_type == 'jettybeach') {  
        if (!(vessel_beam > 0)){
            swal({
            title: 'Missing Vessel Beam',
            text: "Please enter vessel beam:",
            type: 'warning',
            showCancelButton: false,
            confirmButtonText: 'OK',
            showLoaderOnConfirm: true,
            allowOutsideClick: false
            })
        }
        }
        if (mooring_type == 'mooring') {
        if (!(vessel_weight > 0)){
            swal({
            title: 'Missing Vessel Weight',
            text: "Please enter vessel weight:",
            type: 'warning',
            showCancelButton: false,
            confirmButtonText: 'OK',
            showLoaderOnConfirm: true,
            allowOutsideClick: false
            })
        }
        }
        if (!vessel_rego || vessel_rego == "" || vessel_rego == " "){
            swal({
                title: 'Missing Vessel Registration',
                text: "Please enter a vessel registration.",
                type: 'warning',
                showCancelButton: false,
                confirmButtonText: 'OK',
                showLoaderOnConfirm: true,
                allowOutsideClick: false,
            })
        }
      },
      loadMap: function() {

        var vm = this;

        console.log('Loading map...');
        var nowTemp = new Date();
        var now = moment.utc({year: nowTemp.getFullYear(), month: nowTemp.getMonth(), day: nowTemp.getDate(), hour: 0, minute: 0, second: 0}).toDate();

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
                layer: 'public:mapbox-satellite',
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

//        this.groundsSource.loadSource = function (onSuccess) {
//
//            if (vm.dateCache != vm.arrivalDateString+vm.departureDateString+vm.gearType+vm.penType) {
//            var urlBase = vm.parkstayUrl+'/api/mooring_map_filter/?';
//            var params = {format: 'json'};
//            var isCustom = false;
//
//
//            if ((vm.arrivalData.date) && (vm.departureData.date)) {
//                isCustom = true;
//                var arrival = vm.arrivalDateString;
//                if (arrival) {
//                    params.arrival = arrival;
//                }
//                var departure = vm.departureDateString;
//                if (departure) {
//                    params.departure = vm.departureDateString;
//                }
//                params.num_adult = vm.numAdults;
//                params.num_concessions = vm.numConcessions;
//                params.num_children = vm.numChildren;
//                params.num_infant = vm.numInfants;
//                params.num_mooring = vm.numMooring;
//                params.gear_type = vm.gearType;
//                params.pen_type = vm.penType;
//                
//            }
//            $.ajax({
//                url: urlBase+$.param(params),
//                success: function (response, stat, xhr) {
//                    vm.groundsIds.clear();
//                    response.forEach(function(el) {
//                        vm.groundsIds.add(el.id);
//                    });
//                    vm.updateFilter();
//                    vm.dateCache = vm.arrivalDateString+vm.departureDateString+vm.gearType+vm.penType;
//                },
//                dataType: 'json'
//            });
//            }
//        };

//        this.grounds = new ol.layer.Vector({
//            source: this.groundsSource,
//            style: function (feature) {
//                var style = feature.get('style');
//                return style;
//            }
//        });

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
            interactions: ol.interaction.defaults({}).extend([
                  new ol.interaction.PinchZoom({
                      constrainResolution: true
                   })
            ]),
            layers: [
                this.streets,
                this.tenure,
                // this.grounds,
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
        var template_group = $('#template_group').val();
        if (template_group == 'rottnest') { 
		vm.admissions_key = 'ria';
	}
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
        this.arrivalEl.fdatepicker('update', now);

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
        var fivedays = new Date();
        fivedays.setDate(fivedays.getDate() + 5);
        fivedays = moment.utc({year: fivedays.getFullYear(), month: fivedays.getMonth(), day: fivedays.getDate(), hour: 0, minute: 0, second: 0}).toDate();
        
        this.departureEl.fdatepicker('update', fivedays);

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
            name: 'street',
            canDelete: "no",
            visible: true,
            source: new ol.source.WMTS({
                url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
                format: 'image/png',
                layer: 'public:mapbox-streets',
                matrixSet: this.matrixSet,
                projection: this.projection,
                tileGrid: tileGrid
            })
        });



        this.satellite = new ol.layer.Tile({
            name: 'satellite',
            canDelete: "no",
            visible: false,
            source: new ol.source.WMTS({
                url: 'https://kmi.dpaw.wa.gov.au/geoserver/gwc/service/wmts',
                format: 'image/png',
                layer: 'public:mapbox-satellite',
                matrixSet: this.matrixSet,
                projection: this.projection,
                tileGrid: tileGrid
            })
        });


        this.tenure = new ol.layer.Tile({
            name: 'tenure',
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
               // vm.groundsSource.loadSource();
               vm.buildmarkers();
 
            }
        });

        vm.updateBooking();
        this.groundsSource = new ol.source.Vector({
            features: vm.groundsFilter   
        });

        this.groundsSource.loadSource = function (onSuccess) {
            
            if (vm.dateCache != vm.arrivalDateString+vm.departureDateString+vm.gearType+vm.penType) {
                    vm.mapLoading = true;
                    vm.loadingID = vm.loadingID + 1;
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
                        params.num_infant = vm.numInfants;
                        params.num_mooring = vm.numMooring;
                        params.gear_type = vm.gearType;
                        params.pen_type = vm.penType;
                    }
                    
                    $.ajax({
                        loadID: vm.loadingID,
                        url: urlBase+$.param(params),
                        success: function (response, stat, xhr) {
                            vm.groundsIds.clear();
                            response.forEach(function(el) {
                               vm.groundsIds.add(el.id);

                               vm.dateCache = vm.arrivalDateString+vm.departureDateString+vm.gearType+vm.penType;
                               vm.markerAvail[el.id] = el.avail;
                            });

                            vm.updateFilter();
                       //     vm.removePinAnchors();
                       //     vm.anchorPinLevelChange = true;
                            vm.buildmarkers();
                            if (vm.loadingID == this.loadID) {
                               vm.mapLoading = false;
                            }

                        },
                        error: function(xhr, stat, err) {
                            if (vm.loadingID == this.loadID) {
	                            vm.mapLoading = false;
                            }
                            swal({
                              title: 'Error',
                              text: "There was and error loading map data please try again.",
                              type: 'error',
                              showCancelButton: false,
                              confirmButtonText: 'Close',
                              showLoaderOnConfirm: true,
                              allowOutsideClick: false
                            });
			},
                        dataType: 'json'
                    });
          }
       };
       this.grounds = new ol.layer.Vector({
           source: this.groundsSource,
            style: function (feature) {
                var style = feature.get('style');
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
                anchorYUnits: 'fraction',
                imgSize: [32, 32] // JM
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
            interactions: ol.interaction.defaults({}).extend([
                  new ol.interaction.PinchZoom({
                      constrainResolution: true
                   })
            ]),
            layers: [
                this.streets,
                this.satellite,
                this.tenure,
                this.grounds,
                this.posLayer
            ],
            overlays: [this.popup]
        });

        $('#map-toggle').hide();
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



        $('#vesselRego').blur(function() {
               vm.searchRego();
        });

        $('#vesselSize').blur(function() { 
               vm.vesselSize = this.value;
               vm.removePinAnchors();
               vm.removePinGroups();
	       vm.buildmarkers();
        });
        $('#vesselDraft').blur(function() { 
               vm.vesselDraft = this.value;
               vm.removePinAnchors();
               vm.removePinGroups();
	       vm.buildmarkers();
        });
        $('#vesselBeam').blur(function() { 
               vm.vesselBeam = this.value;
               vm.removePinAnchors();
               vm.removePinGroups();
	       vm.buildmarkers();
        });
        $('#vesselWeight').blur(function() { 
               vm.vesselWeight = this.value;
               vm.removePinAnchors();
               vm.removePinGroups();
	       vm.buildmarkers();
	    });

        $('#vesselDraft').blur(function() {
               vm.vesselDraft = this.value;
               vm.removePinAnchors();
               vm.removePinGroups();
               vm.buildmarkers();
        });

        $('#dateArrival').change(function() {
               // vm.groundsSource.loadSource();
               vm.reload();
        });

        $('#dateDeparture').change(function() {
                vm.reload();
               // vm.groundsSource.loadSource();
        });

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
                $('#mapPopupInfo').attr('href', properties.props.info_url);
                if (properties.props.mooring_type == 0 || properties.props.mooring_type == 1 || properties.props.mooring_type == 2) {
                    $('#mapPopupMooringType').val(properties.props.mooring_physical_type);
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
		            $("#max_stay_period").html(properties.props.max_advance_booking);
                    $("#vessel_size_popup").html(properties.props.vessel_size_limit);
                    $("#vessel_draft_popup").html(properties.props.vessel_draft_limit);
                    if(properties.props.mooring_physical_type == 0){
                        $("#vessel_beam_weight_popup").html("Max Weight: " + properties.props.vessel_weight_limit);
                    }
                    else {
                        $("#vessel_beam_weight_popup").html("Max Beam: " + properties.props.vessel_beam_limit);
                    }
                    var vessel_size = $('#vesselSize').val();
                    var vessel_draft = $('#vesselDraft').val();
                    var vessel_rego = $('#vesselRego').val();
                    var vessel_beam = $('#vesselBeam').val();
                    var vessel_weight = $('#vesselWeight').val();

                    if (properties.props.mooring_physical_type == 0 && vessel_size > 0 && vessel_draft > 0 && vessel_weight > 0 &&vessel_rego.length > 1) {
                        var distance_radius = properties.props.park.distance_radius;
                        $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability2/?site_id='+properties.marker_id+'&distance_radius='+distance_radius+'&'+vm.bookingParam);
                        // $("#mapPopupBook").attr('target','_blank');

                    } else if ((properties.props.mooring_physical_type == 1 || properties.props.mooring_physical_type == 2 ) && ( vessel_size > 0 && vessel_draft > 0 && vessel_beam > 0 && vessel_rego.length > 1)) { 
			var distance_radius = properties.props.park.distance_radius;
		        $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability2/?site_id='+properties.marker_id+'&distance_radius='+distance_radius+'&'+vm.bookingParam);
                    } else {
	                      $("#mapPopupBook").attr('href','javascript:void(0);');
                              $("#mapPopupBook").attr('target','');
                   }
                } else {
                    $("#max_stay_period").html(properties.props.max_advance_booking);
                    $("#vessel_size_popup").html(properties.props.vessel_size_limit);
                    $("#vessel_draft_popup").html(properties.props.vessel_draft_limit);
                    if(properties.props.mooring_physical_type == 0){
                        $("#vessel_beam_weight_popup").html("Vessel Weight: " + properties.props.vessel_weight_limit);
                    }
                    else {
                        $("#vessel_beam_weight_popup").html("Vessel Beam: " + properties.props.vessel_beam_limit);
                    }   
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
                    //if (properties.props) { 
                    //if (properties.props.mooring_type == 0) {
                    //    $('#mapPopupBook').show();
                    //    $("#mapPopupImage").hide();
                    //    var vessel_size = $('#vesselSize').val();
                    //    var vessel_rego = $('#vesselRego').val();
                    //    var vessel_draft = $('#vesselDraft').val();
                    //    if (vessel_size > 0 && vessel_draft > 0 && vessel_rego.length > 1) { 
                    //           var distance_radius = properties.props.park.distance_radius;
                    //           $("#mapPopupBook").attr('href', vm.parkstayUrl+'/availability2/?site_id='+properties.marker_id+'&distance_radius='+distance_radius+'&'+vm.bookingParam);
                    //    } else {
		    //    	 $("#mapPopupBook").attr('href','javascript:void;');
		    //    }
                    //} else {
                    //    $('#mapPopupBook').hide();
                    //}
		    //} else {
		    //    $('#mapPopupBook').hide();
		    //}
	        } 

          } else {
             $(element).hide();
          }
        });

            var x = document.cookie.split('vessel_rego=');
            if(x.length == 2){
                var secondHalf = x[1].split(';');
                var rego = secondHalf[0];
                vm.vesselRego = rego;
                vm.searchRego(rego);
            }

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



        // hook to update the visible feature list on viewport change
        this.olmap.getView().on('propertychange', function(ev) {
            vm.updateViewport();
            vm.buildmarkers();
        });
	this.reload();
    }
};
</script>
