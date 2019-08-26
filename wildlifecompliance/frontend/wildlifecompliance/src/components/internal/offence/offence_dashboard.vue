<template>
    <div class="container" id="internalOffenceDash">
        <FormSection :label="`Offence`" :Index="`0`">

        <div class="row">
            <div class="col-md-3">
                <label class="">Type:</label>
                <select class="form-control" v-model="filterType">
                    <option v-for="option in offence_types" :value="option.id" v-bind:key="option.id">
                        {{ option.display }}
                    </option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="">Status:</label>
                <select class="form-control" v-model="filterStatus">
                    <option v-for="option in offence_statuses" :value="option.id" v-bind:key="option.id">
                        {{ option.display }}
                    </option>
                </select>
            </div>
        </div>
        <div class="row">
            <div class="col-md-3">
                <label class="">Date from:</label>
                <div class="input-group date" ref="issueDateFromPicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateFromPicker" />
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
            <div class="col-md-3">
                <label class="">Date to:</label>
                <div class="input-group date" ref="issueDateToPicker">
                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateToPicker" />
                    <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                    </span>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="offence_table" id="offence-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
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
    name: 'OffenceTableDash',
    data() {
        let vm = this;
        return {
            offence_types: [],
            offence_statuses: [],

            filterType: 'all',
            filterStatus: 'all',
            filterDateFromPicker: '',
            filterDateToPicker: '',

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
                    url: '/api/offence_paginated/get_paginated_datatable/?format=datatables',
                    dataSrc: 'data',
                    data: function(d) {
                        d.type = vm.filterType;
                        d.status = vm.filterStatus;
                        d.date_from = vm.filterDateFromPicker;
                        d.date_to = vm.filterDateToPicker;
                    }
                },
                columns: [
                    {
                        data: 'lodgement_number',
                        searchable: true,
                        orderable: true,
                    },
                    {
                        data: 'alleged_offences',
                        searchable: false,
                        orderable: true,
                        mRender: function (data, type, row){
                            let ret = '';
                            for (let i=0; i<data.length; i++){
                                ret = ret + data[i].act + ', ' + data[i].name + '<br />';
                            }
                            return ret;
                        }
                    },
                    {
                        data: 'identifier',
                        searchable: true,
                        orderable: true
                    },
                    {
                        data: 'occurrence_date_from',
                        searchable: true,
                        orderable: true
                    },
                    {
                        data: 'offenders',
                        searchable: true,
                        orderable: true,
                        mRender: function (data, type, row){
                            console.log('offenders:');
                            console.log(data);
                            let ret = '';
                            for (let i=0; i<data.length; i++){
                                let name = '';
                                let num_chars = 30;
                                if (data && data[i].person){
                                    name = data[i].person.first_name + ' ' + data[i].person.last_name;
                                } else if (data[i] && data[i].organisation) {
                                    name = data[i].organisation.name;
                                }

                                let temp = (name.length > num_chars) ?
                                    '<span title="' + name + '">' + $.trim(name).substring(0, num_chars).split(" ").slice(0, -1).join(" ") + '...</span>' :
                                    name;
                                ret = ret + temp + '<br />';
                            }
                            return ret;
                        }
                    },
                    {
                        data: 'status.name',
                        searchable: true,
                        orderable: true,
                    },
                    {
                        data: 'user_action',
                        searchable: false,
                        orderable: true,
                        mRender: function (data, type, row){
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
                'Offender(s)',
                'Status',
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
            this.$refs.offence_table.vmDataTable.draw();
        },
        filterStatus: function () {
            this.$refs.offence_table.vmDataTable.draw();
        },
        filterPaymentStatus: function () {
            this.$refs.offence_table.vmDataTable.draw();
        },
        filterDateFromPicker: function () {
            this.$refs.offence_table.vmDataTable.draw();
        },
        filterDateToPicker: function () {
            this.$refs.offence_table.vmDataTable.draw();
        },
        filterRegionId: function () {
            this.$refs.offence_table.vmDataTable.draw();
        },
        filterDistrictId: function () {
            this.$refs.offence_table.vmDataTable.draw();
        },
    },
    created: async function() {
        this.constructOptionsType();
        this.constructOptionsStatus();
    },
    methods: {
        // updateDistricts: function(updateFromUI) {
        //     console.log('updateDistricts');
        //     // if (updateFromUI) {
        //     //     // We don't want to clear the default district selection when initially loaded, which derived from the call_email
        //     //     this.offence.district_id = null;
        //     // }
        //     this.offence_availableDistricts = []; // This is a list of options for district
        //     for (let record of this.offence_regionDistricts) {
        //         if (this.filterRegionId == record.id) {
        //             for (let district_id of record.districts) {
        //                 for (let district_record of this.sanction_outcome_regionDistricts) {
        //                     if (district_record.id == district_id) {
        //                         this.sanction_outcome_availableDistricts.push(district_record);
        //                     }
        //                 }
        //             }
        //         }
        //     }

        //     this.sanction_outcome_availableDistricts.splice(0, 0, {
        //         id: "all",
        //         display_name: "All",
        //         district: "",
        //         districts: [],
        //         region: null
        //     });

        //     this.filterDistrictId = 'all';
        // },
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
            let returned = await cache_helper.getSetCacheList('OffenceTypes', '/api/offence/types.json');
            Object.assign(this.offence_types, returned);
            this.offence_types.splice(0, 0, {id: 'all', display: 'All'});
        },
        constructOptionsStatus: async function() {
            let returned = await cache_helper.getSetCacheList('OffenceStatuses', '/api/offence/statuses.json');
            Object.assign(this.offence_statuses, returned);
            this.offence_statuses.splice(0, 0, {id: 'all', display: 'All'});
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
