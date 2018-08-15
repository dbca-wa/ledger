<template id="closureHistory">
<div class="row">
    <Close ref="closeModal" @closeRange="addClosure()" @updateRange="updateClosure()" :title="getTitle" :statusHistory="closure"></Close>
    <div class="well">
        <div class="col-sm-8">
            <h1>Closure History</h1>
        </div>
        <div class="col-sm-4">
            <button @click="showClose()" class="btn btn-primary pull-right table_btn">Add Closure Period</button>
        </div>
        <datatable ref="closure_dt" :dtHeaders ="ch_headers" :dtOptions="ch_options" id="cg_table"></datatable>
     </div>
    <confirmbox id="deleteClosure" :options="deleteClosurePrompt"></confirmbox>
</div>
</template>

<script>
import datatable from './datatable.vue'
import confirmbox from './confirmbox.vue'
import Close from './closureHistory/close.vue'
import Open from './closureHistory/open.vue'
import {bus} from './eventBus.js'
import {
    $,
    Moment,
    api_endpoints,
    helpers
}
from '../../hooks.js'

export default {
    name: 'closureHistory',
    props: {
        datatableURL: {
            type: String,
            required: true
        },
        closeCampground: {
            type: Boolean,
            default: true
        },
        object_id: {
            type: Number,
            required: true
        }
    },
    components: {
        datatable,
        confirmbox,
        Close,
    },
    computed: {
        getTitle: function() {
            if (this.closeCampground){
                return '(Temporarily) Close Mooring';
            }else{
                return '(Temporarily) Close Mooring Site';
            }
        }
    },
    data: function() {
        let vm = this;
        return {
            campground: {},
            campsite:{},
            closure: {
                id:'',
                status: 1,
                reason: '',
                closure_reason: ''
            },
            deleteClosure: null,
            deleteClosurePrompt: {
                icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
                message: "Are you sure you want to Delete this closure Period",
                buttons: [{
                    text: "Delete",
                    event: "deleteClosure",
                    bsColor: "btn-danger",
                    handler: function() {
                        vm.deleteClosureRecord(vm.deleteClosure);
                        vm.deleteClosure = null;
                    },
                    autoclose: true,
                }],
                id: 'deleteClosure'
            },
            ch_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                ajax: {
                    url: vm.datatableURL,
                    dataSrc: ''
                },
                order: [],
                columns: [{
                    data: 'range_start',
                    mRender: function(data, type, full) {
                        return Moment(data).format('DD/MM/YYYY');
                    },
                    orderable: false

                }, {
                    data: 'range_end',
                    mRender: function(data, type, full) {
                        if (data) {
                            return Moment(data).add(1, 'day').format('DD/MM/YYYY');
                        }
                        else {
                            return '';
                        }
                    },
                    orderable: false

                }, {
                    mRender: function(data,type, full){
                        return full.reason ? full.reason: '';
                    },
                    orderable: false
                }, {
                    data: 'details',
                    orderable: false,
                    mRender: function(data,type,full){
                        return parseInt(full.closure_reason) == 1 ? data : '';
                    }
                }, {
                    data: 'editable',
                    mRender: function(data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editRange' data-range=\"__ID__\" >Edit</a><br/><a href='#' class='deleteRange' data-range=\"__ID__\" >Delete</a></td>";
                            return column.replace(/__ID__/g, id);
                        }
                        else {
                            return "";
                        }
                    },
                    orderable: false
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            ch_headers: ['Closure Start', 'Reopen', 'Closure Reason', 'Details', 'Action'],
        }
    },
    methods: {
        showClose: function(){
            this.$refs.closeModal.isOpen = true;
        },
        deleteClosureRecord: function(id) {
            var vm = this;
            var url = vm.closureURL(id);
            $.ajax({
                method: "DELETE",
                url: url,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}
            }).done(function(msg) {
                vm.$refs.closure_dt.vmDataTable.ajax.reload();
            });
        },
        getAddURL: function() {
            if (this.closeCampground){
                return api_endpoints.opencloseCG(this.object_id);
            }else{
                return api_endpoints.opencloseCS(this.object_id);
            }
        },
        closureURL: function(id) {
            if (this.closeCampground){
                return api_endpoints.campground_status_history_detail(id);
            }else{
                return api_endpoints.campsite_status_history_detail(id);
            }
        },
        editClosure: function (id){
            let vm = this;
            $.ajax({
                url: vm.closureURL(id),
                method: 'GET',
                xhrFields: { withCredentials:true },
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.closure = data;
                    vm.showClose();
                },
                error:function (resp){

                }
            });
        },
        addClosure: function() {
            this.sendData(this.getAddURL(),'POST');
        },
        updateClosure: function() {
            this.sendData(this.closureURL(this.$refs.closeModal.closure_id),'PUT');
        },
        sendData: function(url,method) {
            let vm = this;
            var data = vm.$refs.closeModal.statusHistory;
            $.ajax({
                url: url,
                method: method,
                xhrFields: { withCredentials:true },
                data: data,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.closeModal.close();
                    vm.$refs.closure_dt.vmDataTable.ajax.reload();
                },
                error:function (resp){
                    var msg = helpers.apiError(resp);
                    vm.$refs.closeModal.errorString = msg;
                    vm.$refs.closeModal.errors = true;
                }
            });

        },
        addTableListeners: function() {
            let vm = this;
            vm.$refs.closure_dt.vmDataTable.on('click','.editRange', function(e) {
                e.preventDefault();
                var id = $(this).data('range');
                vm.editClosure(id);
            });
            vm.$refs.closure_dt.vmDataTable.on('click','.deleteRange', function(e) {
                e.preventDefault();
                var id = $(this).data('range');
                vm.deleteClosure = id;
                bus.$emit('showAlert', 'deleteClosure');
            });
        },
    },
    mounted: function() {
        let vm = this;
        vm.addTableListeners();
    }
}
</script>

<style>
</style>
