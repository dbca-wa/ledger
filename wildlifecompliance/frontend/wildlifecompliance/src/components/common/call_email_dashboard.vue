<template id="application_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Call/Email <small v-if="is_external">View existing licences and amend or renew them</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Call/Email status</label>
                                <select class="form-control" v-model="filterLicenceType">
                                    <option value="All">All</option>
                                    <!--option v-for="s in call_status">{{s}}</option-->
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="call_email_datatable" :id="datatable_id" :dtOptions="call_email_options" :dtHeaders="call_email_headers"/>
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
    name: 'CallEmailTableDash',
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
            datatable_id: 'call-email-datatable-'+vm._uid,
            other_data: 'my_data',
            
            
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
            /*
            licence_status:[],
            licence_activityTitles : [],
            licence_regions: [],
            licence_submitters: [],
            licence_licenceTypes: [],
            licence_status: [],
            licence_categories: [],
            licence_categoryStatus: [],
            */
            call_status: [],
            call_email_headers:["Call status","Classification"],
            call_email_options: {
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
                    { data: "status"},
                    { data: "classification"},
                ],
                /*
                columns: [
                    {data: "id"},
                    {data: "current_application.licence_type_data.name"},
                    {data: "applicant"},
                    {data: "status"},
                    {
                        data: "issue_date",
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
                */
                processing: true,
                initComplete: function () {
                    /*
                    var classificationColumn = vm.$refs.call_email_datatable.vmDataTable.columns(1);
                    classificationColumn.data().unique().sort().each( function ( d, j ) {
                        let classificationTitles = [];
                        $.each(d,(index,a) => {
                            // Split region string to array
                            if (a != null){
                                $.each(a.split(','),(i,r) => {
                                    r != null && regionTitles.indexOf(r) < 0 ? regionTitles.push(r): '';
                                });
                            }
                        })
                        vm.licence_regions = classificationTitles;
                    });
                    */
                    
                    // Grab Activity from the data in the table
                    var statusColumn = vm.$refs.call_email_datatable.vmDataTable.columns(1);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let callStatus = [];
                        $.each(d,(index,a) => {
                            a != null && callStatus.indexOf(a) < 0 ? callStatus.push(a): '';
                        })
                        vm.call_status = callStatus;
                    });
                    
                    /*
                    // Grab Status from the data in the table
                    var statusColumn = vm.$refs.call_email_datatable.vmDataTable.columns(5);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.licence_status = statusTitles;
                    });
                    */
                    // Fix the table rendering columns
                    vm.$refs.call_email_datatable.vmDataTable.columns.adjust().responsive.recalc();
                    
                }
            }
        }
    },
    components:{
        datatable
    },
    
    watch:{
        filterLicenceType: function(){
        },
        filterLicenceStatus: function(){
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
    /*
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
            vm.$refs.call_email_datatable.table.dataTableExt.afnFiltering.push(
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
    */
}
</script>
<style scoped>
</style>
