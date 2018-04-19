<template id="proposal_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Approvals <small v-if="is_external">View existing approvals and ammed or renew them</small>
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
                                <select class="form-control" v-model="filterProposalStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in approval_status" :value="s">{{s}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Expiry From</label>
                            <div class="input-group date" ref="proposalDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Expiry To</label>
                            <div class="input-group date" ref="proposalDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
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
            filterProposalStatus: 'All',
            filterProposalLodgedFrom: '',
            filterProposalLodgedTo: '',
            filterProposalSubmitter: 'All',
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            approval_status:[],
            proposal_activityTitles : [],
            proposal_regions: [],
            proposal_submitters: [],
            proposal_headers:["Number","Region","Activity","Title","Holder","Status","Start Date","Expiry Date","Approval","Action"],
            proposal_options:{
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
                        mRender:function(data,type,full){
                            return full.reference;
                        }

                    },
                    {
                        data: "region",
                        'render': function (value) {
                            return helpers.dtPopover(value);
                        },
                        'createdCell': helpers.dtPopoverCellFn
                    },
                    {data: "activity"},
                    {
                        data: "title",
                        'render': function (value) {
                            return helpers.dtPopover(value);
                        },
                        'createdCell': helpers.dtPopoverCellFn
                    },
                    {data: "applicant"},
                    {data: "status"},
                    {
                        data: "start_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        }
                    },
                    {
                        data: "expiry_date",
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
                            if (!vm.is_external){
                                if(vm.check_assessor(full) && full.can_reissue){
                                    
                                    links +=  `<a href='#${full.id}' data-reissue-approval='${full.current_proposal}'>Reissue</a><br/>`;
                                    links +=  `<a href='/internal/proposal/${full.id}'>View</a><br/>`;

                            }
                                else{
                                    links +=  `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                                }
                            }
                            else{
                                if (full.can_user_edit) {
                                    links +=  `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                                    links +=  `<a href='#${full.id}' data-discard-proposal='${full.current_proposal}'>Discard</a><br/>`;
                                }
                                else if (full.can_user_view) {
                                    links +=  `<a href='/external/proposal/${full.current_proposal}'>View</a><br/>`;
                                }
                            }
                            return links;
                        }
                    }
                ],
                processing: true,
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
                    var statusColumn = vm.$refs.proposal_datatable.vmDataTable.columns(5);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.approval_status = statusTitles;
                    });
                    // Fix the table rendering columns
                    vm.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                }
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterProposalActivity: function() {
            let vm = this;
            if (vm.filterProposalActivity!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.columns(2).search(vm.filterProposalActivity).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.columns(2).search('').draw();
            }
        },
        filterProposalStatus: function() {
            let vm = this;
            if (vm.filterProposalStatus!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.columns(5).search(vm.filterProposalStatus).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.columns(5).search('').draw();
            }
        },
        filterProposalRegion: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalSubmitter: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalLodgedFrom: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalLodgedTo: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
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
        is_referral: function(){
            return this.level == 'referral';
        }
    },
    methods:{
        addEventListeners: function(){
            let vm = this;
            // Initialise Proposal Date Filters
            $(vm.$refs.proposalDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalDateToPicker).on('dp.change', function(e){
                if ($(vm.$refs.proposalDateToPicker).data('DateTimePicker').date()) {
                    vm.filterProposalLodgedTo =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.proposalDateToPicker).data('date') === "") {
                    vm.filterProposaLodgedTo = "";
                }
             });
            $(vm.$refs.proposalDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.proposalDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.proposalDateFromPicker).data('DateTimePicker').date()) {
                    vm.filterProposalLodgedFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.proposalDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.proposalDateFromPicker).data('date') === "") {
                    vm.filterProposalLodgedFrom = "";
                }
            });
            // End Proposal Date Filters
            // External Discard listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-reissue-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-reissue-approval');
                vm.reissueApproval(id);
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
                    let from = vm.filterProposalLodgedFrom;
                    let to = vm.filterProposalLodgedTo;
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

        fetchProfile: function(){
            let vm = this;
            Vue.http.get(api_endpoints.profile).then((response) => {
                vm.profile = response.body
                              
            },(error) => {
                console.log(error);
                
            })
        },

        check_assessor: function(proposal){
            let vm = this;         
            
            var assessor = proposal.allowed_assessors.filter(function(elem){
                    return(elem.id=vm.profile.id)
                });
                
            if (assessor.length > 0)
                return true;
            else
                return false;       
        },

        reissueApproval:function (proposal_id) {
            let vm = this;
            let status= 'with_approver'
            let data = {'status': status}
            swal({
                title: "Reissue Approval",
                text: "Are you sure you want to reissue this approval?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Reissue approval',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(proposal_id+'/reissue_approval')),JSON.stringify(data),{
                emulateJSON:true,
                })
                .then((response) => {
                    swal(
                        'Reissue',
                        'Your approval has been reissued',
                        'success'
                    )
                    vm.$router.push({
                    name:"internal-proposal",
                    params:{proposal_id:proposal_id}
                    });
                }, (error) => {
                    console.log(error);
                });
            },(error) => {

            });
        },


    },
    mounted: function(){
        this.fetchProfile();
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
