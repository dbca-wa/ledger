<template>
    <div class="container" id="internalInspectionDash">
        <FormSection :label="`Sanction Outcome`" :Index="`0`">
        <div class="row">
            <div class="col-md-3">
                <label class="">Type:</label>
                <select class="form-control" v-model="filterSanctionOutcomeType">
                    <option v-for="option in sanction_outcome_types" :value="option.id" v-bind:key="option.id">
                        {{ option.display }}
                    </option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="">Status:</label>
            </div>
            <div class="col-md-3">
                <label class="">Payment status:</label>
            </div>
        </div>
        <div class="row">
            <div class="col-md-3">
                <label class="">Issue date from:</label>
            </div>
            <div class="col-md-3">
                <label class="">Issue date to:</label>
            </div>
        </div>
        <div class="row">
            <div class="col-md-3">
                <label class="">Region:</label>
            </div>
            <div class="col-md-3">
                <label class="">District:</label>
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
            filterSanctionOutcomeType: 'all',

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
                        console.log('data to be sent');
                        d.sanction_outcome_type = vm.filterSanctionOutcomeType;
                        console.log(d);
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
                        orderable: true
                    },
                    {
                        data: 'identifier',
                        searchable: true,
                        orderable: true
                    },
                    {
                        data: 'date_of_issue',
                        searchable: true,
                        orderable: true
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
                            return 'Not implemented';
                        }
                    },
                    {
                        searchable: true,
                        orderable: false,
                        mRender: function (data, type, row){
                            return 'Not implemented';
                        }
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
                'Offender',
                'Status',
                'Payment Status',
                'Sanction Outcome',
                'Action',
            ],
        }
    },
    created: async function() {
        let returned_types = await cache_helper.getSetCacheList('SanctionOutcomeTypes', '/api/sanction_outcome/types.json');
        Object.assign(this.sanction_outcome_types, returned_types);
        this.sanction_outcome_types.splice(0, 0, {id: 'all', display: 'All'});
    },
    components: {
        datatable,
        FormSection,
    },
}

</script>

<style>

</style>
