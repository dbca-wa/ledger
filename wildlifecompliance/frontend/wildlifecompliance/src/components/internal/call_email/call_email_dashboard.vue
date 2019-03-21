<template>
<div class="container" id="internalCallEmailDash">
    <div class="row">
        <!--
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Organisation</label>
                <select class="form-control" v-model="filterOrganisation">
                    <option value="All">All</option>
                    <option v-for="o in organisationChoices" :value="o">{{o}}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Applicant</label>
                <select class="form-control" v-model="filterApplicant">
                    <option value="All">All</option>
                    <option v-for="a  in applicantChoices" :value="a">{{a}}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Role</label>
                <select class="form-control" v-model="filterRole">
                    <option value="All">All</option>
                    <option v-for="r in roleChoices" :value="r">{{r}}</option>
                </select>
            </div>
        </div>
        -->
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Call/Email status</label>
                <select class="form-control" v-model="filterStatus">
                    <option value="All">All</option>
                    <!--
                    <option v-for="s in statusChoices" :value="s">{{s}}</option>
                    -->
                </select>
            </div>
        </div>
    </div>
    <datatable ref="call_email_table" id="call-email-table" :dtOptions="dtOptions" :dtHeaders="dtHeaders"></datatable>
</div>
</template>
<script>
import $ from 'jquery'
import datatable from '@vue-utils/datatable.vue'
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'CallEmailTableDash',
  data() {
    let vm = this;
    console.log("test1");
    return {
        // Filters
        filterStatus: 'All',
        callStatus: [],
        callClassification: [],
        dtOptions:{
                
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                
                responsive: true,
                processing:true,
                ajax: {
                    "url": helpers.add_endpoint_json(api_endpoints.call_email,'datatable_list'),
                    "dataSrc": '',
                },
                columns:[
                    {
                        data:"id",
                    },
                    {
                        data:"status",
                    },
                    {
                        data:"classification",
                    },
                ],
                initComplete: function(){
                    console.log("test2");
                    var statusColumn = vm.$refs.call_email_table.vmDataTable.columns(1);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusChoices = [];
                        $.each(d,(index,a) => {
                            a != null && statusChoices.indexOf(a) < 0 ? statusChoices.push(a): '';
                        })
                        vm.callStatus = statusChoices;
                    });
                    var classificationColumn = vm.$refs.call_email_table.vmDataTable.columns(2);
                    classificationColumn.data().unique().sort().each( function ( d, j ) {
                        let classificationChoices = [];
                        $.each(d,(index,a) => {
                            a != null && classificationChoices.indexOf(a) < 0 ? classificationChoices.push(a): '';
                        })
                        vm.callClassification = classificationChoices;
                    });
                }
            },
            dtHeaders:["Id", "Status","Classification"],
        }
    },
    /*
    watch: {
        filterOrganisation: function() {
            let vm = this;
            if (vm.filterOrganisation!= 'All') {
                vm.$refs.org_access_table.vmDataTable.columns(1).search(vm.filterOrganisation).draw();
            } else {
                vm.$refs.org_access_table.vmDataTable.columns(1).search('').draw();
            }
        },
        filterApplicant: function() {
            let vm = this;
            if (vm.filterApplicant != 'All') {
                vm.$refs.org_access_table.vmDataTable.columns(2).search(vm.filterApplicant).draw();
            } else {
                vm.$refs.org_access_table.vmDataTable.columns(2).search('').draw();
            }
        },
    },
    */
    /*   
    beforeRouteEnter: function(to, from, next) {
    console.log('BEFORE-ROUTE func()')
    //Vue.http.get(`/api/returns/${to.params.return_id}.json`).then(res => {
    Vue.http.get(`/api/call_email/datatable_list.json`).then(res => {
        next(vm => {
           vm.table = res.body;
           console.log(vm);
           console.log(vm.table);
        });
    }, err => {
      console.log(err);
    });
    },
    */
    components: {
        datatable
    },
    /*
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        }
    },
    */
    methods: {},
    /*
    mounted: function () {
    }
    */
}
</script>
