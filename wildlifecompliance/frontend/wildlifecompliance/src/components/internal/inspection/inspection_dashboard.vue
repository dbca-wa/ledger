<template>
    <div class="container" id="internalInspectionDash">
        <FormSection :label="`Inspection`" :Index="`0`">

        <form class="form-horizontal" name="createForm" method="get">
            <div class="row">
                <div class="col-md-3">
                        <label for="">Type</label>
                        <select class="form-control" v-model="filterInspectionType">
                            <option v-for="option in inspectionTypes" :value="option.description" v-bind:key="option.id">
                                {{ option.description }} 
                            </option>
                    </select>
                </div>
                <div class="col-md-3">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterStatus">
                            <option v-for="option in statusChoices" :value="option.display" v-bind:key="option.id">
                                {{ option.display }}
                            </option>
                        </select>
                </div>

            </div>
            <div class="row">
                <div class="col-md-3">
                    <label for="">Planned From</label>
                    <div class="input-group date" ref="plannedDateFromPicker">
                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterPlannedFrom">
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                    </div>
                </div>
                <div class="col-md-3">
                    <label for="">Planned To</label>
                    <div class="input-group date" ref="plannedDateToPicker">
                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterPlannedTo">
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                    </div>
                </div>
                <div class="col-md-3 pull-right">
                    <button @click.prevent="createInspection"
                        class="btn btn-primary pull-right">New Inspection</button>
                </div>    
            </div>
            
        </form>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="inspection_table" id="inspection-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
            </div>
        </div>
        </FormSection>
        <div v-if="inspectionInitialised">
            <CreateInspectionModal ref="add_inspection"  />
        </div>

    </div>
