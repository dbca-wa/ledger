<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large>
            <div class="container-fluid">
                <ul class="nav nav-pills">
                    <li class="nav-item active"><a data-toggle="tab" :href="'#'+oTab">Offence</a></li>
                    <li class="nav-item"><a data-toggle="tab" :href="'#'+dTab">Details</a></li>
                    <li class="nav-item"><a data-toggle="tab" :href="'#'+pTab">Offender(s)</a></li>
                    <li class="nav-item"><a data-toggle="tab" :href="'#'+lTab" @click="mapOffenceClicked">Location</a></li>
                </ul>
                <div class="tab-content">
                    <div :id="oTab" class="tab-pane fade in active">
                        <div class="row">

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left" for="offence-identifier">Identifier</label>
                                </div>
                                <div class="col-sm-6">
                                    <div v-if="offence">
                                        <input type="text" class="form-control" name="identifier" placeholder="" v-model="offence.identifier" v-bind:key="offence.id">
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">Use occurrence from/to</label>
                                <input class="col-sm-1" id="occurrence_from_to_true" type="radio" v-model="offence.occurrence_from_to" v-bind:value="true">
                                <label class="col-sm-1 radio-button-label" for="occurrence_from_to_true">Yes</label>
                                <input class="col-sm-1" id="occurrence_from_to_false" type="radio" v-model="offence.occurrence_from_to" v-bind:value="false">
                                <label class="col-sm-1 radio-button-label" for="occurrence_from_to_false">No</label>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">{{ occurrenceDateLabel }}</label>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="occurrenceDateFromPicker">
                                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="offence.occurrence_date_from" />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                                <div v-show="offence.occurrence_from_to">
                                    <div class="col-sm-3">
                                        <div class="input-group date" ref="occurrenceDateToPicker">
                                            <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="offence.occurrence_date_to" />
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">{{ occurrenceTimeLabel }}</label>
                                <div class="col-sm-3">
                                    <div class="input-group date" ref="occurrenceTimeFromPicker">
                                        <input type="text" class="form-control" placeholder="HH:MM" v-model="offence.occurrence_time_from" />
                                        <span class="input-group-addon">
                                            <span class="glyphicon glyphicon-calendar"></span>
                                        </span>
                                    </div>
                                </div>
                                <div v-show="offence.occurrence_from_to">
                                    <div class="col-sm-3">
                                        <div class="input-group date" ref="occurrenceTimeToPicker">
                                            <input type="text" class="form-control" placeholder="HH:MM" v-model="offence.occurrence_time_to" />
                                            <span class="input-group-addon">
                                                <span class="glyphicon glyphicon-calendar"></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">Alleged Offence</label>
                                <div class="col-sm-6">
                                    <input class="form-control" id="alleged-offence" />
                                </div>
                                <div class="col-sm-3">
                                    <input type="button" class="btn btn-primary" value="Add" @click.prevent="addAllegedOffenceClicked()" />
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-12">
                                    <datatable ref="alleged_offence_table" id="alleged-offence-table" :dtOptions="dtOptionsAllegedOffence" :dtHeaders="dtHeadersAllegedOffence" />
                                </div>
                            </div></div>
                        </div>
                    </div>

                    <div :id="dTab" class="tab-pane fade in">
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="form-group">
                                    <div class="row">
                                        <div class="col-sm-3">
                                            <label class="control-label pull-left" for="offence-details">Details</label>
                                        </div>
                                        <div class="col-sm-6">
                                            <div v-if="offence">
                                                <textarea class="form-control" placeholder="add details" id="offence-details" v-model="offence.details" v-bind:key="offence.id"/>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div :id="pTab" class="tab-pane fade in">
                        <div class="row">
                            <div class="col-sm-12 form-group"><div class="row">
                                <input class="col-sm-1" id="offender_individual" type="radio" v-model="offender_search_type" value="individual">
                                <label class="col-sm-1 radio-button-label" for="offender_individual">Individual</label>
                                <input class="col-sm-1" id="offender_organisation" type="radio" v-model="offender_search_type" value="organisation">
                                <label class="col-sm-1 radio-button-label" for="offender_organisation">Organisation</label>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <label class="col-sm-3">Offender</label>
                                <div class="col-sm-6">
                                    <input class="form-control" id="offender_input" />
                                </div>
                                <div class="col-sm-3">
                                    <input type="button" class="btn btn-primary" value="Add" @click.prevent="addOffenderClicked()" />
                                </div>
                            </div></div>

                            <div class="col-sm-12 form-group"><div class="row">
                                <div class="col-sm-12">
                                    <datatable ref="offender_table" id="offender-table" :dtOptions="dtOptionsOffender" :dtHeaders="dtHeadersOffender" />
                                </div>
                            </div></div>
                        </div>
                    </div>

                    <div :id="lTab" class="tab-pane fade in">
                        <div class="row">
                            <div class="col-sm-12 form-group">
                                <div v-if="offence.location">
                                    <MapLocationOffence v-bind:key="lTab" :id="lTab" ref="mapOffenceComponent"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div slot="footer">
                <button type="button" v-if="processingDetails" disabled class="btn btn-default" @click="ok"><i class="fa fa-spinner fa-spin"></i> Adding</button>
                <button type="button" v-else class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>

