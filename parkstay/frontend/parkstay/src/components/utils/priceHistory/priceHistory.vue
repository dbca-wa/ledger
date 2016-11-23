<template id="priceHistory">
<div class="row">
    <PriceHistoryDetail ref="historyModal" @addPriceHistory="addHistory()" @updatePriceHistory="updateHistory()" :title="getTitle" :priceHistory="price"></PriceHistoryDetail>
    <div class="well">
        <div class="col-sm-8">
            <h1>Price History</h1>
        </div>
        <div class="col-sm-4">
            <button v-show="showAddBtn" @click="showHistory()" class="btn btn-primary pull-right table_btn">Add Price History</button>
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
        showAddBtn: {
            type: Boolean,
            default: true
        },
        addPriceHistory: {
            type: Boolean,
            default: true
        },
        historyDeleteURL: {
            type: String,
            required: true
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
                message: "Are you sure you want to Delete this Price History Record",
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
                    data: 'date_start',
                    mRender: function(data, type, full) {
                        return Moment(data).format('MMMM Do, YYYY');
                    }

                }, {
                    data: 'date_end',
                    mRender: function(data, type, full) {
                        if (data) {
                            return Moment(data).add(1, 'day').format('MMMM Do, YYYY');
                        }
                        else {
                            return '';
                        }
                    }

                }, {
                    data: 'adult'
                }, {
                    data: 'concession'
                }, {
                    data: 'child'
                }, {
                    data: 'details',
                    mRender: function(data, type, full) {
                        if (data){
                            return data;
                        }
                        return '';
                    }
                }, {
                    data: 'editable',
                    mRender: function(data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editPrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\" >Edit</a><br/>"
                            if (full.deletable){
                                column += "<a href='#' class='deletePrice' data-date_start=\"__START__\"  data-date_end=\"__END__\"  data-rate=\"__RATE__\">Delete</a></td>";
                            }
                            column = column.replace(/__START__/g, full.date_start)
                            column = column.replace(/__END__/g, full.date_end)
                            column = column.replace(/__RATE__/g, full.rate_id)
                            return column
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
        deleteHistoryRecord: function(data) {
            var vm = this;
            var url = vm.historyDeleteURL;
            $.ajax({
                 beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                method: "POST",
                url: url,
                xhrFields: { withCredentials:true },
                data: JSON.stringify(data),
            }).done(function(msg) {
                vm.$refs.history_dt.vmDataTable.ajax.reload();
            });
        },
        getAddURL: function() {
            if (this.addPriceHistory){
                return api_endpoints.addPrice(this.object_id);
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
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
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
            vm.$refs.history_dt.vmDataTable.on('click','.editPrice', function(e) {
                e.preventDefault();
                var id = $(this).data('priceHistory');
                vm.editHistory(id);
            });
            vm.$refs.history_dt.vmDataTable.on('click','.deletePrice', function(e) {
                e.preventDefault();
                let btn = this;
                var data = {
                    'date_start':$(btn).data('date_start'),
                    'rate_id':$(btn).data('rate'),
                };
                $(btn).data('date_end') != null ? data.date_end = $(btn).data('date_end'): '';
                vm.deleteHistory = data;
        
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
