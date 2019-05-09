<template>
    <div class="container" id="internalCallEmailDash">
        <FormSection :label="`Call/Emails`" :Index="`0`">
                  
              
        <form class="form-horizontal" name="createForm" method="get">
            <div class="row">
                <div class="col-md-3">
                        <label for="">Call/Email Status</label>
                        <select class="form-control" v-model="filterStatus">
                            <option value="All">All</option>
                            <option v-for="c in statusChoices" :value="c">{{ c }}</option>
                        </select>
                </div>
                <div class="col-md-3">
                        <label for="">Call/Email Classification</label>
                        <select class="form-control" v-model="filterClassification">
                        <option value="All">All</option>
                        <option v-for="option in classification_types" :value="option.name" v-bind:key="option.name">
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
                <div class="col-md-3 pull-right">
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
    import {
        api_endpoints,
        helpers
    }
    from '@/utils/hooks'
    import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
    import FormSection from "@/components/compliance_forms/section.vue";
    export default {
        name: 'CallEmailTableDash',
        data() {
            let vm = this;
            return {
                // Filters
                filterStatus: 'All',
                filterClassification: 'All',
                //filterLodgmentDate: null,
                statusChoices: [],
                classificationChoices: [],
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

                    language: {
                        processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                    },

                    responsive: true,
                    processing: true,
                    ajax: {
                        "url": helpers.add_endpoint_json(api_endpoints.call_email, 'datatable_list'),
                        "dataSrc": '',
                    },
                    columns: [
                        {
                            data: "id",
                        },
                        {
                            data: "status",
                        },
                        {
                            data: "classification",
                            mRender: function (data, type, full) {
                                if (data) {
                                    return data.name;
                                } else {
                                    return '';
                                }
                            }
                        },
                        {
                            data: "lodgement_date",
                            mRender: function (data, type, full) {
                                return data != '' && data != null ? moment(data).format(vm.dateFormat) : '';
                            }
                        },
                        {
                            data: "number",
                        },
                        {
                            data: "caller",
                        },
                        {
                            data: "assigned_to",
                        },
                        {
                            mRender: function (data, type, full) {
                                return `<a href="/internal/call_email/${full.id}">View</a>`
                            }
                        }
                    ],

                    initComplete: function () {
                        var callColumn = vm.$refs.call_email_table.vmDataTable.columns(1);
                        callColumn.data().unique().sort().each(function (d, j) {
                            let status_choices = [];
                            $.each(d, (index, a) => {
                                a != null && status_choices.indexOf(a) < 0 ? status_choices.push(a) :
                                '';
                            })
                            vm.statusChoices = status_choices;
                        });
                        var classificationColumn = vm.$refs.call_email_table.vmDataTable.columns(2);
                        classificationColumn.data().unique().sort().each(function (d, j) {
                            let classification_choices = [];
                            $.each(d, (index, a) => {
                                a['name'] != null && classification_choices.indexOf(a['name']) < 0 ?
                                    classification_choices.push(a['name']) : '';
                            })
                            vm.classificationChoices = classification_choices;
                        });
                    }

                },
                dtHeaders: [
                    "Call/Email ID",
                    "Call/Email Status",
                    "Classification",
                    "lodgement_date",
                    "number",
                    "caller",
                    "assigned_to",
                    "Action",
                ],
            }
        },

        watch: {
            filterCall: function () {
                let vm = this;
                let regexSearch = helpers.datatableExactStringMatch(vm.filterStatus);
                if (vm.filterStatus != 'All') {
                    vm.$refs.call_email_table.vmDataTable.columns(1).search(regexSearch, true, false).draw();
                } else {
                    vm.$refs.call_email_table.vmDataTable.columns(1).search('').draw();
                }
            },
            filterClassification: function () {
                let vm = this;
                let regexSearch = helpers.datatableExactStringMatch(vm.filterClassification);
                if (vm.filterClassification != 'All') {
                    vm.$refs.call_email_table.vmDataTable.columns(2).search(regexSearch, true, false).draw();
                } else {
                    vm.$refs.call_email_table.vmDataTable.columns(2).search('').draw();
                }
            },
            filterLodgedFrom: function () {
                this.$refs.call_email_table.vmDataTable.draw();
            },
            filterLodgedTo: function () {
                this.$refs.call_email_table.vmDataTable.draw();
            },
        },

        created: function() {
            this.loadClassification();
            this.loadReportTypes();
        },
        components: {
            datatable,
            FormSection,
        },
        computed: {
            ...mapGetters('callemailStore', {
                classification_types: "classification_types",
                report_types: "report_types",
            }),
        },
        methods: {
            ...mapActions('callemailStore', {
                loadClassification: "loadClassification",
                loadReportTypes: "loadReportTypes",
            }),
            
            createCallEmailUrl: function () {
                this.$router.push({
                    name: 'new-call-email' 
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
                        //$(vm.$refs.lodgementDateToPicker).data("DateTimePicker").minDate(e.date);
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
            }
        },
        mounted: function () {
            let vm = this;
            $('a[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                }, 100);
            });
            this.$nextTick(() => {
                vm.initialiseSearch();
                vm.addEventListeners();
            });
        }


    }
</script>