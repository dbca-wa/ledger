<template>
    <div class="container" id="internalSanctionOutcomeDash">
        <FormSection :label="`Sanction Outcome`" :Index="`0`">

        <div class="row">
            <div class="col-md-3">
                <label class="">Type:</label>
                <select class="form-control" v-model="filterType">
                    <option v-for="option in sanction_outcome_types" :value="option.id" v-bind:key="option.id">
                        {{ option.display }}
                    </option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="">Status:</label>
                <select class="form-control" v-model="filterStatus">
                    <option v-for="option in sanction_outcome_statuses" :value="option.id" v-bind:key="option.id">
                        {{ option.display }}
                    </option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="">Payment status:</label>
                <select class="form-control" v-model="filterPaymentStatus">
                    <option v-for="option in sanction_outcome_payment_statuses" :value="option.id" v-bind:key="option.id">
                        {{ option.display }}
                    </option>
                </select>
            </div>
        </div>
        <div class="row">
            <div class="col-md-3">
                <label class="">Issue date from:</label>
                <div class="input-group date" ref="issueDateFromPicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateFromPicker" />
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
            <div class="col-md-3">
                <label class="">Issue date to:</label>
                <div class="input-group date" ref="issueDateToPicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateToPicker" />
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-3">
                <label class="">Region:</label>
                                  <!-- <select class="form-control col-sm-9" v-on:change.prevent="sanction_outcome.region_id=$event.target.value; updateDistricts('updatefromUI')" v-bind:value="sanction_outcome.region_id">
                                    <option  v-for="option in regions" :value="option.id" v-bind:key="option.id">
                                      {{ option.display_name }} 
                                    </option>
                                  </select> -->
                <select class="form-control" v-on:change.prevent="filterRegionId=$event.target.value; updateDistricts('updatefromUI')" v-bind:value="filterRegionId">
                    <option v-for="option in sanction_outcome_regions" :value="option.id" v-bind:key="option.id">
                        {{ option.display_name }}
                    </option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="">District:</label>
                                  <!-- <select class="form-control" v-model="sanction_outcome.district_id">
                                    <option  v-for="option in availableDistricts" :value="option.id" v-bind:key="option.id">
                                      {{ option.display_name }} 
                                    </option>
                                  </select> -->
                <select class="form-control" v-model="filterDistrictId">
                    <option v-for="option in sanction_outcome_availableDistricts" :value="option.id" v-bind:key="option.id">
                        {{ option.display_name }}
                    </option>
                </select>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="sanction_outcome_table" id="sanction_outcome-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
            </div>
        </div>
        </FormSection>
    </div>
</template>

<script>
import $ from 'jquery'
import datatable from '@vue-utils/datatable.vue'
import FormSection from "@/components/compliance_forms/section.vue";
import { api_endpoints, helpers, cache_helper } from '@/utils/hooks'

