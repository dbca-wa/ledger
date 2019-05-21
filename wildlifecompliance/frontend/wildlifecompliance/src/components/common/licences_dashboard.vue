<template id="licence_dashboard">
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
                                <label for="">Licence Category</label>
                                <select class="form-control" v-model="filterLicenceType">
                                    <option value="All">All</option>
                                    <option v-for="l in licence_categories" :value="l">{{l}}</option>
                                </select>
                            </div>
                        </div>
                        <!--<div class="col-md-3">
                            <div class="form-group">
                                <label for="">Licence Status</label>
                                <select class="form-control" v-model="filterLicenceStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in licence_status" :value="s">{{s}}</option>
                                </select>
                            </div>
                        </div>-->
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Issued From</label>
                            <div class="input-group date" ref="licenceDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterLicenceIssuedFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Issued To</label>
                            <div class="input-group date" ref="licenceDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterLicenceIssuedTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Licence Holder</label>
                                <select class="form-control" v-model="filterLicenceHolder" ref="licence_holder_select">
                                    <option value="All">All</option>
                                    <option v-for="holder in licence_holders" :value="holder.holder_name" v-bind:key="`licence_holder_${holder.holder_name}`">{{holder.holder_name}}</option>
                                </select>
                            </div>
                        </div>
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
            filterLicenceType: 'All',
//            filterLicenceStatus: 'All',
            filterLicenceIssuedFrom: '',
            filterLicenceIssuedTo: '',
            filterLicenceHolder: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
//            licence_status:[],
            licence_holders: [],
            licence_categories: [],
