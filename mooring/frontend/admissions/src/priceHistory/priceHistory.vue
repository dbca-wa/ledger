<template id="priceHistory">
<div class="row">
    <parkPriceHistory v-if="addParkPrice" ref="historyModal" @addParkPriceHistory="addParkHistory()" @updateParkPriceHistory="updateParkHistory()" :priceHistory="parkPrice" @cancel="closeHistory()"/>
    <PriceHistoryDetail v-else ref="historyModal" @addPriceHistory="addHistory()" @updatePriceHistory="updateHistory()" :priceHistory="price"></PriceHistoryDetail>
        <div class="col-sm-8">
            <h3>Price History</h3>
        </div>
        <div class="col-sm-4">
            <button v-show="showAddBtn" @click="showHistory()" class="btn btn-primary pull-right table_btn">Add Price History</button>
        </div>
        <datatable ref="history_dt" :dtHeaders ="dt_headers" :dtOptions="dt_options" id="ph_table"></datatable>
    <confirmbox id="deleteHistory" :options="deleteHistoryPrompt"></confirmbox>
</div>
</template>

<script>
import datatable from '../utils/datatable.vue'
import confirmbox from '../utils/confirmbox.vue'
import PriceHistoryDetail from './priceHistoryDetail.vue'
import parkPriceHistory from './parkPriceHistoryDetail.vue'
import {bus} from '../utils/eventBus.js'
import {
    $,
    Moment,
    api_endpoints,
    helpers,
    datetimepicker
}
from '../hooks.js'

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
        addParkPrice:{
            type: Boolean,
            default: function () {
                return false;
            }
        },
        level: {
            validator: function (value){
                var levels = ['campground','campsite_class','campsite','park'];
                return $.inArray(value,levels) > -1;
            },
            //required: true
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
        },
        dt_headers:{
            type:Array,
            default:function () {
               return ['Period Start', 'Period End', 'Adult Price', 'Child Price', 'Infant Price', 'Family Price', 'Action'];
            }
        }
    },
    components: {
        datatable,
        confirmbox,
        PriceHistoryDetail,
        parkPriceHistory
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
            parkPrice: {
                period_start:'',
                period_end:'',
                adult_cost:'',
                adult_overnight_cost:'',
                children_cost:'',
                children_overnight_cost:'',
                infant_cost:'',
                infant_overnight_cost:'',
                family_cost:'',
                family_overnight_cost:'',
                comments:'',
                reason:{id:1}
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

        }
    },
    methods: {
        getTitle: function() {
            if (this.price.id || this.price.original){
                return 'Update Price History';
            } else {
                return 'Add Price History';
            }
        },
        showHistory: function() {
            this.$refs.historyModal.title = this.getTitle();
            this.$refs.historyModal.isOpen = true;
        },
        closeHistory:function () {
            let vm =this;
            vm.price = {
                reason:'',
                details:''
            };
            vm.parkPrice ={
                reason:'',
                details:''
            };
            this.$refs.historyModal.close();
            this.$refs.historyModal.isOpen = false;
        },
        deleteHistoryRecord: function(data) {
            var vm = this;
            var url = null;
            if (vm.level == 'park') {
                url = api_endpoints.park_entry_rate(data.rate_id);
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
            else {
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
        getEditURL: function() {
            return api_endpoints.editCampsiteClassPrice(this.object_id);
        },
        updateHistory: function() {
            var vm=this;
            if (this.level == 'campsite') {
                this.price.campsite = this.object_id;
                this.sendData(this.getEditURL(),'PUT',JSON.stringify(vm.price));
            }
            else{
                this.sendData(this.getEditURL(),'POST',JSON.stringify(vm.price));
            }
        },
        addParkHistory: function() {
            var data = this.validateNewPrice(this.parkPrice)
            var start = this.parkPrice.period_start.split("/");
            this.parkPrice.period_start = start[2] + "-" + start[1] + "-" + start[0];
            if (this.parkPrice.period_end){
                var end = this.parkPrice.period_end.split("/") 
                this.parkPrice.period_end = end[2] + "-" + end[1] +"-" + end[0];
            }
            this.sendData(api_endpoints.park_add_price(),'POST',JSON.stringify(data));
        },
        validateNewPrice: function(data){
            if(!data.adult_cost || data.adult_cost == null || data.adult_cost == ''){
                data.adult_cost = '0.00';
            }
            if(!data.adult_overnight_cost || data.adult_overnight_cost == null || data.adult_overnight_cost == ''){
                data.adult_overnight_cost = '0.00';
            }
            if(!data.children_cost || data.children_cost == null || data.children_cost == ''){
                data.children_cost = '0.00'
            }
            if(!data.children_overnight_cost || data.children_overnight_cost == null || data.children_overnight_cost == ''){
                data.children_overnight_cost = '0.00'
            }
            if(!data.infant_cost || data.infant_cost == null || data.infant_cost == ''){
                data.infant_cost = '0.00'
            }
            if(!data.infant_overnight_cost || data.infant_overnight_cost == null || data.infant_overnight_cost == ''){
                data.infant_overnight_cost = '0.00'
            }
            if(!data.family_cost || data.family_cost == null || data.family_cost == ''){
                data.family_cost = '0.00'
            }
            if(!data.family_overnight_cost || data.family_overnight_cost == null || data.family_overnight_cost == ''){
                data.family_overnight_cost = '0.00'
            }
            if(!data.period_end || data.period_end == ""){
                delete data.period_end;
            }
            return data;
        },
        updateParkHistory: function() {
            this.sendData(api_endpoints.park_entry_rate(this.parkPrice.id),'PUT',JSON.stringify(this.parkPrice));
        },
        sendData: function(url,method,data) {
            let vm = this;
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                url: url,
                method: method,
                xhrFields: { withCredentials:true },
                data: data,
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.closeHistory();
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
                if (vm.level == 'park') {
                    vm.$http.get(api_endpoints.park_entry_rate(rate)).then((response)=>{
                        vm.parkPrice = response.body;
                        vm.$refs.historyModal.selected_rate= rate;
                        vm.price.period_start = Moment(vm.price.period_start ).format('YYYY-MM-DD');
                        vm.price.period_end != null ? vm.price.period_end : '';
                    },(error)=>{
                        console.log(error);
                    });
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
                    vm.deleteHistory = data;
                }
                else{
                    vm.deleteHistory = $(btn).data('rate');
                }
                bus.$emit('showAlert', 'deleteHistory');
            });
        },
    },
    mounted: function() {
        let vm = this;
        vm.addTableListeners();
        vm.$refs.history_dt.vmDataTable.order(0, "desc");
        
    }
}
</script>

<style>
</style>
