<template id="priceHistory">
<div class="row">
    <PriceHistoryDetail ref="historyModal" @addPriceHistory="addHistory()" @updatePriceHistory="updateHistory()" :title="getTitle" :priceHistory="price"></PriceHistoryDetail>
    <div class="well">
        <div class="col-sm-8">
            <h1>Price History</h1>
        </div>
        <div class="col-sm-4">
            <button @click="showHistory()" class="btn btn-primary pull-right table_btn">Add Price History</button>
        </div>
        <datatable ref="history_dt" :dtHeaders ="ch_headers" :dtOptions="ch_options" id="ph_table"></datatable>
     </div>
    <confirmbox id="deleteHistory" :options="deleteHistoryPrompt"></confirmbox>
</div>
</template>

<script>
import datatable from '../datatable.vue'
import confirmbox from '../confirmbox.vue'
import PriceHistoryDetail from './priceHistoryDetail.vue'
import {bus} from '../eventBus.js'
import {
    $,
    Moment,
    api_endpoints,
    helpers
}
from '../../../hooks.js'

export default {
    name: 'priceHistory',
    props: {
        datatableURL: {
            type: String,
            required: true
        },
        addPriceHistory: {
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
        PriceHistoryDetail
    },
    computed: {
        getTitle: function() {
            if (this.addPriceHistory){
                return 'Add Price History';
            }else{
                return 'Update Price History';
            }
        }
    },
    data: function() {
        let vm = this;
        return {
            campground: {},
            campsite:{},
            price: {},
            deleteHistory: null,
            deleteHistoryPrompt: {
                icon: "<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
                message: "Are you sure you want to Delete this closure Period",
                buttons: [{
                    text: "Delete",
                    event: "delete",
                    bsColor: "btn-danger",
                    handler: function() {
                        vm.deleteHistoryRecord(vm.deleteHistory);
                        vm.deleteHistory = null;
                    },
                    autoclose: true,
                }],
                id: 'deleteHistory'
            },
            ch_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                ajax: {
                    url: vm.datatableURL,
                    dataSrc: ''
                },
                columns: [{
                    data: 'range_start',
                    mRender: function(data, type, full) {
                        return Moment(data).format('MMMM Do, YYYY');
                    }

                }, {
                    data: 'range_end',
                    mRender: function(data, type, full) {
                        if (data) {
                            return Moment(data).add(1, 'day').format('MMMM Do, YYYY');
                        }
                        else {
                            return '';
                        }
                    }

                }, {
                    data: 'status'
                }, {
                    data: 'details'
                }, {
                    data: 'status'
                }, {
                    data: 'details'
                }, {
                    data: 'editable',
                    mRender: function(data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editRange' data-priceHistory=\"__ID__\" >Edit</a><br/><a href='#' class='deleteRange' data-priceHistory=\"__ID__\" >Delete</a></td>";
                            return column.replace(/__ID__/g, id);
                        }
                        else {
                            return "";
                        }
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            ch_headers: ['Period Start', 'Period End', 'Adult Price', 'Concession Price', 'Child Price', 'Comment', 'Action'],
        }
    },
    methods: {
        showHistory: function(){
            this.$refs.historyModal.isOpen = true;
        },
        deleteHistoryRecord: function(id) {
            var vm = this;
            var url = vm.closureURL(id);
            $.ajax({
                method: "DELETE",
                url: url,
            }).done(function(msg) {
                vm.$refs.history_dt.vmDataTable.ajax.reload();
            });
        },
        getAddURL: function() {
            if (this.addPriceHistory){
                return api_endpoints.opencloseCG(this.object_id);
            }else{
                return api_endpoints.opencloseCS(this.object_id);
            }
        },
        historyURL: function(id) {
            if (this.addPriceHistory){
                return api_endpoints.campground_status_history_detail(id);
            }else{
                return api_endpoints.campsite_status_history_detail(id);
            }
        },
        editHistory: function (id){
            let vm = this;
            $.ajax({
                url: vm.closureURL(id),
                method: 'GET',
                xhrFields: { withCredentials:true },
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.closure = data;
                    vm.showHistory();
                },
                error:function (resp){
                }
            });
        },
        addHistory: function() {
            this.sendData(this.getAddURL(),'POST');
        },
        updateHistory: function() {
            this.sendData(this.closureURL(this.$refs.historyModal.closure_id),'PUT');
        },
        sendData: function(url,method) {
            let vm = this;
            var data = vm.price;
            $.ajax({
                url: url,
                method: method,
                xhrFields: { withCredentials:true },
                data:JSON.stringify(data),
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.historyModal.close();
                    vm.$refs.history_dt.vmDataTable.ajax.reload();
                },
                error:function (resp){
                    var msg = helpers.apiError(resp);
                    vm.$refs.historyModal.errorString = msg;
                    vm.$refs.historyModal.errors = true;
                }
            });

        },
        addTableListeners: function() {
            let vm = this;
            vm.$refs.history_dt.vmDataTable.on('click','.editHistory', function(e) {
                e.preventDefault();
                var id = $(this).data('priceHistory');
                vm.editHistory(id);
            });
            vm.$refs.history_dt.vmDataTable.on('click','.deletHistory', function(e) {
                e.preventDefault();
                var id = $(this).data('priceHistory');
                vm.deleteHistory = id;
                bus.$emit('showAlert', 'deleteHistory');
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
