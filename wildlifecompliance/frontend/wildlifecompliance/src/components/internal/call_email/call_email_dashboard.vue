<template>
    <div class="container" id="internalCallEmailDash">
        <FormSection :label="`Call/Emails`" :Index="`0`">
                  
              
        <form class="form-horizontal" name="createForm" method="get">
            <div class="row">
                <div class="col-md-3">
                        <label for="">Call/Email Status</label>
                        <select class="form-control" v-model="filterStatus">
                            <option v-for="option in status_choices" :value="option.display" v-bind:key="option.id">
                                {{ option.display }}
                            </option>
                        </select>
                </div>
                <div class="col-md-3">
                        <label for="">Call/Email Classification</label>
                        <select class="form-control" v-model="filterClassification">
                            <option v-for="option in classification_types" :value="option.name" v-bind:key="option.id">
                                {{ option.name }} 
                            </option>
                    </select>
                </div>
            </div>
            <div class="row">
                <div class="col-md-3">
                    <label for="">Lodged From</label>
                    <div class="input-group date" ref="lodgementDateFromPicker">
                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterLodgedFrom">
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                    </div>
                </div>
                <div class="col-md-3">
                    <label for="">Lodged To</label>
                    <div class="input-group date" ref="lodgementDateToPicker">
                        <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterLodgedTo">
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                    </div>
                </div>
                <div v-if="current_user && current_user.is_volunteer" class="col-md-3 pull-right">
                    <button @click.prevent="createCallEmailUrl"
                        class="btn btn-primary pull-right">New Call/Email</button>
                </div>    
            </div>
            
        </form>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="call_email_table" id="call-email-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
            </div>
        </div>
        </FormSection>

        <FormSection :label="`Location`" :Index="`1`">
            <MapLocations />
        </FormSection>
    </div>
