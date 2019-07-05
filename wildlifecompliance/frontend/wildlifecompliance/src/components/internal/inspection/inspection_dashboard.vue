<template>
    <div class="container" id="internalInspectionDash">
        <FormSection :label="`Inspection`" :Index="`0`">

        <form class="form-horizontal" name="createForm" method="get">
            <!-- <div class="row">
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
            </div> -->
            <div class="row">
                <!-- <div class="col-md-3">
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
                </div> -->
                <div class="col-md-3 pull-right">
                    <button @click.prevent="createInspectionUrl"
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

    </div>
</template>
<script>
    import $ from 'jquery'
    import datatable from '@vue-utils/datatable.vue'
    import Vue from 'vue'
    import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
    import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
    import FormSection from "@/components/compliance_forms/section.vue";
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
                filterClassification: 'All',
                // statusChoices: [],
                status_choices: [],
                filterLodgedFrom: '',
                filterLodgedTo: '',
                dateFormat: 'DD/MM/YYYY',
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
                        
                        "url": "/api/inspection/datatable_list",
                        "dataSrc": '',
                    },
                    columns: [
                        {
                            data: "number",
                            //searchable: false,
                        },
                        {
                            data: "title",
                            //searchable: false,
                        },
                        {
                            data: "details",
                            //searchable: false,  
                        },
                    ],
                },
                dtHeaders: [
                    "Number",
                    "Title",
                    "Details",
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

        },
        watch: {
            // filterStatus: function () {
            //     this.$refs.call_email_table.vmDataTable.draw();
            // },
            // filterClassification: function () {
            //     this.$refs.call_email_table.vmDataTable.draw();
            // },
            // filterLodgedFrom: function () {
            //     this.$refs.call_email_table.vmDataTable.draw();
            // },
            // filterLodgedTo: function () {
            //     this.$refs.call_email_table.vmDataTable.draw();
            // },
        },
        components: {
            datatable,
            FormSection,
        },
        computed: {
        },
        methods: {
            ...mapActions('inspectionStore', {
                saveInspection: "saveInspection",
            }),
            
            createInspectionUrl: async function () {
                const newInspectionId = await this.saveInspection({ route: false, crud: 'create'});
                
                this.$router.push({
                    name: 'view-inspection', 
                    params: { inspection_id: newInspectionId}
                    });
            },
            // addEventListeners: function () {
            //     let vm = this;
            //     // Initialise Application Date Filters
            //     $(vm.$refs.lodgementDateToPicker).datetimepicker(vm.datepickerOptions);
            //     $(vm.$refs.lodgementDateToPicker).on('dp.change', function (e) {
            //         if ($(vm.$refs.lodgementDateToPicker).data('DateTimePicker').date()) {
            //             vm.filterLodgedTo = e.date.format('DD/MM/YYYY');
            //         } else if ($(vm.$refs.lodgementDateToPicker).data('date') === "") {
            //             vm.filterLodgedTo = "";
            //         }
            //     });
            //     $(vm.$refs.lodgementDateFromPicker).datetimepicker(vm.datepickerOptions);
            //     $(vm.$refs.lodgementDateFromPicker).on('dp.change', function (e) {
            //         if ($(vm.$refs.lodgementDateFromPicker).data('DateTimePicker').date()) {
            //             vm.filterLodgedFrom = e.date.format('DD/MM/YYYY');
            //         } else if ($(vm.$refs.lodgementDateFromPicker).data('date') === "") {
            //             vm.filterLodgedFrom = "";
            //         }
            //     });
            // },
            initialiseSearch: function () {
                //this.dateSearch();
            },
            // dateSearch: function () {
            //     let vm = this;
            //     vm.$refs.call_email_table.table.dataTableExt.afnFiltering.push(
            //         function (settings, data, dataIndex, original) {
            //             let from = vm.filterLodgedFrom;
            //             let to = vm.filterLodgedTo;
            //             let val = original.lodgement_date;

            //             if (from == '' && to == '') {
            //                 return true;
            //             } else if (from != '' && to != '') {
            //                 return val != null && val != '' ? moment().range(moment(from, vm.dateFormat),
            //                     moment(to, vm.dateFormat)).contains(moment(val)) : false;
            //             } else if (from == '' && to != '') {
            //                 if (val != null && val != '') {
            //                     return moment(to, vm.dateFormat).diff(moment(val)) >= 0 ? true : false;
            //                 } else {
            //                     return false;
            //                 }
            //             } else if (to == '' && from != '') {
            //                 if (val != null && val != '') {
            //                     return moment(val).diff(moment(from, vm.dateFormat)) >= 0 ? true : false;
            //                 } else {
            //                     return false;
            //                 }
            //             } else {
            //                 return false;
            //             }
            //         }
            //     );
            // },
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
                // await vm.addEventListeners();
            });
            
            
        }
    }
</script>