<script>
import Vue from 'vue'
import Awesomplete from 'awesomplete'
import modal from '@vue-utils/bootstrap-modal.vue'
import datatable from '@vue-utils/datatable.vue'
import { mapGetters, mapActions } from 'vuex'
import { api_endpoints, helpers, cache_helpew } from '@/utils/hooks'
import MapLocationOffence from './map_location_offence1'
import utils from '../utils'
import $ from 'jquery'
import 'bootstrap/dist/css/bootstrap.css'
import 'awesomplete/awesomplete.css'

export default {
    name: "Offence",
    data: function() {
        let vm = this;
    
        vm.max_items = 20;
        vm.ajax_for_alleged_offence = null;
        vm.ajax_for_offender = null;
        vm.suggest_list = []; // This stores a list of alleged offences displayed after search.
        vm.suggest_list_offender = []; // This stores a list of alleged offences displayed after search.
        vm.awe = null;
        vm.awe_offender = null;
    
        return {
            officers: [],
            isModalOpen: false,
            processingDetails: false,
            current_alleged_offence: {
                id: null,
                Act: '',
                SectionRegulation: '',
                AllegedOffence: '',
            },
            current_offender: null,
            offender_search_type: 'individual',
            oTab: 'oTab'+vm._uid,
            dTab: 'dTab'+vm._uid,
            pTab: 'pTab'+vm._uid,
            lTab: 'lTab'+vm._uid,
            dtHeadersOffender: [
                'id',
                'data_type',
                'Description',
                'Action',
            ],
            dtHeadersAllegedOffence: [
                'id',
                'Act',
                'Section/Regulation',
                'Alleged Offence',
                'Action',
            ],
            dtOptionsOffender: {
                columns: [
                    {
                        data: 'id',
                        visible: false
                    },
                    {
                        data: 'data_type',
                        visible: true
                    },
                    {
                        data: '',
                        mRender: function(data, type, row){
                            if (row.data_type == 'individual'){
                                let full_name = [row.first_name, row.last_name].filter(Boolean).join(' ');
                                let email = row.email?'E:' + row.email:'';
                                let p_number = row.phone_number?'P:' + row.phone_number:'';
                                let m_number = row.mobile_number?'M:' + row.mobile_number:'';
                                let dob = row.dob?'DOB:' + row.dob:'DOB: ---';
                                let myLabel = ['<strong>' + full_name + '</strong>', email, p_number, m_number, dob].filter(Boolean).join('<br />');

                                return myLabel;
                            } else if (row.data_type == 'organisation'){
                                let name = row.name?row.name:'';
                                let abn = row.abn?'ABN:' + row.abn:'';
                                let myLabel = ['<strong>' + name + '</strong>', abn].filter(Boolean).join('<br />');

                                return myLabel;
                            }
                        }
                    },
                    {
                        data: 'Action',
                        mRender: function(data, type, row){
                            return '<a href="#" class="remove_button" data-offender-id="' + row.id + '">Remove</a>';
                        }
                    },
                ]
            },
            dtOptionsAllegedOffence: {
                columns: [
                    {
                        data: 'id',
                        visible: false
                    },
                    { 
                        data: 'Act', 
                    },
                    { 
                        data: 'Section/Regulation',
                    },
                    { 
                        data: 'Alleged Offence', 
                    },
                    { 
                        data: 'Action',
                        mRender: function(data, type, row){
                            return '<a href="#" class="remove_button" data-alleged-offence-id="' + row.id + '">Remove</a>';
                        }
                    },
                ]
            },
        }
    },
    components: {
        modal,
        datatable,
        MapLocationOffence,
    },
    computed: {
        ...mapGetters('callemailStore', {
            call_email: "call_email",
        }),
        ...mapGetters('offenceStore', {
            offence: 'offence',
        }),
        modalTitle: function() {
            return "Identify Offence";
        },
        occurrenceDateLabel: function() {
            if (this.offence.occurrence_from_to) {
                return "Occurrence date from";
            } else {
                return "Occurrence date";
            }
        },
        occurrenceTimeLabel: function() {
            if (this.offence.occurrence_from_to) {
                return "Occurrence time from";
            } else {
                return "Occurrence time";
            }
        },
    },
    filters: {
        formatDate: function(data) {
            return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
        }
    },
    methods: {
        ...mapActions('callemailStore', {
            setAllocatedTo: "setAllocatedTo",
            loadCallEmail: 'loadCallEmail',
        }),
        ...mapActions('offenceStore', {
            setAllegedOffenceIds: "setAllegedOffenceIds",
            setOffenders: "setOffenders",
            setCallEmailId: "setCallEmailId",
            saveOffence: "saveOffence",
            setOffenceEmpty: "setOffenceEmpty",
        }),
        removeOffenderClicked: function(e){   
            let vm = this;

            let offenderId = parseInt(e.target.getAttribute("data-offender-id"));
            vm.$refs.offender_table.vmDataTable.rows(function(idx, data, node){
                if(data.id === offenderId){
                    vm.$refs.offender_table.vmDataTable.row(idx).remove().draw();
                }
            });
        },
        removeClicked: function(e){   
            let vm = this;

            let allegedOffenceId = parseInt(e.target.getAttribute("data-alleged-offence-id"));
            vm.$refs.alleged_offence_table.vmDataTable.rows(function(idx, data, node){
                if(data.id === allegedOffenceId){
                    vm.$refs.alleged_offence_table.vmDataTable.row(idx).remove().draw();
                }
            });

        },
        addOffenderClicked: function() {
            let vm = this;

            if(vm.current_offender.id && vm.current_offender.data_type){
                let already_exists = false;

                let ids = vm.$refs.offender_table.vmDataTable.columns(0).data()[0];
                let data_types = vm.$refs.offender_table.vmDataTable.columns(1).data()[0];

                for (let i=0; i<ids.length; i++){
                    if (ids[i] == vm.current_offender.id && data_types[i] == vm.current_offender.data_type){
                        already_exists = true;
                        break;
                    }
                }

                if (!already_exists){
                    if (vm.current_offender.data_type == 'individual'){
                        vm.$refs.offender_table.vmDataTable.row.add({
                            'data_type': vm.current_offender.data_type,
                            'id': vm.current_offender.id,
                            'first_name': vm.current_offender.first_name,
                            'last_name': vm.current_offender.last_name,
                            'email': vm.current_offender.email,
                            'p_number': vm.current_offender.p_number,
                            'm_number': vm.current_offender.m_numberum,
                            'dob': vm.current_offender.dob,
                        }).draw();
                    } else if (vm.current_offender.data_type == 'organisation'){
                        vm.$refs.offender_table.vmDataTable.row.add({
                            'data_type': vm.current_offender.data_type,
                            'id': vm.current_offender.id,
                            'name': vm.current_offender.name,
                            'abn': vm.current_offender.abn,
                        }).draw();
                    }
                }
            }

            vm.setCurrentOffenderEmpty();
        },
        addAllegedOffenceClicked: function() {
            let vm = this;

            if(vm.current_alleged_offence.id){
                let already_exists = vm.$refs.alleged_offence_table.vmDataTable.columns(0).data()[0].includes(vm.current_alleged_offence.id);

                if (!already_exists){
                    vm.$refs.alleged_offence_table.vmDataTable.row.add(
                        {
                            'id': vm.current_alleged_offence.id,
                            'Act': vm.current_alleged_offence.Act,
                            'Section/Regulation': vm.current_alleged_offence.SectionRegulation,
                            'Alleged Offence': vm.current_alleged_offence.AllegedOffence,
                        }
                    ).draw();
                }
            }

            vm.setCurrentAllegedOffenceEmpty();
        },
        ok: async function () {
            await this.sendData();

            // Update call_email in vuex
            await this.loadCallEmail({ call_email_id: this.call_email.id }); 

            this.setOffenceEmpty();
            this.close();
        },
        cancel: function() {
            this.isModalOpen = false;
            this.close();
        },
        close: function () {
            this.isModalOpen = false;
        },
        mapOffenceClicked: function(){
            this.$refs.mapOffenceComponent.mapTabClicked();
        },
        sendData: async function(){
            let vm = this;

            // Set call_email id to the offence
            vm.setCallEmailId(vm.call_email.id);

            // Collect offenders data from the datatable, and set them to the vuex
            let offenders = vm.$refs.offender_table.vmDataTable.rows().data().toArray();
            vm.setOffenders(offenders);

            // Collect alleged offence data from the datatable, and set them to the vuex
            let alleged_offences = vm.$refs.alleged_offence_table.vmDataTable.rows().data().toArray();
            let alleged_offence_ids = alleged_offences.map(a => {
                return({ 'id': a.id }); // We just need id to create relations between the offence and the alleged offence(s)
            });
            vm.setAllegedOffenceIds(alleged_offence_ids);

            // TODO: send data to the server
            vm.saveOffence();
        },
        addEventListeners: function () {
            let vm = this;
            let el_fr_date = $(vm.$refs.occurrenceDateFromPicker);
            let el_fr_time = $(vm.$refs.occurrenceTimeFromPicker);
            let el_to_date = $(vm.$refs.occurrenceDateToPicker);
            let el_to_time = $(vm.$refs.occurrenceTimeToPicker);
  
            // "From" field
            el_fr_date.datetimepicker({ format: 'DD/MM/YYYY', maxDate: 'now', showClear: true });
            el_fr_date.on('dp.change', function (e) {
                if (el_fr_date.data('DateTimePicker').date()) {
                    vm.offence.occurrence_date_from = e.date.format('DD/MM/YYYY');
                } else if (el_fr_date.data('date') === "") {
                    vm.offence.occurrence_date_from = "";
                }
            });
            el_fr_time.datetimepicker({ format: 'LT', showClear: true });
            el_fr_time.on('dp.change', function (e) {
                if (el_fr_time.data('DateTimePicker').date()) {
                    vm.offence.occurrence_time_from = e.date.format('LT');
                } else if (el_fr_time.data('date') === "") {
                    vm.offence.occurrence_time_from = "";
                }
            });
  
            // "To" field
            el_to_date.datetimepicker({ format: 'DD/MM/YYYY', maxDate: 'now', showClear: true });
            el_to_date.on('dp.change', function (e) {
                if (el_to_date.data('DateTimePicker').date()) {
                    vm.offence.occurrence_date_to = e.date.format('DD/MM/YYYY');
                } else if (el_to_date.data('date') === "") {
                    vm.offence.occurrence_date_to = "";
                }
            });
            el_to_time.datetimepicker({ format: 'LT', showClear: true });
            el_to_time.on('dp.change', function (e) {
                if (el_to_time.data('DateTimePicker').date()) {
                    vm.offence.occurrence_time_to = e.date.format('LT');
                } else if (el_to_time.data('date') === "") {
                    vm.offence.occurrence_time_to = "";
                }
            });

            $('#alleged-offence-table').on('click', '.remove_button', vm.removeClicked);
            $('#offender-table').on('click', '.remove_button', vm.removeOffenderClicked);
        },
        search_offender: function(searchTerm){
            var vm = this;
            vm.suggest_list_offender = [];
            vm.suggest_list_offender.length = 0;
            vm.awe_offender.list = [];

            /* Cancel all the previous requests */
            if (vm.ajax_for_offender != null){
                vm.ajax_for_offender.abort();
                vm.ajax_for_offender = null;
            }

            let search_url = '';
            if (vm.offender_search_type == 'individual'){
                search_url = '/api/search_user/?search=';
            } else {
                search_url = '/api/search_organisation/?search=';
            }

            vm.ajax_for_offender = $.ajax({
                type: 'GET',
                url: search_url + searchTerm,
                success: function(data){
                    if (data && data.results) {
                        let persons = data.results;
                        let limit = Math.min(vm.max_items, persons.length);
                        for (var i = 0; i < limit; i++){
                            vm.suggest_list_offender.push(persons[i])
                        }
                    }
                    vm.awe_offender.list = vm.suggest_list_offender;
                    vm.awe_offender.evaluate();
                },
                error: function (e){

                }
            });

        },
        search: function(searchTerm){
            var vm = this;
            vm.suggest_list = [];
            vm.suggest_list.length = 0;
            vm.awe.list = [];
  
            /* Cancel all the previous requests */
            if (vm.ajax_for_alleged_offence != null){
                vm.ajax_for_alleged_offence.abort();
                vm.ajax_for_alleged_offence = null;
            }
  
            vm.ajax_for_alleged_offence = $.ajax({
                type: 'GET',
                url: '/api/search_alleged_offences/?search=' + searchTerm,
                success: function(data){
                    if (data && data.results) {
                        let persons = data.results;
                        let limit = Math.min(vm.max_items, persons.length);
                        for (var i = 0; i < limit; i++){
                            vm.suggest_list.push(persons[i])
                        }
                    }
                    vm.awe.list = vm.suggest_list;
                    vm.awe.evaluate();
                },
                error: function (e){

                }
            });
        },
        markMatchedText(original_text, input){
            let ret_text = original_text.replace(new RegExp(input, "gi"), function(a, b){
                return '<mark>' + a + '</mark>';
            });
            return ret_text;
        },
        initAwesompleteOffender: function(){
            let self = this;
  
            let element_search = document.getElementById('offender_input');
            self.awe_offender = new Awesomplete(element_search, {
                maxItems: self.max_items,
                sort: false,
                filter: ()=>{ return true; }, // Display all the items in the list without filtering.
                item: function(text, input){
                    let ret =  Awesomplete.ITEM(text, ''); // Not sure how this works but this doesn't add <mark></mark>
                    return ret;
                },
                data: function(item, input){
                    if (self.offender_search_type == 'individual') {
                        let f_name = item.first_name?item.first_name:'';
                        let l_name = item.last_name?item.last_name:'';

                        let full_name = [f_name, l_name].filter(Boolean).join(' ');
                        let email = item.email?'E:' + item.email:'';
                        let p_number = item.phone_number?'P:' + item.phone_number:'';
                        let m_number = item.mobile_number?'M:' + item.mobile_number:'';
                        let dob = item.dob?'DOB:' + item.dob:'DOB: ---';

                        let full_name_marked = '<strong>' + self.markMatchedText(full_name, input) + '</strong>';
                        let email_marked = self.markMatchedText(email, input);
                        let p_number_marked = self.markMatchedText(p_number, input);
                        let m_number_marked = self.markMatchedText(m_number, input);
                        let dob_marked = self.markMatchedText(dob, input);

                        let myLabel = [full_name_marked, email_marked, p_number_marked, m_number_marked, dob_marked].filter(Boolean).join('<br />');
                        myLabel = '<div data-item-id=' + item.id + ' data-type="individual">' + myLabel + '</div>';

                        return { 
                            label: myLabel,   // Displayed in the list below the search box
                            value: [full_name, dob].filter(Boolean).join(', '), // Inserted into the search box once selected
                            id: item.id
                        };
                    } else {
                        let name = item.name?item.name:'';
                        let abn = item.abn?'ABN:' + item.abn:'';

                        let name_marked = '<strong>' + self.markMatchedText(name, input) + '</strong>';
                        let abn_marked = self.markMatchedText(abn, input);

                        let myLabel = [name_marked, abn_marked].filter(Boolean).join('<br />');
                        myLabel = '<div data-item-id=' + item.id + ' data-type="organisation">' + myLabel + '</div>';

                        return { 
                            label: myLabel,
                            value: [name, abn].filter(Boolean).join(', '),
                            id: item.id
                        };
                    }
                }
            });
            $(element_search).on('keyup', function(ev){
                var keyCode = ev.keyCode || ev.which;
                if ((48 <= keyCode && keyCode <= 90)||(96 <= keyCode && keyCode <= 105) || (keyCode == 8) || (keyCode == 46)){
                  self.search_offender(ev.target.value);
                  return false;
                }
            }).on('awesomplete-selectcomplete', function(ev){
                ev.preventDefault();
                ev.stopPropagation();
                return false;
            }).on('awesomplete-select', function(ev){
                /* Retrieve element id of the selected item from the list
                 * By parsing it, we can get the order-number of the item in the list
                 */
                let origin = $(ev.originalEvent.origin)
                let originTagName = origin[0].tagName;
                if (originTagName != "DIV"){
                    // Assuming origin is a child element of <li>
                    origin = origin.parent();
                }
                let data_item_id = origin[0].getAttribute('data-item-id');
                let data_type = origin[0].getAttribute('data-type');

                for(let i = 0; i < self.suggest_list_offender.length; i++){
                    if (self.suggest_list_offender[i].id == parseInt(data_item_id)){
                        self.setCurrentOffender(data_type, self.suggest_list_offender[i].id);
                        break;
                    }
                }
            });
        },
        initAwesompleteAllegedOffence: function(){
            var self = this;
  
            var element_search = document.getElementById('alleged-offence');
            self.awe = new Awesomplete(element_search, {
                maxItems: self.max_items,
                sort: false,
                filter: ()=>{ return true; }, // Display all the items in the list without filtering.
                item: function(text, input){
                    let ret =  Awesomplete.ITEM(text, ''); // Not sure how this works but this doesn't add <mark></mark>
                    return ret;
                },
                data: function(item, input){
                    let act = item.act?item.act:'';
                    let name = item.name?item.name:'';
                    let offence_text = item.offence_text?item.offence_text:'';

                    let act_marked = self.markMatchedText(act, input);
                    let name_marked = self.markMatchedText(name, input);
                    let offence_text_marked = self.markMatchedText(offence_text, input);
  
                    let myLabel = ['<strong>' + act_marked + ', ' + name_marked + '</strong>', offence_text_marked].filter(Boolean).join('<br />');
                    myLabel = '<div data-item-id="' + item.id + '">' + myLabel + '</div>';
  
                    return {
                        label: myLabel,   // Displayed in the list below the search box
                        value: [act, name, offence_text].filter(Boolean).join(', '), // Inserted into the search box once selected
                        id: item.id
                    };
                }
            });
            $(element_search).on('keyup', function(ev){
                var keyCode = ev.keyCode || ev.which;
                if ((48 <= keyCode && keyCode <= 90)||(96 <= keyCode && keyCode <= 105) || (keyCode == 8) || (keyCode == 46)){
                  self.search(ev.target.value);
                  return false;
                }
            }).on('awesomplete-selectcomplete', function(ev){
                ev.preventDefault();
                ev.stopPropagation();
                return false;
            }).on('awesomplete-select', function(ev){
                /* Retrieve element id of the selected item from the list
                 * By parsing it, we can get the order-number of the item in the list
                 */
                let origin = $(ev.originalEvent.origin)
                let originTagName = origin[0].tagName;
                if (originTagName != "DIV"){
                    // Assuming origin is a child element of <li>
                    origin = origin.parent();
                }
                let elem_id = origin[0].getAttribute('data-item-id');
                for(let i = 0; i < self.suggest_list.length; i++){
                    if (self.suggest_list[i].id == parseInt(elem_id)){
                        self.setCurrentOffenceSelected(self.suggest_list[i]);
                        break;
                    }
                }
            });
        },
        searchOrganisation: function(id){
            return new Promise ((resolve,reject) => {
                Vue.http.get('/api/search_organisation/' + id).then((response) => {
                    resolve(response.body);
                },
                (error) => {
                    reject(error);
                });
            });
        },
        setCurrentOffender: function(data_type, id){
            let vm = this;

            if (data_type == 'individual'){
                let initialisers = [
                    utils.fetchUser(id),
                ]
                Promise.all(initialisers).then(data => {
                    vm.current_offender = data[0];
                    vm.current_offender.data_type = 'individual';
                });
            } else if (data_type == 'organisation'){
                let initialisers = [
                    vm.searchOrganisation(id),
                ]
                Promise.all(initialisers).then(data => {
                    vm.current_offender = data[0];
                    vm.current_offender.data_type = 'organisation';
                });
            }
        },
        setCurrentOffenceSelected: function(offence){
            let vm = this;

            if(offence.id){
                vm.current_alleged_offence.id = offence.id;
                vm.current_alleged_offence.Act = offence.act;
                vm.current_alleged_offence.SectionRegulation = offence.name;
                vm.current_alleged_offence.AllegedOffence = offence.offence_text;
            } else {
                vm.setCurrentAllegedOffenceEmpty();
            }
        },
        setCurrentOffenderEmpty: function(){
            let vm = this;

            vm.current_offender = null;

            $('#offender_input').val('');
        },
        setCurrentAllegedOffenceEmpty: function(){
            let vm = this;

            vm.current_alleged_offence.id = null;
            vm.current_alleged_offence.Act = '';
            vm.current_alleged_offence.SectionRegulation = '';
            vm.current_alleged_offence.AllegedOffence = '';

            $('#alleged-offence').val('');
        },
    },
    created: async function() {
        this.$nextTick(function() {
            this.initAwesompleteAllegedOffence();
            this.initAwesompleteOffender();
        });
    },
    mounted: function() {
        let vm = this;
        vm.$nextTick(() => {
            vm.addEventListeners();
        });
    }
};
</script>

<style lang="css" scoped>
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
.top-buffer{margin-top: 5px;}
.top-buffer-2x{margin-top: 10px;}
#offence-details {

}
.radio-button-label {
    padding-left: 0;
}
.awesomplete {
    display: inherit !important;
}
.tab-content {
    background: white;
    padding: 10px;
    border: solid 1px lightgray;
}
#DataTable {
    padding: 10px 5px;
    border: 1px solid lightgray;
}
</style>