</template>
<script>
    import $ from 'jquery'
    import datatable from '@vue-utils/datatable.vue'
    import MapLocations from "./map_locations.vue";
    import Vue from 'vue'
    import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
    import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
    import FormSection from "@/components/compliance_forms/section.vue";
    export default {
        name: 'CallEmailDashTable',
        data() {
            let vm = this;
            return {
                classification_types: [],
                // classificationChoices: [],
                report_types: [],
                // Filters
                filterStatus: 'All',
                filterClassification: 'All',
                // statusChoices: [],
                status_choices: [],
                filterLodgedFrom: '',
                filterLodgedTo: '',
                dateFormat: 'DD/MM/YYYY',
                datepickerOptions: {
                    format: 'DD/MM/YYYY',
                    showClear: true,
                    useCurrent: false,
                    keepInvalid: true,
                    allowInputToggle: true
                },
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
                        //"url": helpers.add_endpoint_json(api_endpoints.call_email, 'datatable_list'),
                        //"url": helpers.add_endpoint_json(api_endpoints.call_email_paginated, 'get_paginated_datatable'),
                        "url": "/api/call_email_paginated/get_paginated_datatable/?format=datatables",
                        "dataSrc": 'data',
                        "data": function(d) {
                            d.status_description = vm.filterStatus;
                            d.classification_description = vm.filterClassification;
                            d.date_from = vm.filterLodgedFrom != '' && vm.filterLodgedFrom != null ? moment(vm.filterLodgedFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                            d.date_to = vm.filterLodgedTo != '' && vm.filterLodgedTo != null ? moment(vm.filterLodgedTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        }
                    },
                    columns: [
                        {
                            data: "number",
                            searchable: false,
                            //orderable: true,
                        },
                        {
                            data: "status.name",
                            searchable: false,
                            orderable: false,
                        },
                        {
                            data: "classification",
                            searchable: false,
                            //orderable: false,
                            mRender: function (data, type, full) {
                                if (data) {
                                    return data.name;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            data: "lodged_on",
                            searchable: false,
                            //orderable: false,
                            mRender: function (data, type, full) {
                                return data != '' && data != null ? moment(data).format(vm.dateFormat) : '';
                            }
                        },
                        
                        {
                            data: "caller",
                            searchable: false,
                        },
                        {
                            data: "assigned_to",
                            searchable: false,
                            orderable: false,
                            mRender: function (data, type, full) {
                                if (data) {
                                    return data.full_name;
                                } else {
                                    return '';
                                }
                            }
                        },
                        // {
                        //     mRender: function (data, type, full) {
                        //         return `<a href="/internal/call_email/${full.id}">View</a>`
                        //     }
                        // }
                        {
                        // Actions
                            //width: "10%",
                            //mRender: function(data,type,full) {
                              //  let links = '';
                                //    links += full.user_is_assignee ? 
                                  //      `<a href="/internal/call_email/${full.id}">Process</a>` :
                                    //    `<a href="/internal/call_email/${full.id}">View</a>`;
                                //return links;
                            //},
                            //orderable: false,
                            //searchable: false
                            data: "user_action",
                            searchable: false,
                            orderable: false,
                        }
                    ],
                },
                dtHeaders: [
                    "Number",
                    "Status",
                    "Classification",
                    "Lodged on",
                    "Caller",
                    "Assigned to",
                    "Action",
                ],
            }
        },

        beforeRouteEnter: function(to, from, next) {
            next(async (vm) => {
                await vm.loadCurrentUser({ url: `/api/my_compliance_user_details` });
                // await this.datatablePermissionsToggle();
            });
        },
        
        created: async function() {
            
            let returned_classification_types = await cache_helper.getSetCacheList('CallEmail_ClassificationTypes', '/api/classification.json');
            console.log('classification types');
            console.log(returned_classification_types);
            Object.assign(this.classification_types, returned_classification_types);
            console.log(this.classification_types);
            this.classification_types.splice(0, 0, {id: 'all', name: 'All'});

            let returned_status_choices = await cache_helper.getSetCacheList('CallEmail_StatusChoices', '/api/call_email/status_choices');
            console.log('returned_status_choices');
            console.log(returned_status_choices);
            Object.assign(this.status_choices, returned_status_choices);
            console.log(this.status_choices);
            this.status_choices.splice(0, 0, {id: 'all', display: 'All'});

        },
        watch: {
            filterStatus: function () {
                this.$refs.call_email_table.vmDataTable.draw();
            },
            filterClassification: function () {
                this.$refs.call_email_table.vmDataTable.draw();
            },
            filterLodgedFrom: function () {
                this.$refs.call_email_table.vmDataTable.draw();
            },
            filterLodgedTo: function () {
                this.$refs.call_email_table.vmDataTable.draw();
            },
        },
        components: {
            datatable,
            FormSection,
            MapLocations,
        },
        computed: {
            ...mapGetters('callemailStore', {
            }),
            ...mapGetters({
                current_user: 'current_user',
            }),
            
        },
        methods: {
            ...mapActions('callemailStore', {
                saveCallEmail: "saveCallEmail",
            }),
            ...mapActions({
                loadCurrentUser: "loadCurrentUser",
                // userhasComplianceRole: "hasComplianceRole",
            }),
            // datatablePermissionsToggle: function() {
            //     return this.current_user.base_compliance_permissions.includes('officer');
            // },
            createCallEmailUrl: async function () {
                const newCallId = await this.saveCallEmail({ route: false, crud: 'create'});
                console.log("newCallId");
                console.log(newCallId);

                this.$router.push({
                    name: 'view-call-email', 
                    params: {call_email_id: newCallId}
                    });
            },
            addEventListeners: function () {
                let vm = this;
                // Initialise Application Date Filters
                $(vm.$refs.lodgementDateToPicker).datetimepicker(vm.datepickerOptions);
                $(vm.$refs.lodgementDateToPicker).on('dp.change', function (e) {
                    if ($(vm.$refs.lodgementDateToPicker).data('DateTimePicker').date()) {
                        vm.filterLodgedTo = e.date.format('DD/MM/YYYY');
                    } else if ($(vm.$refs.lodgementDateToPicker).data('date') === "") {
                        vm.filterLodgedTo = "";
                    }
                });
                $(vm.$refs.lodgementDateFromPicker).datetimepicker(vm.datepickerOptions);
                $(vm.$refs.lodgementDateFromPicker).on('dp.change', function (e) {
                    if ($(vm.$refs.lodgementDateFromPicker).data('DateTimePicker').date()) {
                        vm.filterLodgedFrom = e.date.format('DD/MM/YYYY');
                    } else if ($(vm.$refs.lodgementDateFromPicker).data('date') === "") {
                        vm.filterLodgedFrom = "";
                    }
                });
            },
            initialiseSearch: function () {
                this.dateSearch();
            },
            dateSearch: function () {
                let vm = this;
                vm.$refs.call_email_table.table.dataTableExt.afnFiltering.push(
                    function (settings, data, dataIndex, original) {
                        let from = vm.filterLodgedFrom;
                        let to = vm.filterLodgedTo;
                        let val = original.lodgement_date;

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
