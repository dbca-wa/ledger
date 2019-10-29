<template id="proposal_dashboard">
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
                        <!--
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Region</label>
                                <select style="width:100%" class="form-control input-sm" multiple ref="filterRegion" >
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
                        -->
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterProposalStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in proposal_status" :value="s.value">{{s.name}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Submitter</label>
                                <select class="form-control" v-model="filterProposalSubmitter">
                                    <option value="All">All</option>
                                    <option v-for="s in proposal_submitters" :value="s.email">{{s.search_term}}</option>
                                </select>
                            </div>
                        </div>
                        <div v-if="is_external" class="col-md-6">
                            <router-link  style="margin-top:25px;" class="btn btn-primary pull-right" :to="{ name: 'apply_proposal' }">New Application</router-link>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="">Lodged From</label>
                            <div class="input-group date" ref="proposalDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Lodged To</label>
                            <div class="input-group date" ref="proposalDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                        <!-- <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Submitter</label>
                                <select class="form-control" v-model="filterProposalSubmitter">
                                    <option value="All">All</option>
                                    <option v-for="s in proposal_submitters" :value="s.email">{{s.search_term}}</option>
                                </select>
                            </div>
                        </div> -->
                    </div>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable v-if="level=='external'" ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_ex_options" :dtHeaders="proposal_ex_headers"/>
                            <datatable v-else ref="proposal_datatable" :id="datatable_id" :dtOptions="proposal_options" :dtHeaders="proposal_headers"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import "babel-polyfill"
