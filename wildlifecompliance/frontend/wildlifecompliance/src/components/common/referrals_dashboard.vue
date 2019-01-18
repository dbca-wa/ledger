<template id="application_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Applications requiring assessment
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
                                    <option v-for="lt in application_licence_types" :value="lt">{{lt}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterApplicationStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in application_status" :value="s">{{s}}</option>
                                </select>
                            </div>
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
                                    <option v-for="s in application_submitters" :value="s.email">{{s.search_term}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="application_datatable" :id="datatable_id" :dtOptions="application_options" :dtHeaders="application_headers"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'ApplicationTableDash',
    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'application-datatable-'+vm._uid,
            // Filters for Applications
            filterApplicationRegion: [],
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
            application_status:[],
            application_licence_types: [],
            application_regions: [],
            application_submitters: [],
            application_headers:["Number","Licence Category","Activity Type","Submitter","Applicant","Status","Lodged on","Action"],
            application_options:{
                customApplicationSearch: true,
                tableID: 'application-datatable-'+vm._uid,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.assessment,'user_list'),
                    "dataSrc": ''
                },
                columns: [
                    {
                        data: "application",
                        mRender:function(data,type,full){
                            return 'P'+data;
                        }
                    },
                    {
                        data: "application_category",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? `${data}` : '';
                        }
                    },
                    {
                        data: "licence_activity_type",
                        mRender:function (data,type,full) {
                            return data.id != '' && data.id != null ? `${data.name}` : '';
                        }
                    },
                    {
                        data: "submitter",
                        mRender:function (data,type,full) {
                            return data.id != '' && data.id != null ? `${data.first_name} ${data.last_name}` : '';
                        }
                    },
                    {
                        data: "applicant",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? `${data}` : '';
                        }
                    },
                    {
                        data: "status",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? `${data}` : '';
                        }
                    },
                    {
                        data: "application_lodgement_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        }
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            links +=  full.can_be_processed ? `<a href='/internal/application/${full.application}'>Process</a><br/>`: `<a href='/internal/application/${full.application}'>View</a><br/>`;
                            return links;
                        }
                    }
                ],
                processing: true,
                initComplete: function () {
                    // Grab Regions from the data in the table
                    var regionColumn = vm.$refs.application_datatable.vmDataTable.columns(1);
                    regionColumn.data().unique().sort().each( function ( d, j ) {
                        let regionTitles = [];
                        $.each(d,(index,a) => {
                            // Split region string to array
                            if (a != null){
                                $.each(a.split(','),(i,r) => {
                                    r != null && regionTitles.indexOf(r) < 0 ? regionTitles.push(r): '';
                                });
                            }
                        })
                        vm.application_regions = regionTitles;
                    });
                    // Grab Activity from the data in the table
                    var titleColumn = vm.$refs.application_datatable.vmDataTable.columns(2);
                    titleColumn.data().unique().sort().each( function ( d, j ) {
                        let activityTitles = [];
                        $.each(d,(index,a) => {
                            a != null && activityTitles.indexOf(a) < 0 ? activityTitles.push(a): '';
                        })
                        vm.application_activityTitles = activityTitles;
                    });
                    // Grab submitters from the data in the table
                    var submittersColumn = vm.$refs.application_datatable.vmDataTable.columns(3);
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
                    var statusColumn = vm.$refs.application_datatable.vmDataTable.columns(5);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.application_status = statusTitles;
                    });
                }
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterApplicationActivity: function() {
            let vm = this;
            if (vm.filterApplicationActivity!= 'All') {
                vm.$refs.application_datatable.vmDataTable.columns(2).search(vm.filterApplicationActivity).draw();
            } else {
                vm.$refs.application_datatable.vmDataTable.columns(2).search('').draw();
            }
        },
        filterApplicationStatus: function() {
            let vm = this;
            if (vm.filterApplicationStatus!= 'All') {
                vm.$refs.application_datatable.vmDataTable.columns(5).search(vm.filterApplicationStatus).draw();
            } else {
                vm.$refs.application_datatable.vmDataTable.columns(5).search('').draw();
            }
        },
        filterApplicationRegion: function(){
            this.$refs.application_datatable.vmDataTable.draw();
        },
        filterApplicationSubmitter: function(){
            this.$refs.application_datatable.vmDataTable.draw();
        },
        filterApplicationLodgedFrom: function(){
            this.$refs.application_datatable.vmDataTable.draw();
        },
        filterApplicationLodgedTo: function(){
            this.$refs.application_datatable.vmDataTable.draw();
        }
    },
    computed: {
    },
    methods:{
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
            vm.$refs.application_datatable.vmDataTable.on('click', 'a[data-discard-application]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-discard-application');
                vm.discardApplication(id);
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
            let vm = this;
            vm.$refs.application_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let found = false;
                    let filtered_regions = vm.filterApplicationRegion;
                    if (filtered_regions.length == 0){ return true; } 
                    let regions = original.region != '' && original.region != null ? original.region.split(','): [];
                    $.each(regions,(i,r) => {
                        if (filtered_regions.indexOf(r) != -1){
                            found = true;
                            return false;
                        }
                    });
                    if  (found) { return true; }
                    return false;
                }
            );
        },
        submitterSearch:function(){
            let vm = this;
            vm.$refs.application_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let filtered_submitter = vm.filterApplicationSubmitter;
                    if (filtered_submitter == 'All'){ return true; } 
                    return filtered_submitter == original.submitter.email;
                }
            );
        },
        dateSearch:function(){
            let vm = this;
            vm.$refs.application_datatable.table.dataTableExt.afnFiltering.push(
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
        }
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
            vm.addEventListeners();
            vm.initialiseSearch();
        });
    }
}
</script>
<style scoped>
</style>