export default {
    name: 'SanctionOutcomeTableDash',
    data() {
        let vm = this;
        return {
            sanction_outcome_types: [],
            sanction_outcome_statuses: [],
            sanction_outcome_payment_statuses: [],
            sanction_outcome_regions: [],  //this is the list of options
            sanction_outcome_regionDistricts: [],
            sanction_outcome_availableDistricts: [], // this is generated from the regionDistricts[] above

            filterType: 'all',
            filterStatus: 'all',
            filterPaymentStatus: 'all',
            filterDateFromPicker: '',
            filterDateToPicker: '',
            filterRegionId: 'all',
            filterDistrictId: 'all',

            dtOptions: {
                serverSide: true,
                searchDelay: 1000,
                lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                order: [
                    [0, 'desc']
                ],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                processing: true,
                ajax: {
                    url: '/api/sanction_outcome_paginated/get_paginated_datatable/?format=datatables',
                    dataSrc: 'data',
                    data: function(d) {
                        d.type = vm.filterType;
                        d.status = vm.filterStatus;
                        d.payment_status = vm.filterPaymentStatus;
                        d.date_from = vm.filterDateFromPicker;
                        d.date_to = vm.filterDateToPicker;
                        d.region_id = vm.filterRegionId;
                        d.district_id = vm.filterDistrictId;
                    }
                },
                columns: [
                    {
                        data: 'lodgement_number',
                        searchable: true,
                        orderable: true,
                    },
                    {
                        data: 'type',
                        searchable: false,
                        orderable: true,
                        mRender: function (data, type, full) {
                            return data.name;
                        }
                    },
                    {
                        data: 'identifier',
                        searchable: true,
                        orderable: true
                    },
                    {
                        data: 'date_of_issue',
                        searchable: true,
                        orderable: true,
                        mRender: function (data, type, full) {
                            return data != '' && data != null ? moment(data).format('DD/MM/YYYY') : '';
                        }
                    },
                    {
                        data: 'offender',
                        searchable: true,
                        orderable: true,
                        mRender: function (data, type, row){
                            let name = '';
                            let num_chars = 30;
                            if (data && data.person){
                                name = data.person.first_name + ' ' + data.person.last_name;
                            } else if (data && data.organisation) {
                                name = data.organisation.name;
                            }

                            let shortText = (name.length > num_chars) ?
                                '<span title="' + name + '">' + $.trim(name).substring(0, num_chars).split(" ").slice(0, -1).join(" ") + '...</span>' :
                                name;
                            return shortText;
                        }
                    },
                    {
                        data: 'status.name',
                        searchable: true,
                        orderable: true,
                    },
                    {
                        searchable: true,
                        orderable: false,
                        mRender: function (data, type, row){
                            return '---';
                        }
                    },
                    {
                        searchable: true,
                        orderable: false,
                        mRender: function (data, type, row){
                            return '---';
                        }
                    },
                    {
                        data: 'user_action',
                        searchable: false,
                        orderable: true,
                        mRender: function (data, type, row){
                            console.log(data);
                            if (data){
                                return data;
                            } else { 
                                return '---';
                            }
                        }
                    }
                ],
            },
            dtHeaders: [
                'Number',
                'Type',
                'Identifier',
                'Date',
                'Offender',
                'Status',
                'Payment Status',
                'Sanction Outcome',
                'Action',
            ],
        }
    },
    mounted(){
        let vm = this;
        vm.$nextTick(() => {
            vm.addEventListeners();
        });
    },
    computed: {
        current_region_id: function() {
            return this.filterRegionId;
        },
    },
    watch: {
        current_region_id: function() {
            this.updateDistricts();
        },
        filterType: function () {
            this.$refs.sanction_outcome_table.vmDataTable.draw();
        },
        filterStatus: function () {
            this.$refs.sanction_outcome_table.vmDataTable.draw();
        },
        filterPaymentStatus: function () {
            this.$refs.sanction_outcome_table.vmDataTable.draw();
        },
        filterDateFromPicker: function () {
            this.$refs.sanction_outcome_table.vmDataTable.draw();
        },
        filterDateToPicker: function () {
            this.$refs.sanction_outcome_table.vmDataTable.draw();
        },
        filterRegionId: function () {
            this.$refs.sanction_outcome_table.vmDataTable.draw();
        },
        filterDistrictId: function () {
            this.$refs.sanction_outcome_table.vmDataTable.draw();
        },
    },
    created: async function() {
        this.constructOptionsType();
        this.constructOptionsStatus();
        this.constructOptionsPaymentStatus();
        this.constructOptionsRegion();
        this.constructOptionsDistrict();
    },
    methods: {
        updateDistricts: function(updateFromUI) {
            console.log('updateDistricts');
            // if (updateFromUI) {
            //     // We don't want to clear the default district selection when initially loaded, which derived from the call_email
            //     this.sanction_outcome.district_id = null;
            // }
            this.sanction_outcome_availableDistricts = []; // This is a list of options for district
            for (let record of this.sanction_outcome_regionDistricts) {
                if (this.filterRegionId == record.id) {
                    for (let district_id of record.districts) {
                        for (let district_record of this.sanction_outcome_regionDistricts) {
                            if (district_record.id == district_id) {
                                this.sanction_outcome_availableDistricts.push(district_record);
                            }
                        }
                    }
                }
            }

            this.sanction_outcome_availableDistricts.splice(0, 0, {
                id: "all",
                display_name: "All",
                district: "",
                districts: [],
                region: null
            });

            this.filterDistrictId = 'all';
        },
        addEventListeners: function () {
            this.attachFromDatePicker();
            this.attachToDatePicker();
        },
        attachFromDatePicker: function(){
            let vm = this;
            let el_fr = $(vm.$refs.issueDateFromPicker);
            let el_to = $(vm.$refs.issueDateToPicker);

            el_fr.datetimepicker({ format: 'DD/MM/YYYY', maxDate: 'now', showClear: true });
            el_fr.on('dp.change', function (e) {
                if (el_fr.data('DateTimePicker').date()) {
                    vm.filterDateFromPicker = e.date.format('DD/MM/YYYY');
                    el_to.data('DateTimePicker').minDate(e.date);
                } else if (el_fr.data('date') === "") {
                    vm.filterDateFromPicker = "";
                }
            });
        },
        attachToDatePicker: function(){
            let vm = this;
            let el_fr = $(vm.$refs.issueDateFromPicker);
            let el_to = $(vm.$refs.issueDateToPicker);
            el_to.datetimepicker({ format: 'DD/MM/YYYY', maxDate: 'now', showClear: true });
            el_to.on('dp.change', function (e) {
                if (el_to.data('DateTimePicker').date()) {
                    vm.filterDateToPicker = e.date.format('DD/MM/YYYY');
                    el_fr.data('DateTimePicker').maxDate(e.date);
                } else if (el_to.data('date') === "") {
                    vm.filterDateToPicker = "";
                }
            });
        },
        constructOptionsType: async function() {
            let returned = await cache_helper.getSetCacheList('SanctionOutcomeTypes', '/api/sanction_outcome/types.json');
            Object.assign(this.sanction_outcome_types, returned);
            this.sanction_outcome_types.splice(0, 0, {id: 'all', display: 'All'});
        },
        constructOptionsStatus: async function() {
            let returned = await cache_helper.getSetCacheList('SanctionOutcomeStatuses', '/api/sanction_outcome/statuses.json');
            Object.assign(this.sanction_outcome_statuses, returned);
            this.sanction_outcome_statuses.splice(0, 0, {id: 'all', display: 'All'});
        },
        constructOptionsPaymentStatus: async function() {

        },
        constructOptionsRegion: async function() {
            console.log('constructOptionsRegion()')
            let returned_regions = await cache_helper.getSetCacheList(
                "CallEmail_Regions",
                "/api/region_district/get_regions/"
            );
            Object.assign(this.sanction_outcome_regions, returned_regions);
            this.sanction_outcome_regions.splice(0, 0, {
                id: "all",
                display_name: "All",
                district: "",
                districts: [],
                region: null
            });
        },
        constructOptionsDistrict: async function() {
            console.log('constructOptionsDistrict()')
            let returned_region_districts = await cache_helper.getSetCacheList(
                "CallEmail_RegionDistricts",
                api_endpoints.region_district
            );
            Object.assign(this.sanction_outcome_regionDistricts, returned_region_districts);
            console.log(this.sanction_outcome_regionDistricts);
            this.updateDistricts();
        },
    },
    components: {
        datatable,
        FormSection,
    },
}

</script>

<style>

</style>
