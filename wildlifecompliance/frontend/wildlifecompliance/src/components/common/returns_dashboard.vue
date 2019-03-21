<template id="returns_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Returns <small v-if="is_external">View submitted returns and submit new ones</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">LicenceType</label>
                                <select class="form-control" v-model="filterReturnLicenceType">
                                    <option value="All">All</option>
                                    <option v-for="lt in return_licence_types" :value="lt">{{lt}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterReturnStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in status" :value="s">{{s}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="return_datatable" :id="datatable_id" :dtOptions="application_options" :dtHeaders="application_headers"/>
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
            datatable_id: 'return-datatable-'+vm._uid,
            // Filters for Applications
            filterReturnLicenceType: 'All',
            filterReturnStatus: 'All',
            
            // filterApplicationRegion: 'All',
            // filterApplicationStatus: 'All',
            // filterApplicationLodgedFrom: '',
            // filterApplicationLodgedTo: '',
            // filterApplicationSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            external_status:[
                'Draft',
                'Submitted',
                'Approved',
                'Declined'
            ],
            internal_status:[
                'Draft',
                'With Assessor',
                'Issued',
                'Declined'
            ],
            application_activityTitles : [],
            application_regions: [],
            application_submitters: [],
            return_licence_types: [],
            application_headers:["Number","Due Date","Status","Licence","Action"],
            application_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.url,
                    "dataSrc": ''
                },
                columns: [
                    {
                        data: "id",
                        mRender:function (data,type,full) {
                            return `C${data}`;
                        }
                    },
                                        
                    {
                        data: "due_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        }
                    },
                    {data: "processing_status"},
                    {
                        data: "licence",
                        mRender:function (data,type,full) {
                            return `A${data.name}`;
                        }
                    },
                    {
                        mRender:function (data,type,full) {
                            let vm=this;
                            let links = '';

                            links +=  `<a href='/internal/return/${full.id}'>View</a><br/>`;
                            if (full.type == 'sheet') {
                              links +=  `<a href='/external/return/sheet/${full.id}'>Continue</a><br/>`;
                            } else if (full.type == 'question') {
                              links +=  `<a href='/external/return/question/${full.id}'>Continue</a><br/>`;
                            } else {
                              links +=  `<a href='/external/return/${full.id}'>Continue</a><br/>`;
                            }
                            // if (!vm.is_external){

                            //     links +=  `<a href='/internal/return/${full.id}'>View</a><br/>`;
                            // }
                            // else{
                            //         links +=  `<a href='/external/return/${full.id}'>Continue</a><br/>`;
                                    
                            //     // else if (full.can_user_view) {
                            //     //     links +=  `<a href='/external/application/${full.id}'>View</a><br/>`;
                            //     // }
                            // }
                            return links;
                        }
                    }
                ],
                processing: true,
                initComplete: function () {
                    // Grab Regions from the data in the table
                    // var regionColumn = vm.$refs.application_datatable.vmDataTable.columns(1);
                    // regionColumn.data().unique().sort().each( function ( d, j ) {
                    //     let regionTitles = [];
                    //     $.each(d,(index,a) => {
                    //         // Split region string to array
                    //         if (a != null){
                    //             $.each(a.split(','),(i,r) => {
                    //                 r != null && regionTitles.indexOf(r) < 0 ? regionTitles.push(r): '';
                    //             });
                    //         }
                    //     })
                    //     vm.application_regions = regionTitles;
                    // });
                    // Grab Activity from the data in the table
                    // var titleColumn = vm.$refs.application_datatable.vmDataTable.columns(2);
                    // titleColumn.data().unique().sort().each( function ( d, j ) {
                    //     let activityTitles = [];
                    //     $.each(d,(index,a) => {
                    //         a != null && activityTitles.indexOf(a) < 0 ? activityTitles.push(a): '';
                    //     })
                    //     vm.application_activityTitles = activityTitles;
                    // });
                }
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterReturnLicenceType: function(){
        },
        filterReturnStatus: function(){
        }
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
            // this.regionSearch();
            // this.dateSearch();
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
            // let vm = this;
            // vm.$refs.application_datatable.table.dataTableExt.afnFiltering.push(
            //     function(settings,data,dataIndex,original){
            //         let filtered_submitter = vm.filterApplicationSubmitter;
            //         if (filtered_submitter == 'All'){ return true; } 
            //         return filtered_submitter == original.submitter.email;
            //     }
            // );
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
            // console.log(vm.is_external)

        });
    }
}
</script>
<style scoped>
</style>