</template>
<script>
    import $ from 'jquery'
    import datatable from '@vue-utils/datatable.vue'
    import Vue from 'vue'
    import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
    import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
    import FormSection from "@/components/compliance_forms/section.vue";
    import CreateInspectionModal from "./create_inspection_modal.vue";
    
    // import moment from 'moment';
    // import 'bootstrap/dist/css/bootstrap.css';
    // import 'eonasdan-bootstrap-datetimepicker';
    
    export default {
        name: 'InspectionTableDash',
        data() {
            let vm = this;
            return {
                classification_types: [],
                // classificationChoices: [],
                report_types: [],
                // Filters
                filterStatus: 'All',
                filterInspectionType: 'All',
                filterTeamLead: 'All',

                filterPlannedFrom: '',
                filterPlannedTo: '',
                // statusChoices: [],
                statusChoices: [],
                inspectionTypes: [],
                
                dateFormat: 'DD/MM/YYYY',
                inspectionInitialised: false,
                // datepickerOptions: {
                //     format: 'DD/MM/YYYY',
                //     showClear: true,
                //     useCurrent: false,
                //     keepInvalid: true,
                //     allowInputToggle: true
                // },
                dtOptions: {
                    serverSide: true,
                    searchDelay: 1000,
                    lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                    order: [
                        [0, 'desc']
                    ],
                    autoWidth: false,
                    rowCallback: function (row, data) {
                        $(row).addClass('appRecordRow');
                    },


                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },

                    responsive: true,
                    processing: true,
                    ajax: {
                        'url': '/api/inspection_paginated/get_paginated_datatable/?format=datatables',
                        //'url': '/api/inspection/datatable_list',
                        //'dataSrc': '',
                        'dataSrc': 'data',
                        'data': function(d) {
                            d.status_description = vm.filterStatus;
                            d.inspection_description = vm.filterInspectionType;
                            d.date_from = vm.filterPlannedFrom != '' && vm.filterPlannedFrom != null ? moment(vm.filterPlannedFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                            d.date_to = vm.filterPlannedTo != '' && vm.filterPlannedTo != null ? moment(vm.filterPlannedTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        }
                    },
                    columns: [
                        {
                            data: 'number',
                            searchable: false,
                            //orderable: false
                        },
                        {
                            data: 'title',
                            searchable: false,
                            orderable: true
                        },
                        {
                            data: 'inspection_type',
                            searchable: false,
                            orderable: true,
                            mRender: function (data, type, full) {
                                if (data) {
                                    return data.description;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            data: 'status.name',
                            searchable: false,
                            orderable: true
                        },
                        {
                            data: 'planned_for',
                            searchable: false,
                            orderable: true
                        },
                        {
                            data: 'inspection_team_lead',
                            searchable: false,
                            orderable: true,
                            mRender: function (data, type, full) {
                                if (data) {
                                    return data.full_name;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            data: 'user_action',
                            searchable: false,
                            orderable: false
                        },
                    ],
                },
                dtHeaders: [
                    'Number',
                    'Title',
                    'Inspection Type',
                    'Status',
                    'Planned for',
                    'Team Lead',
                    'Action',
                ],
            }
        },

        beforeRouteEnter: function(to, from, next) {
            next(async (vm) => {
                // await vm.loadCurrentUser({ url: `/api/my_compliance_user_details` });
                // await this.datatablePermissionsToggle();
            });
        },
        
        created: async function() {
            // Status choices
            let returned_status_choices = await cache_helper.getSetCacheList(
                'Inspection_StatusChoices', 
                '/api/call_email/status_choices'
                );
            
            Object.assign(this.statusChoices, returned_status_choices);
            this.statusChoices.splice(0, 0, {id: 'all', display: 'All'});

            // inspection_types
            let returned_inspection_types = await cache_helper.getSetCacheList(
                'CallEmail_InspectionTypes', 
                api_endpoints.inspection_types
                );
            Object.assign(this.inspectionTypes, returned_inspection_types);
            // blank entry allows user to clear selection
            this.inspectionTypes.splice(0, 0, 
                {
                id: "all",
                description: "All",
                });

        },
        watch: {
            filterStatus: function () {
                this.$refs.inspection_table.vmDataTable.draw();
            },
            filterInspectionType: function () {
                this.$refs.inspection_table.vmDataTable.draw();
            },
            filterTeamLead: function () {
                this.$refs.inspection_table.vmDataTable.draw();
            },
            filterPlannedFrom: function () {
                this.$refs.inspection_table.vmDataTable.draw();
            },
            filterPlannedTo: function () {
                this.$refs.inspection_table.vmDataTable.draw();
            },
        },
        components: {
            datatable,
            FormSection,
            CreateInspectionModal,
        },
        computed: {
        },
        methods: {
            ...mapActions('inspectionStore', {
                saveInspection: "saveInspection",
            }),
            createInspection: function() {
                this.inspectionInitialised = true;
                this.$nextTick(() => {
                    this.$refs.add_inspection.isModalOpen = true;
                });
            },
            
            createInspectionUrl: async function () {
                const newInspectionId = await this.saveInspection({ route: false, crud: 'create'});
                
                this.$router.push({
                    name: 'view-inspection', 
                    params: { inspection_id: newInspectionId}
                    });
            },
            addEventListeners: function () {
                let vm = this;
                // Initialise Planned Date Filters
                $(vm.$refs.plannedDateToPicker).datetimepicker(vm.datepickerOptions);
                $(vm.$refs.plannedDateToPicker).on('dp.change', function (e) {
                    if ($(vm.$refs.plannedDateToPicker).data('DateTimePicker').date()) {
                        vm.filterPlannedTo = e.date.format('DD/MM/YYYY');
                    } else if ($(vm.$refs.plannedDateToPicker).data('date') === "") {
                        vm.filterLodgedTo = "";
                    }
                });
                $(vm.$refs.plannedDateFromPicker).datetimepicker(vm.datepickerOptions);
                $(vm.$refs.plannedDateFromPicker).on('dp.change', function (e) {
                    if ($(vm.$refs.plannedDateFromPicker).data('DateTimePicker').date()) {
                        vm.filterPlannedFrom = e.date.format('DD/MM/YYYY');
                    } else if ($(vm.$refs.plannedDateFromPicker).data('date') === "") {
                        vm.filterPlannedFrom = "";
                    }
                });
            },
            initialiseSearch: function () {
                this.dateSearch();
            },
            dateSearch: function () {
                let vm = this;
                vm.$refs.inspection_table.table.dataTableExt.afnFiltering.push(
                    function (settings, data, dataIndex, original) {
                        let from = vm.filterPlannedFrom;
                        let to = vm.filterPlannedTo;
                        let val = original.planned_for_date;

                        if (from == '' && to == '') {
                            return true;
                        } else if (from != '' && to != '') {
                            return val != null && val != '' ? moment().range(moment(from, vm.dateFormat),
                                moment(to, vm.dateFormat)).contains(moment(val)) : false;
                        } else if (from == '' && to != '') {
                            if (val != null && val != '') {
                                return moment(to, vm.dateFormat).diff(moment(val)) >= 0 ? true : false;
                            } else {
                                return false;
                            }
                        } else if (to == '' && from != '') {
                            if (val != null && val != '') {
                                return moment(val).diff(moment(from, vm.dateFormat)) >= 0 ? true : false;
                            } else {
                                return false;
                            }
                        } else {
                            return false;
                        }
                    }
                );
            },
        },
        mounted: async function () {
            let vm = this;
            $('a[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                }, 100);
            });
            this.$nextTick(async () => {
                await vm.initialiseSearch();
                await vm.addEventListeners();
            });
            
            
        }
    }
</script>