import datatable from '@/utils/vue/datatable.vue'
import Vue from 'vue'
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
//require("babel-polyfill"); /* only one of 'import' or 'require' is necessary */
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
        },
    },
    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'proposal-datatable-'+vm._uid,
            //Profile to check if user has access to process Proposal
            profile: {},
            is_payment_admin: false,
            // Filters for Proposals
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
            external_status:[
                {value: 'draft', name: 'Draft'},
                {value: 'with_assessor', name: 'Under Review'},
                {value: 'approved', name: 'Approved'},
                {value: 'declined', name: 'Declined'},
                {value: 'discarded', name: 'Discarded'},
            ],
            internal_status:[
                {value: 'draft', name: 'Draft'},
                {value: 'with_assessor', name: 'With Assessor'},
                {value: 'on_hold', name: 'On Hold'},
                {value: 'with_qa_officer', name: 'With QA Officer'},
                {value: 'with_referral', name: 'With Referral'},
                {value: 'with_assessor_requirements', name: 'With Assessor (Requirements)'},
                {value: 'with_approver', name: 'With Approver'},
                {value: 'approved', name: 'Approved'},
                {value: 'declined', name: 'Declined'},
                {value: 'discarded', name: 'Discarded'},
            ],
            proposal_submitters: [],
            proposal_status: [],
            proposal_ex_headers:[
                "Number","Licence Type","Submitter","Applicant","Status","Lodged on","Action"
            ],
            proposal_ex_options:{
                autoWidth: false,
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
                        d.date_from = vm.filterProposalLodgedFrom != '' && vm.filterProposalLodgedFrom != null ? moment(vm.filterProposalLodgedFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.date_to = vm.filterProposalLodgedTo != '' && vm.filterProposalLodgedTo != null ? moment(vm.filterProposalLodgedTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
        		    }
                },
                dom: 'lBfrtip',
                buttons:[
                'excel', 'csv',],
                columns: [
                    {
                        data: "id",
                        mRender:function(data,type,full){
                            return full.lodgement_number;
                        },
                        name: "id, lodgement_number",
                    },
                    {
						data: "application_type",
						name: "application_type__name"
					},
                    {
                        data: "submitter",
                        mRender:function (data,type,full) {
                            if (data) {
                                return `${data.first_name} ${data.last_name}`;
                            }
                            return ''
                        },
                        name: "submitter__email",
                    },
                    {
                        data: "applicant",
                        name: "org_applicant__organisation__name, proxy_applicant__email, proxy_applicant__first_name, proxy_applicant__last_name"
                    },
                    {
                        data: "customer_status",
                        //mRender:function(data,type,full){
                        //    return vm.level == 'internal' ? full.processing_status: data; //Fix the issue with External dashboard Status dropdown shoing internal statuses.
                        //},
                        name: "customer_status",
                    },
                    {
                        data: "lodgement_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        },
                        searchable: false, // handles by filter_queryset override method - class ProposalFilterBackend
                    },
                    {
                        data: "",
                        mRender:function (data,type,full) {
                            let links = '';
                            if (!vm.is_external){
                                /*if(vm.check_assessor(full) && full.can_officer_process)*/
                                if(full.assessor_process){
                                    
                                    links +=  `<a href='/internal/proposal/${full.id}'>Process</a><br/>`;
                                
                            }
                                else{
                                    links +=  `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                                }
                            }
                            else{
                                if (full.can_user_edit) {
                                    links +=  `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                                    links +=  `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                                }
                                else if (full.can_user_view) {
                                    links +=  `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                                }
                            }
                            if (full.fee_paid){
                                links +=  `<a href='/cols/payments/invoice-pdf/${full.fee_invoice_reference}' target='_blank'><i style='color:red;' class='fa fa-file-pdf-o'></i>&nbsp #${full.fee_invoice_reference}</a><br/>`;
                            }
                            return links;
                        },
                        name: '',
                        searchable: false,
                        orderable: false
                    }

                ],
                processing: true,
                /*
                initComplete: function () {
                    // Grab submitters from the data in the table
                    var submittersColumn = vm.$refs.proposal_datatable.vmDataTable.columns(2);
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
                        vm.proposal_submitters = submitters;
                    });
                    // Grab Status from the data in the table
                    var statusColumn = vm.$refs.proposal_datatable.vmDataTable.columns(4);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.proposal_status = statusTitles;
                    });
                }
                */
            },
            proposal_headers:[
                "Number","Licence Type","Submitter","Applicant","Status","Lodged on","Assigned Officer","Action",
            ],
            proposal_options:{
                autoWidth: false,
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
                        d.date_from = vm.filterProposalLodgedFrom != '' && vm.filterProposalLodgedFrom != null ? moment(vm.filterProposalLodgedFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                        d.date_to = vm.filterProposalLodgedTo != '' && vm.filterProposalLodgedTo != null ? moment(vm.filterProposalLodgedTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
        		    }
                },
                dom: 'lBfrtip',
                buttons:[
                'excel', 'csv', ],
                columns: [
                    {
                        data: "id",
                        mRender:function(data,type,full){
                            return full.lodgement_number;
                        },
                        data: "id, lodgement_number"
                    },
                    {
						data: "application_type",
						name: "application_type__name"
					},
                    {
                        data: "submitter",
                        mRender:function (data,type,full) {
                            if (data) {
                                return `${data.first_name} ${data.last_name}`;
                            }
                            return ''
                        },
                        name: "submitter__email",
                    },
                    {
                        data: "applicant",
                        name: "org_applicant__organisation__name, proxy_applicant__email, proxy_applicant__first_name, proxy_applicant__last_name"
                    },
                    {
                        data: "processing_status",
                        //mRender:function(data,type,full){
                        //    return vm.level == 'external' ? full.customer_status: data;
                        //},
                        name: "processing_status",
                    },
                    {
                        data: "lodgement_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        },
                        searchable: false, // handles by filter_queryset override method - class ProposalFilterBackend
                    },
                    {
                        data: "assigned_officer",
                        name: "assigned_officer__first_name, assigned_officer__last_name",
                    },
                    {
                        data: '',
                        mRender:function (data,type,full) {
                            let links = '';
                            if (!vm.is_external){
                                /*if(vm.check_assessor(full) && full.can_officer_process)*/
                                if(full.assessor_process){   
                                        links +=  `<a href='/internal/proposal/${full.id}'>Process</a><br/>`;    
                            }
                                else{
                                    links +=  `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                                }
                            }
                            else{
                                if (full.can_user_edit) {
                                    links +=  `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                                    links +=  `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                                }
                                else if (full.can_user_view) {
                                    links +=  `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                                }
                            }
                            if (full.fee_paid){
                                if(vm.is_payment_admin){
                                links +=  `<a href='/ledger/payments/invoice/payment?invoice=${full.fee_invoice_reference}' target='_blank'>View Payment</a><br/>`;
                            }
                                links +=  `<a href='/cols/payments/invoice-pdf/${full.fee_invoice_reference}' target='_blank'><i style='color:red;' class='fa fa-file-pdf-o'></i>&nbsp #${full.fee_invoice_reference}</a><br/>`;
                            }
                            return links;
                        },
                        name: '',
                        searchable: false,
                        orderable: false
                    }

                ],
                processing: true,
                /*
                initComplete: function () {
                    // Grab submitters from the data in the table
                    var submittersColumn = vm.$refs.proposal_datatable.vmDataTable.columns(2);
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
                        vm.proposal_submitters = submitters;
                    });
                    // Grab Status from the data in the table
                    var statusColumn = vm.$refs.proposal_datatable.vmDataTable.columns(4);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.proposal_status = statusTitles;
                    });

                    // Fix the table rendering columns
                    vm.$refs.proposal_datatable.vmDataTable.columns.adjust().responsive.recalc();
                }
                */
            }
        }
    },
    components:{
        datatable
    },
    watch:{
        filterProposalSubmitter: function(){
            //this.$refs.proposal_datatable.vmDataTable.draw();
            let vm = this;
            if (vm.filterProposalSubmitter!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.columns(2).search(vm.filterProposalSubmitter).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.columns(2).search('').draw();
            }
        },
        filterProposalStatus: function() {
            let vm = this;
            if (vm.filterProposalStatus!= 'All') {
                vm.$refs.proposal_datatable.vmDataTable.columns(4).search(vm.filterProposalStatus).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.columns(4).search('').draw();
            }
        },
        filterProposalLodgedFrom: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        },
        filterProposalLodgedTo: function(){
            this.$refs.proposal_datatable.vmDataTable.draw();
        }
    },
    computed: {
        is_external: function(){
            return this.level == 'external';
        },
        is_referral: function(){
            return this.level == 'referral';
        },
        
    },
    methods:{
        fetchFilterLists: function(){
            let vm = this;

            //vm.$http.get('/api/list_proposal/filter_list/').then((response) => {
            vm.$http.get(api_endpoints.filter_list).then((response) => {
                vm.proposal_submitters = response.body.submitters;
                //vm.proposal_status = vm.level == 'internal' ? response.body.processing_status_choices: response.body.customer_status_choices;
                vm.proposal_status = vm.level == 'internal' ? vm.internal_status: vm.external_status;
            },(error) => {
                console.log(error);
            })
            //console.log(vm.regions);
        },

        discardProposal:function (proposal_id) {
            let vm = this;
            swal({
                title: "Discard Application",
                text: "Are you sure you want to discard this proposal?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Discard Application',
                confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.delete(api_endpoints.discard_proposal(proposal_id))
                .then((response) => {
                    swal(
                        'Discarded',
                        'Your proposal has been discarded',
                        'success'
                    )
                    vm.$refs.proposal_datatable.vmDataTable.ajax.reload();
                }, (error) => {
                    console.log(error);
                });
            },(error) => {

            });
        },
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
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-discard-proposal]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-discard-proposal');
                vm.discardProposal(id);
            });
        },
        initialiseSearch:function(){
            this.submitterSearch();
            this.dateSearch();
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
                vm.profile = response.body;
                vm.is_payment_admin=response.body.is_payment_admin;
                              
            },(error) => {
                console.log(error);
                
            })
        },

        check_assessor: function(proposal){
            let vm = this;
            if (proposal.assigned_officer)
                {
                    { if(proposal.assigned_officer== vm.profile.full_name)
                        return true;
                    else
                        return false;
                }
            }
            else{
                 var assessor = proposal.allowed_assessors.filter(function(elem){
                    return(elem.id=vm.profile.id)
                });
                
                if (assessor.length > 0)
                    return true;
                else
                    return false;
              
            }
            
        },
    },


    mounted: function(){
        this.fetchFilterLists();
        this.fetchProfile();
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
.dt-buttons{
    float: right;
}
</style>
