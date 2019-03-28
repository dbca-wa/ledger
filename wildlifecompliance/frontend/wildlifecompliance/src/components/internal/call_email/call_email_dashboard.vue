<template>
    <div class="container" id="internalCallEmailDash">
        <form class="form-horizontal" name="createForm" method="get">
            <div class="row">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Call/Email status</label>
                        <select class="form-control" v-model="filterCall">
                            <option value="All">All</option>
                            <option v-for="c in callChoices" :value="c">{{ c }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Call/Email classification</label>
                        <select class="form-control" v-model="filterClassification">
                            <option value="All">All</option>
                            <option v-for="i in classificationChoices" :value="i">{{ i }}</option>
                        </select>
                    </div>
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
                <div class="col-sm-12">
                    <button @click.prevent="createCallEmailUrl"
                        class="btn btn-primary pull-right">New Call/Email</button>
                </div>
            </div>
        </form>
                
        <p></p>
        
        <div class="row">
            <div class="col-lg-12">
                <datatable ref="call_email_table" id="call-email-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders" />
            </div>
        </div>

    </div>
</template>
<script>
    import $ from 'jquery'
    import datatable from '@vue-utils/datatable.vue'
    import Vue from 'vue'
    import {
        api_endpoints,
        helpers
    }
    from '@/utils/hooks'
    export default {
        name: 'CallEmailTableDash',
        data() {
            let vm = this;
            return {
                // Filters
                filterCall: 'All',
                filterClassification: 'All',
                //filterLodgmentDate: null,
                callChoices: [],
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
                    columns: [{
                            data: "status",
                        },
                        {
                            data: "classification",
                            mRender: function (data, type, full) {
                                return data.name
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
                                return `<a href="http://www.google.com">link</a>`
                            }
                        }
                    ],

                    initComplete: function () {
                        var callColumn = vm.$refs.call_email_table.vmDataTable.columns(0);
                        //vm.bbVar = callColumn;
                        //console.log(vm.bbVar);
                        callColumn.data().unique().sort().each(function (d, j) {
                            let call_choices = [];
                            $.each(d, (index, a) => {
                                a != null && call_choices.indexOf(a) < 0 ? call_choices.push(a) :
                                '';
                            })
                            vm.callChoices = call_choices;
                            //console.log(vm.classificationChoices);
                        });
                        var classificationColumn = vm.$refs.call_email_table.vmDataTable.columns(1);
                        //vm.bbVar = classificationColumn.data().eq(2);
                        //console.log(vm.bbVar);
                        classificationColumn.data().unique().sort().each(function (d, j) {
                            let classification_choices = [];
                            $.each(d, (index, a) => {
                                a['name'] != null && classification_choices.indexOf(a['name']) < 0 ?
                                    classification_choices.push(a['name']) : '';
                            })
                            vm.classificationChoices = classification_choices;
                            //console.log(vm.classificationChoices);
                        });
                    }

                },
                dtHeaders: [
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

                if (vm.filterCall != 'All') {
                    vm.$refs.call_email_table.vmDataTable.columns(0).search(vm.filterCall, false).draw();
                } else {
                    vm.$refs.call_email_table.vmDataTable.columns(0).search('').draw();
                }
            },
            filterClassification: function () {
                let vm = this;
                if (vm.filterClassification != 'All') {
                    vm.$refs.call_email_table.vmDataTable.columns(1).search(vm.filterClassification, false).draw();
                } else {
                    vm.$refs.call_email_table.vmDataTable.columns(1).search('').draw();
                }
            },
            filterLodgedFrom: function () {
                this.$refs.call_email_table.vmDataTable.draw();
            },
            filterLodgedTo: function () {
                this.$refs.call_email_table.vmDataTable.draw();
            },
        },
        beforeRouteEnter: function (to, from, next) {
            console.log('BEFORE-ROUTE func()')
            //Vue.http.get(`/api/returns/${to.params.return_id}.json`).then(res => {
            Vue.http.get(`/api/call_email/datatable_list.json`).then(res => {
                next(vm => {
                    vm.table = res.body;
                    console.log(vm);
                    console.log(vm.table);
                });
            }, err => {
                console.log(err);
            });
        },
        components: {
            datatable
        },
        computed: {
            isLoading: function () {
                return this.loading.length == 0;
            },
            
        },
        methods: {
            createCallEmailUrl: function () {
                //return `<a href="/api/call_email/create_call_email"/>`;
                this.$router.push({
                    //name: 'external-proposals-dash'
                    name: 'internal-create-call-email' // defined in ../src/components/internal/routes/index.js
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