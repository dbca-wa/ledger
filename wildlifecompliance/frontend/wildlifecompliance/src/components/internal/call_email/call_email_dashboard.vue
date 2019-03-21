<template>
<div class="container" id="internalCallEmailDash">
    <div class="row">
    
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Call/Email status</label>
                <select class="form-control" v-model="filterCall">
                    <option value="All">All</option>
                    <option v-for="c in callChoices" :value="c">{{c}}</option>
                </select>
            </div>
        </div>
        <div class="col-md-3">
            <div class="form-group">
                <label for="">Call/Email classification</label>
                <select class="form-control" v-model="filterClassification">
                    <option value="All">All</option>
                    <option v-for="i in classificationChoices" :key="i.id">{{ i.name }}</option>
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
        filterCall: 'All',
        filterClassification: 'All',
        callChoices: [],
        classificationChoices: [],
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
                        data:"status",
                    },
                    {
                        data:"classification",
                        mRender: function(data, type, full) {
                            return data.name
                        }
                    },
                ],
                
                initComplete: function(){
                    console.log("test2");
                    var callColumn = vm.$refs.call_email_table.vmDataTable.columns(0);
                    callColumn.data().unique().sort().each( function ( d, j ) {
                        let call_choices = [];
                        $.each(d,(index,a) => {
                            a != null && call_choices.indexOf(a) < 0 ? call_choices.push(a): '';
                        })
                        vm.callChoices = call_choices;
                    });
                    var classificationColumn = vm.$refs.call_email_table.vmDataTable.columns(1);
                    classificationColumn.data().unique().sort().each( function ( d, j ) {
                        let classification_choices = [];
                        $.each(d,(index,a) => {
                            a != null && classification_choices.indexOf(a) < 0 ? classification_choices.push(a): '';
                        })
                        vm.classificationChoices = classification_choices;
                    });
                }
                
            },
            dtHeaders:["Call/Email Status","Classification"],
        }
    },
    
    watch: {
        filterCall: function() {
            let vm = this;
            
            if (vm.filterCall!= 'All') {
                vm.$refs.call_email_table.vmDataTable.columns(0).search(vm.filterCall, false).draw();
            } else {
                vm.$refs.call_email_table.vmDataTable.columns(0).search('').draw();
            }
        },
        filterClassification: function() {
            let vm = this;
            if (vm.filterClassification != 'All') {
                vm.$refs.call_email_table.vmDataTable.columns(1).search(vm.filterClassification).draw();
            } else {
                vm.$refs.call_email_table.vmDataTable.columns(1).search('').draw();
            }
        },
    },
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
    components: {
        datatable
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        }
    },
    methods: {},
}
</script>
