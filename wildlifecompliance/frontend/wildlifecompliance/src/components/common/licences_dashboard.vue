<template id="application_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Licences <small v-if="is_external">View existing licences and amend or renew them</small>
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
                                <select class="form-control" v-model="filterLicenceType">
                                    <option value="All">All</option>
                                    <option v-for="l in licence_types" :value="l">{{l}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Licence Status</label>
                                <select class="form-control" v-model="filterLicenceStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in licence_status" :value="s">{{s}}</option>
                                </select>
                            </div>
                        </div>
                        <!--<div class="col-md-3">
                            <div class="form-group">
                                <label for="">Category</label>
                                <select class="form-control" v-model="filterCategory">
                                    <option value="All">All</option>
                                    <option v-for="c in licence_categories" :value="c">{{c}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Category Status</label>
                                <select class="form-control" v-model="filterCategoryStatus">
                                    <option value="All">All</option>
                                    <option v-for="cs in licence_categoryStatus" :value="cs">{{cs}}</option>
                                </select>
                            </div>
                        </div>-->
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="licence_datatable" :id="datatable_id" :dtOptions="licence_options" :dtHeaders="licence_headers"/>
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
    name: 'LicenceTableDash',
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
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'licence-datatable-'+vm._uid,
            // Filters for Licences
            filterLicenceType: 'All',
            filterLicenceStatus: 'All',
            filterCategory: 'All',
            filterCategoryStatus: '',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            licence_status:[],
            licence_activityTitles : [],
            licence_submitters: [],
            licence_types: [],
            licence_categories: [],
            licence_categoryStatus: [],
            licence_headers: ["Number", "Licence Type", "Licence Holder", "Status", "Issue Date", "Licence","Action"],
            licence_options:{
                order: [
                    [0, 'desc']
                ],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.url,
                    "dataSrc": ''
                },
                columns: [
                    {data: "id"},
                    {data: "current_application.licence_type_data.name"},
                    {data: "current_application.applicant"},
                    {data: "current_application.processing_status.name"},
                    {
                        data: "last_issue_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        }
                    },
                    {
                        data: "licence_document",
                        mRender:function(data,type,full){
                            return `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                        }
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            return links;
                        }
                    }
                ],
                processing: true,
                initComplete: function () {
                    // Grab Activity from the data in the table
                    var titleColumn = vm.$refs.licence_datatable.vmDataTable.columns(vm.getColumnIndex('licence type'));
                    titleColumn.data().unique().sort().each( function ( d, j ) {
                        let activityTitles = [];
                        $.each(d,(index,a) => {
                            a != null && activityTitles.indexOf(a) < 0 ? activityTitles.push(a): '';
                        })
                        vm.licence_types = activityTitles;
                    });
                    // Grab Status from the data in the table
                    var statusColumn = vm.$refs.licence_datatable.vmDataTable.columns(vm.getColumnIndex('status'));
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.licence_status = statusTitles;
                    });
                    // Fix the table rendering columns
                    vm.$refs.licence_datatable.vmDataTable.columns.adjust().responsive.recalc();
                }
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterLicenceType: function(){
            this.filterByColumn('licence type', this.filterLicenceType);
        },
        filterLicenceStatus: function(){
            this.filterByColumn('status', this.filterLicenceStatus);
        },
        filterCategory: function(){
        },
        filterCategoryStatus: function(){
        },
    },
    computed: {
        status: function(){
            //return this.is_external ? this.external_status : this.internal_status;
            return [];
        },
        is_external: function(){
            return this.level == 'external';
        },
        
    },
    methods:{
        addEventListeners: function(){
            let vm = this;
            // Initialise Application Date Filters
            // $(vm.$refs.applicationDateToPicker).datetimepicker(vm.datepickerOptions);
            // $(vm.$refs.applicationDateToPicker).on('dp.change', function(e){
            //     if ($(vm.$refs.applicationDateToPicker).data('DateTimePicker').date()) {
            //         vm.filterApplicationLodgedTo =  e.date.format('DD/MM/YYYY');
            //     }
            //     else if ($(vm.$refs.applicationDateToPicker).data('date') === "") {
            //         vm.filterapplicationodgedTo = "";
            //     }
            //  });
            // $(vm.$refs.applicationDateFromPicker).datetimepicker(vm.datepickerOptions);
            // $(vm.$refs.applicationDateFromPicker).on('dp.change',function (e) {
            //     if ($(vm.$refs.applicationDateFromPicker).data('DateTimePicker').date()) {
            //         vm.filterApplicationLodgedFrom = e.date.format('DD/MM/YYYY');
            //         $(vm.$refs.applicationDateToPicker).data("DateTimePicker").minDate(e.date);
            //     }
            //     else if ($(vm.$refs.applicationDateFromPicker).data('date') === "") {
            //         vm.filterApplicationLodgedFrom = "";
            //     }
            // });
            // // End Application Date Filters
            // // External Discard listener
            // vm.$refs.application_datatable.vmDataTable.on('click', 'a[data-discard-application]', function(e) {
            //     e.preventDefault();
            //     var id = $(this).attr('data-discard-application');
            //     vm.discardApplication(id);
            // });
        },
        initialiseSearch:function(){
            this.regionSearch();
            this.dateSearch();
        },
        regionSearch:function(){
            // let vm = this;
            // vm.$refs.application_datatable.table.dataTableExt.afnFiltering.push(
            //     function(settings,data,dataIndex,original){
            //         let found = false;
            //         let filtered_regions = vm.filterApplicationRegion.split(',');
            //         if (filtered_regions == 'All'){ return true; } 

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
            vm.$refs.licence_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let filtered_submitter = vm.filterLicenceSubmitter;
                    if (filtered_submitter == 'All'){ return true; } 
                    return filtered_submitter == original.submitter.email;
                }
            );
        },
        dateSearch:function(){
            let vm = this;
            // vm.$refs.application_datatable.table.dataTableExt.afnFiltering.push(
            //     function(settings,data,dataIndex,original){
            //         let from = vm.filterApplicationLodgedFrom;
            //         let to = vm.filterApplicationLodgedTo;
            //         let val = original.lodgement_date;

            //         if ( from == '' && to == ''){
            //             return true;
            //         }
            //         else if (from != '' && to != ''){
            //             return val != null && val != '' ? moment().range(moment(from,vm.dateFormat),moment(to,vm.dateFormat)).contains(moment(val)) :false;
            //         }
            //         else if(from == '' && to != ''){
            //             if (val != null && val != ''){
            //                 return moment(to,vm.dateFormat).diff(moment(val)) >= 0 ? true : false;
            //             }
            //             else{
            //                 return false;
            //             }
            //         }
            //         else if (to == '' && from != ''){
            //             if (val != null && val != ''){
            //                 return moment(val).diff(moment(from,vm.dateFormat)) >= 0 ? true : false;
            //             }
            //             else{
            //                 return false;
            //             }
            //         } 
            //         else{
            //             return false;
            //         }
            //     }
            // );
        },
        getColumnIndex: function(column_name) {
            return this.licence_headers.map(header => header.toLowerCase()).indexOf(column_name.toLowerCase());
        },
        filterByColumn: function(column, filterAttribute) {
            const column_idx = this.getColumnIndex(column);
            const filterValue = typeof(filterAttribute) == 'string' ? filterAttribute : filterAttribute.name;
            if (filterValue!= 'All') {
                this.$refs.licence_datatable.vmDataTable.columns(column_idx).search('^' + filterValue +'$', true, false).draw();
            } else {
                this.$refs.licence_datatable.vmDataTable.columns(column_idx).search('').draw();
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
            vm.addEventListeners();
            vm.initialiseSearch();
        });
    }
}
</script>
<style scoped>
</style>
