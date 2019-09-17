<template id="proposal_dashboard">
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
                        <!--
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
                        -->
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Status</label>
                                <select class="form-control" v-model="filterProposalStatus">
                                    <option value="All">All</option>
                                    <option v-for="s in approval_status" :value="s">{{s}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Expiry From</label>
                                <div class="input-group date" ref="proposalDateFromPicker">
                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedFrom">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Expiry To</label>
                                <div class="input-group date" ref="proposalDateToPicker">
                                    <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterProposalLodgedTo">
                                    <span class="input-group-addon">
                                        <span class="glyphicon glyphicon-calendar"></span>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div v-if="is_internal" class="col-md-3">
                            <div class="form-group">
                                <label/>
                            <div>
                                <button style="width:80%;" class="btn btn-primary top-buffer-s" :disabled="disabled" @click.prevent="createEClassLicence()">New E Class licence</button>
                            </div>
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
        <ApprovalExtend ref="approval_extend"  @refreshFromResponse="refreshFromResponse"></ApprovalExtend>
        <ApprovalCancellation ref="approval_cancellation"  @refreshFromResponse="refreshFromResponse"></ApprovalCancellation>
        <ApprovalSuspension ref="approval_suspension"  @refreshFromResponse="refreshFromResponse"></ApprovalSuspension>
        <ApprovalSurrender ref="approval_surrender"  @refreshFromResponse="refreshFromResponse"></ApprovalSurrender>
        <!--<EClassLicence ref="eclass_licence" :processing_status="proposal.processing_status" :proposal_id="proposal.id"></EClassLicence>-->
        <EClassLicence ref="eclass_licence"></EClassLicence>


    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import Vue from 'vue'
import ApprovalExtend from '../internal/approvals/approval_extend.vue'
import ApprovalCancellation from '../internal/approvals/approval_cancellation.vue'
import ApprovalSuspension from '../internal/approvals/approval_suspension.vue'
import ApprovalSurrender from '../internal/approvals/approval_surrender.vue'
import EClassLicence from '../internal/approvals/approval_eclass.vue'

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
    components:{
        datatable,
        ApprovalExtend,
        ApprovalCancellation,
        ApprovalSuspension,
        ApprovalSurrender,
        EClassLicence,
    },
    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'proposal-datatable-'+vm._uid,
            //Profile to check if user has access to process Proposal
            profile: {},
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
            approval_status:[],
            proposal_submitters: [],
            proposal_headers:[
                "Number","Application","Licence Type","Holder","Status","Start Date","Expiry Date","Licence","Action",
            ],
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
                        'render':function(data,type,full){
                        if(!vm.is_external){
                            var result = '';
                            var popTemplate = '';
                            var message = '';
                            let tick = '';
                            tick = "<i class='fa fa-exclamation-triangle' style='color:red'></i>"
                            result = '<span>' + full.lodgement_number + '</span>';
                            if(full.can_reissue){
                                if(!full.can_action){
                                    if(full.set_to_cancel){
                                        message = 'This Licence is marked for cancellation to future date';
                                    }
                                    if(full.set_to_suspend){
                                        message = 'This Licence is marked for suspension to future date';
                                    }
                                    if(full.set_to_surrender){
                                        message = 'This Licence is marked for surrendering to future date';
                                    }
                                    popTemplate = _.template('<a href="#" ' +
                                            'role="button" ' +
                                            'data-toggle="popover" ' +
                                            'data-trigger="hover" ' +
                                            'data-placement="top auto"' +
                                            'data-html="true" ' +
                                            'data-content="<%= text %>" ' +
                                            '><%= tick %></a>');
                                    result += popTemplate({
                                        text: message,
                                        tick: tick
                                    });

                                }
                            }
                            return result;
                        }
                        else { return full.lodgement_number }
                        },
                        'createdCell': helpers.dtPopoverCellFn,
                        name: "id, lodgement_number",
                    },
                    {
                        data: "linked_applications",
                        mRender:function (data,type,full) {
                            let applications = '';
                            _.forEach(data, function (item) {
                                applications += item + '<br>';
                            });
                            return applications;
                        },
                        name: "current_proposal__lodgement_number"

                    },


                    {
                        data: "application_type",
                        name: "current_proposal__application_type__name"
                    },
                    {
                        data: "applicant",
                        name: "org_applicant__organisation__name, proxy_applicant__email, proxy_applicant__first_name, proxy_applicant__last_name"
                    },
                    {data: "status"},
                    {
                        data: "start_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        },
                        searchable: false
                    },
                    {
                        data: "expiry_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        },
                        searchable: false
                    },
                    {
                        data: "licence_document",
                        mRender:function(data,type,full){
                            var result = '';
                            var popTemplate = '';
                            if(!full.migrated){
                            // return `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                            result= `<a href="${data}" target="_blank"><i style="color:red" class="fa fa-file-pdf-o"></i></a>`;
                            }
                            else if(full.migrated){
                               var icon = "<i class='fa fa-file-pdf-o' style='color:red'></i>"
                               var message= 'This is a migrated licence';
                               popTemplate = _.template('<a href="#" ' +
                                            'role="button" ' +
                                            'data-toggle="popover" ' +
                                            'data-trigger="hover" ' +
                                            'data-placement="top auto"' +
                                            'data-html="true" ' +
                                            'data-content="<%= text %>" ' +
                                            '><%= tick %></a>');
                                    result += popTemplate({
                                        text: message,
                                        tick: icon
                                    });
                            }
                            return result;
                        },
                        'createdCell': helpers.dtPopoverCellFn,
                        name: 'licence_document__name'
                    },
                    {
                        data: '',
                        mRender:function (data,type,full) {
                            let links = '';
                            if (!vm.is_external){
                                //if(vm.check_assessor(full)){
                                if(full.is_approver){
                                    if(full.can_reissue){
                                        links +=  `<a href='#${full.id}' data-reissue-approval='${full.current_proposal}'>Reissue</a><br/>`;
                                    }
                                }
                                if(full.is_assessor){
                                    // if(full.can_reissue){
                                    //     links +=  `<a href='#${full.id}' data-reissue-approval='${full.current_proposal}'>Reissue</a><br/>`;
                                    // }
                                    if(full.application_type=='E Class' && (full.status=='Current' || full.status=='Suspended')){
                                        if(full.can_extend){
                                            links +=  `<a href='#${full.id}' data-extend-approval='${full.id}'>Extend</a><br/>`;
                                        } else {
                                            links +=  `<a class='disabled' title='Licence has already been extended' style="color: grey;text-decoration: none;">Extend</a><br/>`;
                                        }
                                    }
                                    if(full.can_reissue && full.can_action){
                                        links +=  `<a href='#${full.id}' data-cancel-approval='${full.id}'>Cancel</a><br/>`;
                                        links +=  `<a href='#${full.id}' data-surrender-approval='${full.id}'>Surrender</a><br/>`;
                                    }
                                    if(full.status == 'Current' && full.can_action){
                                        links +=  `<a href='#${full.id}' data-suspend-approval='${full.id}'>Suspend</a><br/>`;
                                    }
                                    if(full.can_reinstate)
                                    {
                                        links +=  `<a href='#${full.id}' data-reinstate-approval='${full.id}'>Reinstate</a><br/>`;
                                    }
                                    links +=  `<a href='/internal/approval/${full.id}'>View</a><br/>`;
                                }
                                else{
                                    links +=  `<a href='/internal/approval/${full.id}'>View</a><br/>`;
                                }
                                if(full.renewal_document && full.renewal_sent){
                                  links +=  `<a href='${full.renewal_document}' target='_blank'>Renewal Notice</a><br/>`;  

                                }
                            }
                            else{//External Dashboard actions.
                                if (full.can_reissue) {
                                    links +=  `<a href='/external/approval/${full.id}'>View</a><br/>`;
                                    if(full.can_action){
                                        links +=  `<a href='#${full.id}' data-surrender-approval='${full.id}'>Surrender</a><br/>`;
                                        if(full.can_amend){
                                           links +=  `<a href='#${full.id}' data-amend-approval='${full.current_proposal}'>Amend</a><br/>`; 
                                       }                                        
                                    }
                                    if(full.renewal_document && full.renewal_sent && full.can_renew) {
                                    links +=  `<a href='#${full.id}' data-renew-approval='${full.current_proposal}'>Renew</a><br/>`;
                                    }                                    
                                }
                                else {
                                    links +=  `<a href='/external/approval/${full.id}'>View</a><br/>`;

                                }
                            }
                            return links;
                        },
                        searchable: false,
                        orderable: false,
                        name: ''
                    },
                    {data: "migrated", visible: false},
                    
                ],
                processing: true,
                /*
                initComplete: function () {
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
                */
            }
        }
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
                vm.$refs.proposal_datatable.vmDataTable.columns(3).search(vm.filterProposalStatus).draw();
            } else {
                vm.$refs.proposal_datatable.vmDataTable.columns(3).search('').draw();
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
        status: function(){
            //return this.is_external ? this.external_status : this.internal_status;
            return [];
        },
        is_external: function(){
            return this.level == 'external';
        },
        is_internal: function(){
            return this.level == 'internal';
        },
        is_referral: function(){
            return this.level == 'referral';
        }
    },
    methods:{
        createEClassLicence: function(){
            //this.save_wo();
            this.$refs.eclass_licence.isModalOpen = true;
        },

        fetchFilterLists: function(){
            let vm = this;

            vm.$http.get(api_endpoints.filter_list_approvals).then((response) => {
                vm.proposal_submitters = response.body.submitters;
                vm.approval_status = response.body.approval_status_choices;
            },(error) => {
                console.log(error);
            })
            //console.log(vm.regions);
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
            // Internal Reissue listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-reissue-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-reissue-approval');
                vm.reissueApproval(id);
            });

            // Internal Extend listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-extend-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-extend-approval');
                vm.extendApproval(id);
            });


            //Internal Cancel listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-cancel-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-cancel-approval');
                vm.cancelApproval(id);
            });

            //Internal Suspend listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-suspend-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-suspend-approval');
                vm.suspendApproval(id);
            });

            // Internal Reinstate listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-reinstate-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-reinstate-approval');
                vm.reinstateApproval(id);
            });

            //Internal/ External Surrender listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-surrender-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-surrender-approval');
                vm.surrenderApproval(id);
            });

            // External renewal listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-renew-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-renew-approval');
                vm.renewApproval(id);
            });

            // External amend listener
            vm.$refs.proposal_datatable.vmDataTable.on('click', 'a[data-amend-approval]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-amend-approval');
                vm.amendApproval(id);
            });

        },
        initialiseSearch:function(){
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
                    let val = original.expiry_date;

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
            return false;
        },

        reissueApproval:function (proposal_id) {
            let vm = this;
            let status= 'with_approver'
            let data = {'status': status}
            swal({
                title: "Reissue Licence",
                text: "Are you sure you want to reissue this licence?",
                type: "warning",
                confirmButtonText: 'Reissue licence',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.proposals,(proposal_id+'/reissue_approval')),JSON.stringify(data),{
                emulateJSON:true,
                })
                .then((response) => {
                    vm.$router.push({
                    name:"internal-proposal",
                    params:{proposal_id:proposal_id}
                    });
                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Reissue Licence",
                    text: error.body,
                    type: "error",
                    })
                });
            },(error) => {

            });
        },

        _extendApproval:function (approval_id) {
            let vm = this;
            let status= 'with_approver'
            let data = {'status': status}
            swal({
                title: "Renew Licence",
                //text: "Are you sure you want to extend this licence?",
                //type: "warning",
                text: "<input type='email' class='form-control' name='email' id='email'/>",
                type: "input",
                showCancelButton: true,
                showCancelButton: true,
                confirmButtonText: 'Extend licence',
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.approvals,(approval_id+'/approval_extend')),JSON.stringify(data),{
                emulateJSON:true,
                })
                .then((response) => {
                    vm.$router.push({
                    name:"internal-proposal",
                    params:{approval_id:approval_id}
                    });
                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Extend Licence",
                    text: error.body,
                    type: "error",
                    })
                });
            },(error) => {

            });
        },

        extendApproval: function(approval_id){
            this.$refs.approval_extend.approval_id = approval_id;
            this.$refs.approval_extend.isModalOpen = true;
        },

        reinstateApproval:function (approval_id) {
            let vm = this;
            let status= 'with_approver'
            //let data = {'status': status}
            swal({
                title: "Reinstate Licence",
                text: "Are you sure you want to reinstate this licence?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Reinstate licence',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.post(helpers.add_endpoint_json(api_endpoints.approvals,(approval_id+'/approval_reinstate')),{
                })
                .then((response) => {
                    swal(
                        'Reinstate',
                        'Your licence has been reinstated',
                        'success'
                    )
                    vm.$refs.proposal_datatable.vmDataTable.ajax.reload();
                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Reinstate Licence",
                    text: error.body,
                    type: "error",
                    })
                });
            },(error) => {

            });
        },

        renewApproval:function (proposal_id) {
            let vm = this;
            let status= 'with_approver'
            //let data = {'status': status}
            swal({
                title: "Renew Licence",
                text: "Are you sure you want to renew this licence?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Renew licence',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposals,(proposal_id+'/renew_approval')),{
                
                })
                .then((response) => {
                   let proposal = {}
                   proposal = response.body
                   vm.$router.push({
                    name:"draft_proposal",
                    params:{proposal_id: proposal.id}
                   });
                    
                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Renew Licence",
                    text: error.body,
                    type: "error",                   
                    })
                });
            },(error) => {

            });
        },

        amendApproval:function (proposal_id) {
            let vm = this;
            swal({
                title: "Amend Licence",
                text: "Are you sure you want to amend this licence?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Amend licence',
                //confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposals,(proposal_id+'/amend_approval')),{
                
                })
                .then((response) => {
                   let proposal = {}
                   proposal = response.body
                   vm.$router.push({
                    name:"draft_proposal",
                    params:{proposal_id: proposal.id}
                   });
                    
                }, (error) => {
                    console.log(error);
                    swal({
                    title: "Amend Licence",
                    text: error.body,
                    type: "error",                   
                    })

                });
            },(error) => {

            });
        },

        cancelApproval: function(approval_id){
            this.$refs.approval_cancellation.approval_id = approval_id;
            this.$refs.approval_cancellation.isModalOpen = true;
        },

        suspendApproval: function(approval_id){
            this.$refs.approval_suspension.approval = {};
            this.$refs.approval_suspension.approval_id = approval_id;
            this.$refs.approval_suspension.isModalOpen = true;
        },

        surrenderApproval: function(approval_id){
            this.$refs.approval_surrender.approval_id = approval_id;
            this.$refs.approval_surrender.isModalOpen = true;
        },

        refreshFromResponse: function(){
            this.$refs.proposal_datatable.vmDataTable.ajax.reload();
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
            vm.addEventListeners();
            vm.initialiseSearch();
        });
    }
}
</script>
<style scoped>
</style>
