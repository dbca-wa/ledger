<template id="priceHistory">
<div class="row">
    <PriceHistoryDetail ref="historyModal" @addPriceHistory="addHistory()" @updatePriceHistory="updateHistory()" :priceHistory="price"></PriceHistoryDetail>
    <div class="well">
        <div class="col-sm-8">
            <h1>Price History</h1>
        </div>
        <div class="col-sm-4">
            <button v-show="showAddBtn" @click="showHistory()" class="btn btn-primary pull-right table_btn">Add Price History</button>
        </div>
        <datatable ref="history_dt" :dtHeaders ="ch_headers" :dtOptions="dt_options" id="ph_table"></datatable>
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
        showAddBtn: {
            type: Boolean,
            default: true
        },
        addPriceHistory: {
            type: Boolean,
            default: true
        },
        level: {
            validator: function (value){
                var levels = ['campground','campsite_class','campsite'];
                return $.inArray(value,levels) > -1;   
            },
            required: true
        },
        historyDeleteURL: {
            type: String,
            //required: true
        },
        object_id: {
            type: Number,
            required: true
        },
        dt_options: {
            type: Object,
            required: true
        }
    },
    components: {
        datatable,
        confirmbox,
        PriceHistoryDetail
    },
    computed: {
    },
    data: function() {
        let vm = this;
        return {
            campground: {},
            campsite:{},
            price: {
                reason:''
            },
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
            ch_headers: ['Period Start', 'Period End', 'Adult Price', 'Concession Price', 'Child Price', 'Comment', 'Action'],
        }
    },
    methods: {
        getTitle: function() {
            if (this.price.id || this.price.original){
                return 'Update Price History';
            }else{
                return 'Add Price History';
            }
        },
        showHistory: function(){
            this.$refs.historyModal.title = this.getTitle();
            this.$refs.historyModal.isOpen = true;
        },
        deleteHistoryRecord: function(data) {
            var vm = this;
            var url = null;
            if (vm.level != 'campsite'){
                url = vm.historyDeleteURL;
                $.ajax({
                     beforeSend: function(xhrObj) {
                        xhrObj.setRequestHeader("Content-Type", "application/json");
                        xhrObj.setRequestHeader("Accept", "application/json");
                    },
                    method: "POST",
                    url: url,
                    xhrFields: { withCredentials:true },
                    data: JSON.stringify(data),
                    headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}
                }).done(function(msg) {
                    vm.$refs.history_dt.vmDataTable.ajax.reload();
                });
            }
            else{
                url = api_endpoints.campsiterate_detail(data);
                $.ajax({
                     beforeSend: function(xhrObj) {
                        xhrObj.setRequestHeader("Content-Type", "application/json");
                        xhrObj.setRequestHeader("Accept", "application/json");
                    },
                    method: "DELETE",
                    url: url,
                    xhrFields: { withCredentials:true },
                    headers: {'X-CSRFToken': helpers.getCookie('csrftoken')}
                }).done(function(msg) {
                    vm.$refs.history_dt.vmDataTable.ajax.reload();
                });
            }
        },
        getAddURL: function() {
            if (this.level == 'campground'){
                return api_endpoints.addPrice(this.object_id);
            }
            else if(this.level == 'campsite'){
                return api_endpoints.campsite_rate;
            }
            else{
                return api_endpoints.addCampsiteClassPrice(this.object_id);
            }
        },
        getEditURL: function() {
            if (this.level == 'campground'){
                return api_endpoints.editPrice(this.object_id);
            }
            else if (this.level == 'campsite'){
                return api_endpoints.campsiterate_detail(this.price.id);
            }
            else{
                return api_endpoints.editCampsiteClassPrice(this.object_id);
            }
        },
        addHistory: function() {
            if (this.level == 'campsite'){ this.price.campsite = this.object_id; }
            this.sendData(this.getAddURL(),'POST');
        },
        updateHistory: function() {
            if (this.level == 'campsite'){ 
                this.price.campsite = this.object_id; 
                this.sendData(this.getEditURL(),'PUT');
            }
            else{
                this.sendData(this.getEditURL(),'POST');
            }
        },
        sendData: function(url,method) {
            let vm = this;
            var data = vm.price;
            data.reason = parseInt(data.reason);
            console.log(vm.price);
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                url: url,
                method: method,
                xhrFields: { withCredentials:true },
                data: JSON.stringify(data),
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$refs.historyModal.close();
                    vm.price = {};
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
                var rate = $(this).data('rate');
                if (vm.level != 'campsite'){
                    var start = $(this).data('date_start');
                    var end = $(this).data('date_end');
                    var reason = $(this).data('reason');
                    var details = $(this).data('details');
                    vm.$refs.historyModal.selected_rate= rate;
                    vm.price.period_start = Moment(start).format('D/MM/YYYY');
                    vm.price.original = {
                        'date_start': start,
                        'rate_id': rate, 
                        'reason': reason,
                        'details': details
                    };
                    end != null ? vm.price.date_end : '';
                    vm.showHistory();
                }
                else{
                   $.get(api_endpoints.campsiterate_detail(rate), function(data) {
                        vm.price.period_start = data.date_start;
                        vm.price.id = data.id;
                        vm.$refs.historyModal.selected_rate = data.rate;
                        vm.showHistory();
                    }); 
                }
            });
            vm.$refs.history_dt.vmDataTable.on('click','.deletePrice', function(e) {
                e.preventDefault();
                let btn = this;
                if (vm.level != 'campsite'){
                    var data = {
                        'date_start':$(btn).data('date_start'),
                        'rate_id':$(btn).data('rate'),
                    };
                    $(btn).data('date_end') != null ? data.date_end = $(btn).data('date_end'): '';
                    vm.deleteHistory = data;
                }
                else{vm.deleteHistory = $(btn).data('rate');}
        
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
