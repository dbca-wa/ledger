<template id="application_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Applications <small v-if="is_external">View existing applications and lodge new ones</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Licence Type</label>
                                <select class="form-control" v-model="filterApplicationLicenceType">
                                    <option value="All">All</option>
                                    <option v-for="lt in application_licence_types" :value="lt" v-bind:key="`licence_type_${lt}`">{{lt}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterApplicationStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in application_status" :value="s" v-bind:key="`status_${s.id}`">{{s.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div v-if="is_external" class="col-md-3">
                            <router-link  style="margin-top:25px;" class="btn btn-primary pull-right" :to="{ name: 'apply_application' }">New Application</router-link>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Lodged From</label>
                            <div class="input-group date" ref="applicationDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterApplicationLodgedFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Lodged To</label>
                            <div class="input-group date" ref="applicationDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterApplicationLodgedTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Submitter</label>
                                <select class="form-control" v-model="filterApplicationSubmitter">
                                    <option value="All">All</option>
                                    <option v-for="s in application_submitters" :value="s.email" v-bind:key="`submitter_${s.email}`">{{s.search_term}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable v-if="level=='external'" ref="external_application_datatable" :id="datatable_id" :dtOptions="application_ex_options" :dtHeaders="application_ex_headers"/>
                            <datatable v-else ref="application_datatable" :id="datatable_id" :dtOptions="application_options" :dtHeaders="application_headers"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'ApplicationTableDash',
    props: {
        level:{
            type: String,
            required: true,
            validator:function(val) {
                let options = ['internal','external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        url:{
            type: String,
            required: true
        }
    },
    data() {
        let vm = this;
        let internal_application_headers = [];
        internal_application_headers = ["Number","Licence Category","Activity","Submitter","Applicant","Status","Payment Status","Lodged on","Assigned Officer","Action"];
        let internal_columns = [
            {
                data: "lodgement_number",
                mRender:function(data,type,full){
                    return data;
                }
            },
            {data: "category_name"},
            {
                data: "activity_purpose_string",
                mRender:function (data,type,full) {
                    let output = data.replace(/(?:\r\n|\r|\n)/g, '<br>');
                    return output;
                }
            },
            {
                data: "submitter",
                mRender:function (data,type,full) {
                    if (data) {
                        return `${data.first_name} ${data.last_name}`;
                    }
                    return ''
                }
            },
            {data: "applicant"},
            {
                data: "processing_status",
                mRender:function(data,type,full){
                    return vm.is_external ? full.customer_status.name: data.name;
                }
            },
            {
                data: "payment_status",
                mRender:function(data,type,full){
                    return vm.is_external ? full.customer_status.name: data;
                }
            },
            {
                data: "lodgement_date",
                mRender:function (data,type,full) {
                    return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                }
            },
            {data: "assigned_officer"},
            {
                // Actions
                mRender:function (data,type,full) {
                    let links = '';
                    if (!vm.is_external){
                        links += (full.can_be_processed && full.user_in_officers_and_assessors) ?
                            `<a href='/internal/application/${full.id}'>Process</a><br/>` :
                            `<a href='/external/application/${full.id}'>View</a><br/>`;
                    }
                    if (vm.is_external){
                        if (full.can_current_user_edit) {
                            links +=  `<a href='/external/application/${full.id}'>Continue</a><br/>`;
                            links +=  `<a href='#${full.id}' data-discard-application='${full.id}'>Discard</a><br/>`;
                        }
                    }
                    return links;
                }
            }
        ]
        
        let external_columns = [
            {
                data: "lodgement_number",
                mRender:function(data,type,full){
                    return data;
                }
            },
            {data: "category_name"},
            {
                data: "activity_purpose_string",
                mRender:function (data,type,full) {
                    let output = data.replace(/(?:\r\n|\r|\n)/g, '<br>');
                    return output;
                }
            },
            {
                data: "submitter",
                mRender:function (data,type,full) {
                    if (data) {
                        return `${data.first_name} ${data.last_name}`;
                    }
                    return ''
                }
            },
            {data: "applicant"},
            {
                data: "customer_status",
                mRender:function(data,type,full){
                    return vm.is_external ? full.customer_status.name: data.name;
                }
            },
            {
                data: "lodgement_date",
                mRender:function (data,type,full) {
                    return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                }
            },
            {
                // Actions
                mRender:function (data,type,full) {
                    let links = '';
                    if (!vm.is_external){
                        links +=  `<a href='/internal/application/${full.id}'>View</a><br/>`;
                    }
                    else{
                        if (full.can_current_user_edit) {
                            links +=  `<a href='/external/application/${full.id}'>Continue</a><br/>`;
                            links +=  `<a href='#${full.id}' data-discard-application='${full.id}'>Discard</a><br/>`;
                        }
                        else if (full.can_user_view) {
                            links +=  `<a href='/external/application/${full.id}'>View</a><br/>`;

                            if (full.payment_status == 'unpaid'){
                                links +=  `<a href='#${full.id}' data-pay-application-fee='${full.id}'>Pay Application Fee</a><br/>`;
                            }
                        }
                    }
                    return links;
                }
            }
        ]
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'application-datatable-'+vm._uid,
            // Filters for Applications
            filterApplicationLicenceType: 'All',
            filterApplicationStatus: 'All',
            filterApplicationLodgedFrom: '',
            filterApplicationLodgedTo: '',
            filterApplicationSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            application_licence_types : [],
            application_submitters: [],
            application_status: [],
            application_ex_headers:["Number","Licence Category","Activity","Submitter","Applicant","Status","Lodged on","Action"],
            application_ex_options:{
                order: [
                    [0, 'desc']
                ],
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.url,
                    "dataSrc": ''
                },
                columns: external_columns,
                processing: true,
                initComplete: function () {
                    // Grab Activity from the data in the table
                    var titleColumn = vm.visibleDatatable.vmDataTable.columns(vm.getColumnIndex('licence category'));
                    titleColumn.data().unique().sort().each( function ( d, j ) {
                        let activityTitles = [];
                        $.each(d,(index,a) => {
                            a != null && activityTitles.indexOf(a) < 0 ? activityTitles.push(a): '';
                        })
                        vm.application_licence_types = activityTitles;
                    });
                    // Grab submitters from the data in the table
                    var submittersColumn = vm.visibleDatatable.vmDataTable.columns(vm.getColumnIndex('submitter'));
                    submittersColumn.data().unique().sort().each( function ( d, j ) {
                        var submitters = [];
                        $.each(d,(index,s) => {
                            if (!submitters.find(submitter => submitter.email == s.email) || submitters.length == 0){
                                submitters.push({
                                    'email':s.email,
                                    'search_term': `${s.first_name} ${s.last_name} (${s.email})`
                                });
                            }
                        });
                        vm.application_submitters = submitters;
                    });
                    // Grab Status from the data in the table
                    var statusColumn = vm.visibleDatatable.vmDataTable.columns(vm.getColumnIndex('status'));
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && !statusTitles.filter(status => status.id == a.id ).length ? statusTitles.push(a): '';
                        })
                        vm.application_status = statusTitles;
                    });
                }
            },
            application_headers:internal_application_headers,
            application_options:{
                order: [
                    [0, 'desc']
                ],
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.url,
                    "dataSrc": ''
                },
                columns: internal_columns,
                processing: true,
                initComplete: function () {
                    // Grab Activity from the data in the table
                    var titleColumn = vm.visibleDatatable.vmDataTable.columns(vm.getColumnIndex('licence category'));
                    titleColumn.data().unique().sort().each( function ( d, j ) {
                        let activityTitles = [];
                        $.each(d,(index,a) => {
                            a != null && activityTitles.indexOf(a) < 0 && a.length ? activityTitles.push(a): '';
                        })
                        vm.application_licence_types = activityTitles;
                    });
                    // Grab submitters from the data in the table
                    var submittersColumn = vm.visibleDatatable.vmDataTable.columns(vm.getColumnIndex('submitter'));
                    submittersColumn.data().unique().sort().each( function ( d, j ) {
                        var submitters = [];
                        $.each(d,(index,s) => {
                            if (!submitters.find(submitter => submitter.email == s.email) || submitters.length == 0){
                                submitters.push({
                                    'email':s.email,
                                    'search_term': `${s.first_name} ${s.last_name} (${s.email})`
                                });
                            }
                        });
                        vm.application_submitters = submitters;
                    });
                    var statusColumn = vm.visibleDatatable.vmDataTable.columns(vm.getColumnIndex('status'));
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && !statusTitles.filter(status => status.id == a.id ).length ? statusTitles.push(a): '';
                        })
                        vm.application_status = statusTitles;
                    });

                    // Fix the table rendering columns
                    vm.visibleDatatable.vmDataTable.columns.adjust().responsive.recalc();
                }
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterApplicationStatus: function() {
            this.filterByColumn('status', this.filterApplicationStatus);
        },
        filterApplicationSubmitter: function(){
            this.visibleDatatable.vmDataTable.draw();
        },
        filterApplicationLodgedFrom: function(){
            this.visibleDatatable.vmDataTable.draw();
        },
        filterApplicationLodgedTo: function(){
            this.visibleDatatable.vmDataTable.draw();
        },
        filterApplicationLicenceType: function(){
            this.filterByColumn('licence category', this.filterApplicationLicenceType);
        },
        
    },
    computed: {
        visibleHeaders: function() {
            return this.is_external ? this.application_ex_headers : this.application_headers;
        },
        visibleDatatable: function() {
            return this.is_external ? this.$refs.external_application_datatable : this.$refs.application_datatable;
        },
        is_external: function(){
            return this.level == 'external';
        }
    },
    methods:{
        discardApplication:function (application_id) {
            let vm = this;
            swal({
                title: "Discard Application",
                text: "Are you sure you want to discard this application?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Discard Application',
                confirmButtonColor:'#d9534f'
            }).then((result) => {
                if (result.value) {
                    vm.$http.delete(api_endpoints.discard_application(application_id))
                    .then((response) => {
                        swal(
                            'Discarded',
                            'Your application has been discarded',
                            'success'
                        )
                        vm.visibleDatatable.vmDataTable.ajax.reload();
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        payApplicationFee:function (application_id) {
            let vm = this;
            console.log('test')
            vm.$http.post(helpers.add_endpoint_join(api_endpoints.applications,application_id+'/application_fee_checkout/'), application_id).then(res=>{
                    window.location.href = "/ledger/checkout/checkout/payment-details/";
                },err=>{
                    swal(
                        'Submit Error',
                        helpers.apiVueResourceError(err),
                        'error'
                    )
                });
        },
        addEventListeners: function(){
            let vm = this;
            // Initialise Application Date Filters
            $(vm.$refs.applicationDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.applicationDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.applicationDateToPicker).data('DateTimePicker').date()) {
                    vm.filterApplicationLodgedTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.applicationDateToPicker).data('date') === "") {
                    vm.filterapplicationodgedTo = "";
                }
             });
            $(vm.$refs.applicationDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.applicationDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.applicationDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterApplicationLodgedFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.applicationDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.applicationDateFromPicker).data('date') === "") {
                    vm.filterApplicationLodgedFrom = "";
                }
            });
            // End Application Date Filters
            // External Discard listener
            vm.visibleDatatable.vmDataTable.on('click', 'a[data-discard-application]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-discard-application');
                vm.discardApplication(id);
            });
            // External Pay Application Fee listener
            vm.visibleDatatable.vmDataTable.on('click', 'a[data-pay-application-fee]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-pay-application-fee');
                vm.payApplicationFee(id);
            });
            // Initialise select2 for region
            $(vm.$refs.filterRegion).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Region"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.filterApplicationRegion = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.filterApplicationRegion = selected.val();
            });
        },
        initialiseSearch:function(){
            this.regionSearch();
            this.submitterSearch();
            this.dateSearch();
        },
        regionSearch:function(){
            // let vm = this;
            // vm.visibleDatatable.table.dataTableExt.afnFiltering.push(
            //     function(settings,data,dataIndex,original){
            //         let found = false;
            //         let filtered_regions = vm.filterApplicationRegion;
            //         if (filtered_regions.length == 0){ return true; } 

            //         let regions = original.region != '' && original.region != null ? original.region.split(','): [];

            //         $.each(regions,(i,r) => {
            //             if (filtered_regions.indexOf(r) != -1){
            //                 found = true;
            //                 return false;
            //             }
            //         });
            //         if  (found) { return true; }

            //         return false;
            //     }
            // );
        },
        submitterSearch:function(){
            let vm = this;
            vm.visibleDatatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let filtered_submitter = vm.filterApplicationSubmitter;
                    if (filtered_submitter == 'All'){ return true; } 
                    return filtered_submitter == original.submitter.email;
                }
            );
        },
        dateSearch:function(){
            let vm = this;
            vm.visibleDatatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let from = vm.filterApplicationLodgedFrom;
                    let to = vm.filterApplicationLodgedTo;
                    let val = original.lodgement_date;

                    if ( from == '' && to == ''){
                        return true;
                    }
                    else if (from != '' && to != ''){
                        return val != null && val != '' ? moment().range(moment(from,vm.dateFormat),moment(to,vm.dateFormat)).contains(moment(val)) :false;
                    }
                    else if(from == '' && to != ''){
                        if (val != null && val != ''){
                            return moment(to,vm.dateFormat).diff(moment(val)) >= 0 ? true : false;
                        }
                        else{
                            return false;
                        }
                    }
                    else if (to == '' && from != ''){
                        if (val != null && val != ''){
                            return moment(val).diff(moment(from,vm.dateFormat)) >= 0 ? true : false;
                        }
                        else{
                            return false;
                        }
                    } 
                    else{
                        return false;
                    }
                }
            );
        },
        getColumnIndex: function(column_name) {
            return this.visibleHeaders.map(header => header.toLowerCase()).indexOf(column_name.toLowerCase());
        },
        filterByColumn: function(column, filterAttribute) {
            const column_idx = this.getColumnIndex(column);
            const filterValue = typeof(filterAttribute) == 'string' ? filterAttribute : filterAttribute.name;
            if (filterValue!= 'All') {
                this.visibleDatatable.vmDataTable.columns(column_idx).search('^' + filterValue +'$', true, false).draw();
            } else {
                this.visibleDatatable.vmDataTable.columns(column_idx).search('').draw();
            }
        },
    },
    mounted: function(){
        let vm = this;
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        });
        this.$nextTick(() => {
            vm.initialiseSearch();
            vm.addEventListeners();
        });
    }
}
</script>
<style scoped>
</style>
