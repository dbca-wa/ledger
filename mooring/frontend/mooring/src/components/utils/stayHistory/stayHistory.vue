<template id="stayHistory">
<div class="row">
    <StayHistoryDetail :stay="stay" :mooringarea="mooringarea" ref="addMaxStayModal" @addCgStayHistory="addStayHistory()" @updateStayHistory="updateStayHistory()"></StayHistoryDetail>
    <div class="col-sm-12">
        <alert ref="retrieveStayAlert" :show.sync="retrieve_stay.error" type="danger" :duration="retrieve_stay.timeout">{{retrieve_stay.errorString}}</alert>
        <div class="col-sm-8" v-if="invent"/>
        <div class="col-sm-4" v-if="invent">
            <button @click="showAddStay()" class="btn btn-primary pull-right table_btn">Add Max Stay Period</button>
        </div>
        <datatable ref="addMaxStayDT" :dtHeaders ="msh_headers" :dtOptions="msh_options" id="stay_history"></datatable>
     </div>
    <confirmbox id="deleteStay" :options="deleteStayPrompt"></confirmbox>
</div>
</template>

<script>
import datatable from '../../utils/datatable.vue'
import alert from '../../utils/alert.vue'
import confirmbox from '../../utils/confirmbox.vue'
import StayHistoryDetail from './addMaximumStayPeriod.vue'
import {bus} from '../../utils/eventBus.js'
import {
    $,
    Moment,
    api_endpoints,
    helpers
}
from '../../../hooks.js'

$.extend($.fn.dataTableExt.oSort, {
    "extract-date-pre": function(value){
        if (value == '-'){
            return Infinity;
        }
        var date = value.split('/');
        return Date.parse(date[2] + '/' + date[1] + '/' + date[0])
        
    },
    "extract-date-asc": function(a, b){
        return ((a < b) ? -1 : ((a > b) ? 1 : 0));
    },
    "extract-date-desc": function(a, b){
        return ((a < b) ? 1 : ((a > b) ? -1 : 0));
    }
});

export default {
    name: 'stayHistory',
    props: {
        datatableURL: {
            type: String,
            required: true
        },
        object_id: {
            type: Number,
            required: true
        }
    },
    components: {
        StayHistoryDetail,
        alert,
        confirmbox,
        datatable
    },
    data: function() {
        let vm = this;
        return {
            mooringarea: {},
            invent: false,
            stay: {
                reason:''
            },
            deleteStay: null,
            deleteStayPrompt: {
                icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
                message: "Are you sure you want to Delete this stay Period",
                buttons: [{
                    text: "Delete",
                    event: "delete",
                    bsColor: "btn-danger",
                    handler: function() {
                        vm.deleteStayRecord(vm.deleteStay);
                        vm.deleteStay = null;
                    },
                    autoclose: true,
                }],
                id: 'deleteStay'
            },
            retrieve_stay: {
                error: false,
                timeout: 5000,
                errorString: ''
            },
            msh_headers: ['ID', 'Period Start', 'Period End', 'Maximum Stay(Nights)','Reason', 'Comment', 'Action'],
            msh_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                order: [],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                ajax: {
                    url: api_endpoints.campgroundStayHistory(vm.object_id),
                    dataSrc: ''
                },
                columns: [{
                    mRender: function(data, type, full){
                        return full.id;
                    }
                }, {
                    "data": "range_start",
                    sType: 'extract-date',
                    mRender: function(data, type, full) {
                        // return new Date(data).toLocaleDateString('en-GB');
                        return data;
                    }
                }, {
                    "data": "range_end",
                    sType: 'extract-date',
                    mRender: function(data, type, full) {
                        if(data){
                            // return new Date(data).toLocaleDateString('en-GB');
                            return data;
                        } else {
                            return '-';
                        }   
                    }
                }, {
                    "data": "max_days"
                },{
                    "data": "reason"
                }, {
                    "data": "details"
                }, {
                    "mRender": function(data, type, full) {
                        var id = full.id;
                        if (full.editable) {
                            var column = "<td ><a href='#' class='editStay' data-stay_period=\"__ID__\" >Edit</a>";
                            column += "<br/><a href='#' class='deleteStay' data-stay_period=\"__ID__\" >Delete</a></td>";
                            return column.replace(/__ID__/g, id);
                        }
                        return '';
                    }
                }]
            },
        }
    },
    methods: {
        showAddStay: function(create) {
            create = typeof create !== 'undefined' ? create : true;
            this.$refs.addMaxStayModal.isOpen = true;
            this.$refs.addMaxStayModal.create = create;
        },
        addStayHistory: function() {
            let vm = this;
            this.sendData(api_endpoints.campground_stay_history, 'POST')
        },
        updateStayHistory: function() {
            this.sendData(api_endpoints.campground_stay_history_detail(this.stay.id),'PUT');
        },
        deleteStayRecord: function(id) {
            var vm = this;
            var url = api_endpoints.campground_stay_history_detail(id);
            $.ajax({
                method: "DELETE",
                url: url,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
            }).done(function(msg) {
                vm.refreshMaxStayTable();
            });
        },
        refreshMaxStayTable: function() {
            this.$refs.addMaxStayDT.vmDataTable.ajax.reload();
        },
        fetchStay: function(id) {
            let vm = this;
            $.ajax({
                url: api_endpoints.campground_stay_history_detail(id),
                method: 'GET',
                xhrFields: {
                    withCredentials: true
                },
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.stay = data;
                    vm.showAddStay(false);
                },
                error: function(resp) {
                    vm.retrieve_stay.error = true;
                    vm.retrieve_stay.errorString = 'There was a problem trying to retrive this stay period';
                    setTimeout(function() {
                        vm.retrieve_stay.error = false;
                    }, vm.retrieve_stay.timeout);
                }
            });
        },
        sendData: function(url, method) {
            let vm = this;
            var data = this.stay;
            if (method == 'POST'){
                data.mooringarea = vm.object_id;
            }
            $.ajax({
                url: url,
                method: method,
                xhrFields: { withCredentials:true },
                data: data,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.addMaxStayModal.close();
                    vm.refreshMaxStayTable();
                },
                error:function (resp){
                    vm.errors = true;
                    vm.errorString = helpers.apiError(resp);
                }
            });

        },
        attachEventListenersMaxStayDT: function() {
            let vm = this;
            vm.$refs.addMaxStayDT.vmDataTable.on('click', '.editStay', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-stay_period');
                vm.fetchStay(id);
            });
            vm.$refs.addMaxStayDT.vmDataTable.on('click', '.deleteStay', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-stay_period');
                vm.deleteStay = id;
                bus.$emit('showAlert', 'deleteStay');
            });
        },
    },
    mounted: function() {
        let vm = this;
        vm.attachEventListenersMaxStayDT();
        setTimeout(function(){
            $.ajax({
                url: api_endpoints.profile,
                method: 'GET',
                dataType: 'json',
                success: function(data, stat, xhr){
                    if(data.is_inventory){
                        vm.invent = true;
                    }
                    if(!vm.invent){
                        vm.$refs.addMaxStayDT.vmDataTable.rows().every(function(){
                            var data = this.data();
                            data['editable'] = "";
                            this.data(data);
                        });
                    }
                }
            });
        },400);
    }
}
</script>
