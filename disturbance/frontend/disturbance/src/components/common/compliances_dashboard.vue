a<template id="proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Compliance with requirements <small v-if="is_external">View submitted compliances and submit new ones</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Region</label>
                                <select class="form-control" v-model="filterProposalRegion">
                                    <option value="All">All</option>
                                    <option v-for="r in proposal_regions" :value="r">{{r}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Activity</label>
                                <select class="form-control" v-model="filterProposalActivity">
                                    <option value="All">All</option>
                                    <option v-for="a in proposal_activityTitles" :value="a">{{a}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterComplianceStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in status" :value="s">{{s}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Due date From</label>
                            <div class="input-group date" ref="complianceDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceDueFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Due date To</label>
                            <div class="input-group date" ref="complianceDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterComplianceDueTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12" style="margin-top:25px;">
                            <datatable ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_options" :dtHeaders="proposal_headers"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import Vue from 'vue'
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'ProposalTableDash',
    props: {
        level:{
            type: String,
            required: true,
            validator:function(val) {
                let options = ['internal','referral','external'];
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
            datatable_id: 'proposal-datatable-'+vm._uid,
            //Profile to check if user has access to process Proposal
            profile: {},
            // Filters for Proposals
            filterProposalRegion: 'All',
            filterProposalActivity: 'All',
            filterComplianceStatus: 'All',
            filterComplianceDueFrom: '',
            filterComplianceDueTo: '',
            filterProposalSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            external_status:[
                'Due',
                'Future',
                'Under Review',
                'Approved',
            ],
            internal_status:[
                'Due',
                'Future',
                'With Assessor',
                'Approved',
                
            ],
            proposal_activityTitles : [],
            proposal_regions: [],
            proposal_submitters: [],
            proposal_headers:["Number","Region/District","Activity","Title","Approval","Holder","Status","Due Date","Assigned To", "CustomerStatus", "Reference","Action"],
            proposal_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                ajax: {
                    "url": vm.url,
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        //d.regions = vm.filterProposalRegion.join();
                        d.date_from = vm.filterComplianceDueFrom != '' && vm.filterComplianceDueFrom != null ? moment(vm.filterComplianceDueFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.date_to = vm.filterComplianceDueTo != '' && vm.filterComplianceDueTo != null ? moment(vm.filterComplianceDueTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        if (vm.level == 'external') { // hack to allow for correct Django choicelist in qs filter ProposalFilterBackend.filter_quesryset()
                            d.customer_status = vm.filterComplianceStatus == 'Under Review' ? 'with_assessor': vm.filterComplianceStatus != 'All' ? vm.filterComplianceStatus: '';
                            d.processing_status = '';
                        } else {
                            d.processing_status = vm.filterComplianceStatus == 'With Assessor' ? 'with_assessor': vm.filterComplianceStatus != 'All' ? vm.filterComplianceStatus: '';
                            d.customer_status = '';
                        }
                    }

                },
                dom: 'lBfrtip',
                buttons:[
                'excel', 'csv', ],
                columns: [
                    {
                        data: "id",
                        mRender:function (data,type,full) {
                            //return `C${data}`;
                            return full.reference;
                        },
                        name: "id, lodgement_number",
                    },
                    {
                        data: "regions",
                        name: "proposal__region__name" // will be use like: Approval.objects.filter(proposal__region__name='Kimberley')
                    },
                    {
                        data: "activity",
                        name: "proposal__activity",
                    },
                    {
                        data: "title",
                        name: "proposal__title",
                    },
                    {
                        data: "approval_lodgement_number",
                        mRender:function (data,type,full) {
                            return `A${data}`;
                        },
                        name: "approval__lodgement_number"
                    },
                    {
                        data: "holder",
                        name: "proposal__applicant__organisation__name"
                    },

                    {
                        data: vm.level == 'external'? "customer_status" : "processing_status",
                        searchable: false,
                    },
                    {
                        data: "due_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        }
                    },
                    {
                        data: "assigned_to",
                        name: "assigned_to__first_name, assigned_to__last_name, assigned_to__email"
                        // visible: false
                    },
                    {
                        data: '',
                        mRender:function (data,type,full) {
                            let links = '';
                            if (!vm.is_external){
                                if (full.processing_status=='With Assessor' && vm.check_assessor(full)) {
                                    links +=  `<a href='/internal/compliance/${full.id}'>Process</a><br/>`;
                                    
                                }
                                else {
                                    links +=  `<a href='/internal/compliance/${full.id}'>View</a><br/>`;
                                }
                            }
                            else{
                                if (full.can_user_view) {
                                    links +=  `<a href='/external/compliance/${full.id}'>View</a><br/>`;
                                    
                                }
                                else {
                                    links +=  `<a href='/external/compliance/${full.id}'>Submit</a><br/>`;
                                }
                            }
                            return links;
                        },
                        name: ''
                    },
                    {data: "reference", visible: false},
                    {data: "customer_status", visible: false},
                    {data: "can_user_view", visible: false},
                    {data: "allowed_assessors", visible: false},
                ],
                processing: true,
                /*
                initComplete: function () {
                    // Grab Regions from the data in the table
                    var regionColumn = vm.$refs.proposal_datatable.vmDataTable.columns(1);
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
                        vm.proposal_regions = regionTitles;
                    });
                    // Grab Activity from the data in the table
                    var titleColumn = vm.$refs.proposal_datatable.vmDataTable.columns(2);
                    titleColumn.data().unique().sort().each( function ( d, j ) {
                        let activityTitles = [];
                        $.each(d,(index,a) => {
                            a != null && activityTitles.indexOf(a) < 0 ? activityTitles.push(a): '';
                        })
                        vm.proposal_activityTitles = activityTitles;
                    });

                    // Grab Status from the data in the table
                    var statusColumn = vm.$refs.proposal_datatable.vmDataTable.columns(6);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.status = statusTitles;
                    });
                }
                */
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterProposalRegion: function() {
            //this.$refs.proposal_datatable.vmDataTable.draw();
            let vm = this;
            if (vm.filterProposalRegion!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.columns(1).search(vm.filterProposalRegion).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.columns(1).search('').draw();
            }
        },
        filterProposalActivity: function() {
            let vm = this;
            if (vm.filterProposalActivity!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.columns(2).search(vm.filterProposalActivity).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.columns(2).search('').draw();
            }
        },
        filterComplianceStatus: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalSubmitter: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterComplianceDueFrom: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterComplianceDueTo: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        }
    },
    computed: {
       /* status: function(){
            return this.is_external ? this.external_status : this.internal_status;
            //return [];
        }, */
        is_external: function(){
            return this.level == 'external';
        },
        
    },
    methods:{
        fetchFilterLists: function(){
            let vm = this;

            vm.$http.get(api_endpoints.filter_list_compliances).then((response) => {
                vm.proposal_regions = response.body.regions;
                vm.proposal_activityTitles = response.body.activities;
                vm.status = vm.level == 'external' ? vm.external_status: vm.internal_status;
            },(error) => {
                console.log(error);
            })
            //console.log(vm.regions);
        },


        addEventListeners: function(){
            let vm = this;
            // Initialise Proposal Date Filters
            $(vm.$refs.complianceDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.complianceDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.complianceDateToPicker).data('DateTimePicker').date()) {
                    vm.filterComplianceDueTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.complianceDateToPicker).data('date') === "") {
                    vm.filterProposaLodgedTo = "";
                }
             });
            $(vm.$refs.complianceDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.complianceDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.complianceDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterComplianceDueFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.complianceDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.complianceDateFromPicker).data('date') === "") {
                    vm.filterComplianceDueFrom = "";
                }
            });
            // End Proposal Date Filters          
            

            // Initialise select2 for region
            $(vm.$refs.filterRegion).select2({
                "theme": "bootstrap",
                allowClear: true,
                placeholder:"Select Region"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                vm.filterProposalRegion = selected.val();
            }).
            on("select2:unselect",function (e) {
                var selected = $(e.currentTarget);
                vm.filterProposalRegion = selected.val();
            });
        },
        initialiseSearch:function(){
            this.regionSearch();
            this.dateSearch();
        },
        regionSearch:function(){
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let found = false;
                    let filtered_regions = vm.filterProposalRegion.split(',');
                    if (filtered_regions == 'All'){ return true; } 

                    let regions = original.regions != '' && original.regions != null ? original.regions.split(','): [];

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
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let filtered_submitter = vm.filterProposalSubmitter;
                    if (filtered_submitter == 'All'){ return true; } 
                    return filtered_submitter == original.submitter.email;
                }
            );
        },
        dateSearch:function(){
            let vm = this;
            vm.$refs.proposal_datatable.table.dataTableExt.afnFiltering.push(
                function(settings,data,dataIndex,original){
                    let from = vm.filterComplianceDueFrom;
                    let to = vm.filterComplianceDueTo;
                    let val = original.due_date;

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
        fetchProfile: function(){
            let vm = this;
            Vue.http.get(api_endpoints.profile).then((response) => {
                vm.profile = response.body
                              
            },(error) => {
                console.log(error);
                
            })
        },
        check_assessor: function(compliance){
            let vm = this;         
            
            var assessor = compliance.allowed_assessors.filter(function(elem){
                    return(elem.id==vm.profile.id)
                });
                
            if (assessor.length > 0){
                //console.log(proposal.id, assessor)
                return true;
            }
            else
                return false;       
            
            return false;       
        }
    },
    mounted: function(){
        let vm = this;
        vm.fetchFilterLists();
        vm.fetchProfile();
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
        if(vm.is_external){
            var column = vm.$refs.proposal_datatable.vmDataTable.columns(8); //Hide 'Assigned To column for external'
            column.visible(false);
        }
        
    }
}
</script>
<style scoped>
</style>
