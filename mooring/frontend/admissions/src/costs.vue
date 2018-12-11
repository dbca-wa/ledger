<template lang="html" >
    <div id="admissionsCost" class="row">
        <div class="panel panel-default">
            <div class="panel-heading">
                <h4 class="panel-title">
                    <h3 style="display:inline;">Admission Fees</h3>
                </h4>
            </div>
            <div class="panel-body">
                <div class="col-lg-12">
                    <price-history  :addParkPrice="true" :dt_options="priceHistoryDt" :dt_headers="priceHistoryDtHeaders" :object_id="34" level='park' ></price-history>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {
    $,
    api_endpoints,
    helpers,
    select2,
    datetimepicker,
    Moment
}
from './hooks.js'
import alert from './utils/alert.vue'
import reason from './utils/reasons.vue'
import loader from './utils/loader.vue'
import priceHistory from './priceHistory/priceHistory.vue'
import { mapGetters } from 'vuex'

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
    name:"admissionsCost",
    el: '#admissionsCosts',
    data: function() {
        let vm = this;
        return {
            id:'',
            errors: false,
            errorString: '',
            loading: [],
            priceHistoryDt:{
                responsive: true,
                processing: true,
                ordering:true,
                deferRender: true,
                ajax: {
                    url: api_endpoints.park_price_history(),
                    dataSrc: ''
                },
                columns: [{
                    data:'id'
                    
                },  {
                    
                    data: 'period_start',
                    sType: 'extract-date',
                    mRender: function(data, type, full) {
                        return new Date(data).toLocaleDateString('en-GB');
                    }
                }, {
                    data: 'period_end',
                    sType: 'extract-date',
                    mRender: function(data, type, full) {
                        if(data){
                            return new Date(data).toLocaleDateString('en-GB');
                        } else {
                            return '-';
                        }   
                    }
                }, {
                    data: 'adult_cost',
                    orderable: false,
                    mRender: function(data, type, full){
                        if(data){
                            var column = "<td > $" + full.adult_cost + "(day)<br/>"
                            column += "$" + full.adult_overnight_cost + "(overnight)</td>";
                            return column;
                        } else {
                            return "";
                        }
                    }
                }, {
                    data: 'children_cost',
                    orderable: false,
                    mRender: function(data, type, full){
                        if(data){
                            var column = "<td > $" + full.children_cost + "(day)<br/>"
                            column += "$" + full.children_overnight_cost + "(overnight)</td>";
                            return column;
                        } else {
                            return "";
                        }
                    }
                }, {
                    data: 'infant_cost',
                    orderable: false,
                    mRender: function(data, type, full){
                        if(data){
                            var column = "<td > $" + full.infant_cost + "(day)<br/>"
                            column += "$" + full.infant_overnight_cost + "(overnight)</td>";
                            return column;
                        } else {
                            return "";
                        }
                    }
                }, {
                    data: 'family_cost',
                    orderable: false,
                    mRender: function(data, type, full){
                        if(data){
                            var column = "<td > $" + full.family_cost + "(day)<br/>"
                            column += "$" + full.family_overnight_cost + "(overnight)</td>";
                            return column;
                        } else {
                            return "";
                        }
                    }
                }, {
                    data: 'editable',
                    orderable: false,
                    mRender: function(data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editPrice' data-rate=\"__RATE__\" >Edit</a><br/>"
                            column += "<a href='#' class='deletePrice' data-rate=\"__RATE__\" >Delete</a></td>";
                            column = column.replace(/__RATE__/g, id);
                            return column;
                        }
                        else {
                            return "";
                        }
                    }
                }
                ],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            priceHistoryDtHeaders:[
                "ID", "Period Start", "Period End", "Adult", "Child", "Infant" ,"Family", "Action"
            ]

        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        isModalOpen: function() {
            return this.isOpen;
        },
        isLoading: function(){
            let vm = this;
            if ( vm.loading.length > 0){
                return true;
            }
        },
        ...mapGetters([
          'parks',
          'campsite_classes'
        ]),
    },
    watch: {
        
    },
    components: {
        alert,
        reason,
        loader,
        'price-history':priceHistory
    },
    methods: {
        close: function() {
            this.errors = false;
            this.errorString = '';
            this.isOpen = false;
        },
        goBack:function () {
            helpers.goBack(this);
        },
    },
    mounted: function() {
        var vm = this;
    }
};
</script>

<style lang="css" scoped>
    .editor{
        height: 200px;
    }
    .well:last-child{
        margin-bottom: 5px;
    }
</style>