//            licence_headers: ["Number", "Category", "Holder", "Status", "Issue Date", "Licence", "Action"],
            licence_headers: ["Number", "Category", "Holder", "Issue Date", "Licence", "Action"],
            licence_options:{
                serverSide: true,
                searchDelay: 1000,
                lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                order: [
                    [0, 'desc']
                ],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                rowCallback: function (row, data){
                    $(row).addClass('licRecordRow');
                },
                responsive: true,
                ajax: {
                    "url": vm.url,
                    "dataSrc": 'data',
                    // adding extra GET params for Custom filtering
                    "data": function (d) {
                        d.category_name = vm.filterLicenceType;
//                        d.status = vm.filterLicenceStatus.id;
                        d.holder = vm.filterLicenceHolder;
                        d.date_from = vm.filterLicenceIssuedFrom != '' && vm.filterLicenceIssuedFrom != null ? moment(vm.filterLicenceIssuedFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.date_to = vm.filterLicenceIssuedTo != '' && vm.filterLicenceIssuedTo != null ? moment(vm.filterLicenceIssuedTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                    }
                },
                columns: [
                    {
                        data: "licence_number"
                    },
                    {
                        data: "current_application.category_name",
                        orderable: false,
                        searchable: false // handled by filter_queryset override method - class LicenceFilterBackend
                    },
                    {
                        data: "current_application.applicant",
                        orderable: false,
                        searchable: false // handled by filter_queryset override method - class LicenceFilterBackend
                    },
//                    {
//                        data: "current_application.processing_status.name"
//                    },
                    {
                        data: "last_issue_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        },
                        orderable: false,
                        searchable: false // handled by filter_queryset override method - class LicenceFilterBackend
                    },
                    {
                        data: "licence_document",
                        mRender:function(data,type,full){
                            return `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                        },
                        orderable: false,
                        searchable: false
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            let org_id = full.current_application.org_applicant ? full.current_application.org_applicant.id : ''
                            let proxy_id = full.current_application.proxy_applicant ? full.current_application.proxy_applicant.id : ''
                            let licence_category_id = full.current_application.category_id ? full.current_application.category_id : ''
                            links +=  `<a href='#${full.id}' add-activity-purpose='${full.id}' org_id='${org_id}' proxy_id='${proxy_id}' licence_category_id='${licence_category_id}'>Add Activity/Purpose</a><br/>`;
                            return links;
                        },
                        orderable: false,
                        searchable: false

                    }
                ],
                processing: true,
                initComplete: function () {
                    // Grab Category from the data in the table
                    var titleColumn = vm.$refs.licence_datatable.vmDataTable.columns(vm.getColumnIndex('category'));
                    titleColumn.data().unique().sort().each( function ( d, j ) {
                        let categoryTitles = [];
                        $.each(d,(index,a) => {
                            a != null && categoryTitles.indexOf(a) < 0 ? categoryTitles.push(a): '';
                        })
                        vm.licence_categories = categoryTitles;
                    });
                    // Grab holders from the data in the table
                    var holdersColumn = vm.$refs.licence_datatable.vmDataTable.columns(vm.getColumnIndex('holder'));
                    holdersColumn.data().unique().sort().each( function ( d, j ) {
                        var holders = [];
                        $.each(d,(index, holder) => {
                            if (!holders.find(item => item.holder_name == holder) || holders.length == 0){
                                holders.push({
                                    'holder_name': holder,
                                });
                            }
                        });
                        vm.licence_holders = holders;
                    });
                    // Grab Status from the data in the table
//                    var statusColumn = vm.$refs.licence_datatable.vmDataTable.columns(vm.getColumnIndex('status'));
//                    statusColumn.data().unique().sort().each( function ( d, j ) {
//                        let statusTitles = [];
//                        $.each(d,(index,a) => {
//                            a != null && !statusTitles.filter(status => status.id == a.id ).length ? statusTitles.push(a): '';
//                        })
//                        vm.licence_status = statusTitles;
//                    });
                }
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterLicenceType: function(){
            this.$refs.licence_datatable.vmDataTable.draw();
        },
//        filterLicenceStatus: function(){
//            this.$refs.licence_datatable.vmDataTable.draw();
//        },
        filterLicenceIssuedFrom: function(){
            this.$refs.licence_datatable.vmDataTable.draw();
        },
        filterLicenceIssuedTo: function(){
            this.$refs.licence_datatable.vmDataTable.draw();
        },
        filterLicenceHolder: function(){
            this.$refs.licence_datatable.vmDataTable.draw();
        },
    },
    computed: {
        is_external: function(){
            return this.level == 'external';
        },
        
    },
    methods:{
        addEventListeners: function(){
            let vm = this;
            // Initialise Licence Issued Date Filters
            $(vm.$refs.licenceDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.licenceDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.licenceDateToPicker).data('DateTimePicker').date()) {
                    vm.filterLicenceIssuedTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.licenceDateToPicker).data('date') === "") {
                    vm.filterLicenceIssuedTo = "";
                }
             });
            $(vm.$refs.licenceDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.licenceDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.licenceDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterLicenceIssuedFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.licenceDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.licenceDateFromPicker).data('date') === "") {
                    vm.filterLicenceIssuedFrom = "";
                    $(vm.$refs.licenceDateToPicker).data("DateTimePicker").minDate(false);
                }
            });
            // Initialise select2 for holder
            $(vm.$refs.licence_holder_select).select2({
                "theme": "bootstrap",
                placeholder:"Select Holder"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.filterLicenceHolder = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.filterLicenceHolder = selected.val();
            });
            // Add Activity/Purpose listener
            vm.$refs.licence_datatable.vmDataTable.on('click', 'a[add-activity-purpose]', function(e) {
                e.preventDefault();
                var id = $(this).attr('add-activity-purpose');
                var org_id = $(this).attr('org_id');
                var proxy_id = $(this).attr('proxy_id');
                var licence_category_id = $(this).attr('licence_category_id');
                vm.addActivityPurpose(id, org_id, proxy_id, licence_category_id);
            });
            // Child row listener
            vm.$refs.licence_datatable.vmDataTable.on('click', 'tr.licRecordRow', function(e) {
                // If a link is clicked, ignore
                if($(e.target).is('a')){
                    return;
                }
                // Generate child row for application
                var tr = $(this);
                var row = vm.$refs.licence_datatable.vmDataTable.row(tr);

                if (row.child.isShown()) {
                    // This row is already open - close it
                    row.child.hide();
                    tr.removeClass('shown');
                }
                else {
                    // Open this row (the format() function would return the data to be shown)
                    var child_row = ''
                    // Generate rows for each activity if internal
                    var activity_rows = ''
                    row.data()['current_activities'].forEach(function(activity) {
                        activity_rows += `
                            <tr>
                                <td>${activity['activity_name_str']}</td>
                                <td>${activity['activity_purpose_names'].
                                    replace(/(?:\r\n|\r|\n|,)/g, '<br>')}</td>
                                <td>${activity['processing_status']['name']}</td>
                                <td>${activity['expiry_date']}</td>
                                <td></td>
                            </tr>`;
                    });
                    // Generate html for child row
                    child_row += `
                        <table class="table table-striped table-bordered child-row-table">
                            <tr>
                                <th>Activity</th>
                                <th class="width_55pc">Purposes</th>
                                <th class="width_20pc">Status</th>
                                <th class="width_20pc">Expiry Date</th>
                                <th class="width_20pc">Action</th>
                            </tr>
                            ${activity_rows}
                        </table>`;
                    // Show child row, dark-row className CSS applied from application.scss
                    row.child(
                        child_row
                        , 'dark-row').show();
                    tr.addClass('shown');
                }
            });

        },
        initialiseSearch:function(){
            this.dateSearch();
            this.holderSearch();
        },
        holderSearch:function(){
            let vm = this;
            vm.$refs.licence_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let filtered_holder = vm.filterLicenceHolder;
                    if (filtered_holder == 'All'){ return true; }
                    return filtered_holder == original.holder;
                }
            );
        },
        dateSearch:function(){
            let vm = this;
            vm.$refs.licence_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let from = vm.filterLicenceIssuedFrom;
                    let to = vm.filterLicenceIssuedTo;
                    let val = original.last_issue_date;

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
            return this.licence_headers.map(header => header.toLowerCase()).indexOf(column_name.toLowerCase());
        },
        addActivityPurpose:function (licence_id, org_id, proxy_id, licence_category_id) {
            return this.$router.push({
                name: "apply_application_licence",
                params: {
                    licence_select: 'new_activity',
                    licence_category: licence_category_id,
                    org_select: org_id,
                    proxy_select: proxy_id
                }
            });
        },
//        filterByColumn: function(column, filterAttribute) {
//            const column_idx = this.getColumnIndex(column);
//            const filterValue = typeof(filterAttribute) == 'string' ? filterAttribute : filterAttribute.name;
//            if (filterValue!= 'All') {
//                this.$refs.licence_datatable.vmDataTable.columns(column_idx).search('^' + filterValue +'$', true, false).draw();
//            } else {
//                this.$refs.licence_datatable.vmDataTable.columns(column_idx).search('').draw();
//            }
//        },
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
