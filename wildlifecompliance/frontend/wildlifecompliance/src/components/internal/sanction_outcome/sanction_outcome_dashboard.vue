<template>
    <div class="container" id="internalInspectionDash">
        <FormSection :label="`Sanction Outcome`" :Index="`0`">
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
export default {
    name: 'SanctionOutcomeTableDash',
    data() {
        let vm = this;
        return {
            dtOptions: {
                serverSide: true,
                searchDelay: 1000,
                lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                order: [
                    [0, 'desc']
                ],
                //autoWidth: false,
                // rowCallback: function (row, data) {
                //     $(row).addClass('appRecordRow');
                // },

                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },

                responsive: true,
                processing: true,
                ajax: {
                    // url: '/api/sanction_outcome/datatable_list',
                    url: '/api/sanction_outcome_paginated/get_paginated_datatable/?format=datatables',
                    // dataSrc: 'tableData'
                    dataSrc: 'data',
                    data: function(d) {
                        console.log('data to be sent');
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
                        orderable: false
                    },
                    {
                        data: 'offender',
                        searchable: true,
                        orderable: false
                    },
                    {
                        data: 'status.name',
                        searchable: true,
                        orderable: false,
                    },
                    {
                        mRender: function (data, type, row){
                            return 'Not implemented';
                        },
                        searchable: true,
                        orderable: false
                    },
                    {
                        mRender: function (data, type, row){
                            return 'Not implemented';
                        },
                        searchable: true,
                        orderable: false
                    },
                    {
                        // mRender: function (data, type, row){
                        //     return 'Not implemented';
                        // }
                        data: 'user_action',
                        searchable: false,
                        orderable: false,
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
    components: {
        datatable,
        FormSection,
    },
}

</script>

<style>

</style>
