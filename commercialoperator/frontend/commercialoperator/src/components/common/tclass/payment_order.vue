<template lang="html">
    <div>
        <p> In payment_order </p>
        <v-select  :options="licences" @change="proposal_parks()" v-model="selected_licence" />
        <OrderTable ref="order_table" :expiry_date="selected_licence.expiry_date" :disabled="!parks_available" :headers="headers" :options="parks" name="payment" label="Payment Form" id="id_payment" />
        <!--
        <form :action="payment_form_url" method="post" name="new_payment" enctype="multipart/form-data">
            <div>
        -->
                <!--
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="new_payment_id" :value="1" />
                -->
        <!--
                <div class="row" style="margin-bottom: 50px">
                  <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5;">
                    <div class="navbar-inner">
                        <div class="container">
                          <p class="pull-right">
                            <button :disabled="!parks_available" class="btn btn-primary pull-right" style="margin-top:5px;" @click.prevent="calc_order()">Next</button>
                          </p>
                        </div>
                    </div>
                  </div>
                </div>
            </div>

        </form>
        -->

        <!--<Select :options="options" name="park" label="Park" id="id_park"/> -->
        <!-- <Table headers='{"Species": "text", "Quantity": "number", "Date": "date", "Taken": "checkbox"}' :readonly="readonly" name="payment" label="Payment Form" id="id_payment" :isRequired="isRequired"/> -->
        <!--
        <PaymentCalc ref="payment_calc" @refreshFromResponse="refreshFromResponse"/>
        -->
    </div>
</template>

<script>

import TextArea from '@/components/forms/text-area.vue'
import OrderTable from './order_table.vue'
import Select from '@/components/forms/select.vue'
//import CalcOrder from '@/components/common/payment_order.vue'
import PaymentCalc from './payment_calc.vue'
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
    export default {
        name:'payment',
        components:{
            TextArea,
            OrderTable,
            Select,
            PaymentCalc,
        },
        props:{
            proposal:{
                type: Object,
                required:true
            }
        },
        /*
        props:{
            proposal_id:{
                type:Number,
            },
            processing_status:{
                type:String,
            },
        },
        */
        data:function () {
            let vm = this;
            return{
                values: null,
                //headers: '{"Species": "text", "Quantity": "number", "Date": "date", "Taken": "checkbox"}',
                headers: '{"Park": "select", "Arrival": "date", "Adults": "number", "Children": "number", "Free of Charge":"number", "Cost":"total"}',
                _options: "[{'label': 'Nungarin', 'value': 'Nungarin'}, {'label': 'Nungarin_2', 'value': 'Nungarin_2'}]",
                _parks: [
                    {'label': 'Nungarin', 'value': 'Nungarin'},
                    {'label': 'Ngaanyatjarraku', 'value': 'Ngaanyatjarraku'},
                    {'label': 'Cuballing', 'value': 'Cuballing'}
                ],
                parks: [],
                land_parks: [],
                parks_available: false,
                licences: [],
                table_values: null,
                selected_licence:{
                    default:function () {
                        return {
                            value: String,
                            label: String,
                            expiry_date: String,
                        }
                    }
                },
                columns: ['a','b','c'],
                rows: [['a','b','c']],
            }
        },
        computed: {
            _headers: function() {
                return '{\"Species\": \"text\", \"Quantity\": \"number\", \"Date\": \"date\", \"Taken\": \"checkbox\"}';
                //return {"Species": "text", "Quantity": "number", "Date": "date", "Taken": "checkbox"};
            },
            /*
            "type": "table",
            "headers": "{\"Species\": \"text\", \"Quantity\": \"number\", \"Date\": \"date\", \"Taken\": \"checkbox\"}",
            "name": "Section2-0",
            "label": "The first table in section 2"
            */
        },
        watch:{
            options: function(){
                if (!vm.parks_available) {
                    this.$refs.order_table.options.length = 0;
                    this.$refs.order_table.table_values.length = 0;
                }
            }
        },
        methods:{
            resetTable: function(row) {
                /* Removes the rows, keeos the first and clears the td contents */
                let vm = this;
                //var nrows = $(".editable-table tbody tr").length;
                $(".editable-table tbody").find("tr:not(:first):not(:last)").remove(); // last row contains total price cell

                //vm.$refs.order_table.table.tbody = [["","","","","", ""]];
                //vm.$refs.order_table.table.tbody = [vm.$refs.order_table.init_row];
                vm.$refs.order_table.table.tbody = [vm.$refs.order_table.reset_row()];
                $(".editable-table .selected-tag").text('')
                $(".tbl_input").val('');
            },
            park_options: function() {
                let vm = this;
                vm.parks = [];
                for(var i = 0, length = vm.proposal.land_parks.length; i < length; i++) {
                    vm.parks.push({'label': vm.proposal.land_parks[i].park.name, 'value': vm.proposal.land_parks[i].park.id})
                }
            },
            calc_order: function(){
                //this.save_wo();
                let vm = this;
                var formData = new FormData(document.forms.new_payment);
                //vm.order_details = JSON.parse(formData.get('payment'))['tbody']
                vm.order_details = formData.get('payment')
                vm.$refs.payment_calc.order_details = vm.order_details;
                //vm.$refs.payment_calc.land_parks = vm.proposal.land_parks;
                vm.$refs.payment_calc.isModalOpen = true;
            },
            save: function(e) {
                let vm = this;
                let formData = new FormData(vm.form);
                //formData.append('marine_parks_activities', JSON.stringify(vm.proposal.marine_parks_activities))
                vm.$http.post(vm.payment_form_url,formData).then(res=>{
                    swal(
                        'Saved',
                        'Your proposal has been saved',
                        'success'
                    )
                },err=>{
                });
            },
            get_user_approvals: function(e) {
                let vm = this;
                //let formData = new FormData(vm.form);
                //formData.append('marine_parks_activities', JSON.stringify(vm.proposal.marine_parks_activities))
                vm.$http.get('/api/filtered_payments').then((res) => {
                    var licences = res.body;
                    for (var i in licences) {
                        vm.licences.push({value:licences[i].current_proposal, label:licences[i].lodgement_number, expiry_date:licences[i].expiry_date});
                    }
                    //vm.table_values = null;
                    console.log(vm.licences);
                },err=>{
                });
            },
            proposal_parks: function(e) {
                let vm = this;
                //let formData = new FormData(vm.form);
                //vm.$http.get('/api/proposal/49/proposal_parks').then((res)=>{
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposals,vm.selected_licence.value+'/proposal_parks')).then((res)=>{
                    vm.resetTable();
                    vm.land_parks = res.body.land_parks;
                    //vm.parks = [];
                    vm.parks = [];
                    for (var i in vm.land_parks) {
                        vm.parks.push({
                            value:vm.land_parks[i].park.id,
                            label:vm.land_parks[i].park.name,
                            prices:{
                                adult:vm.land_parks[i].park.adult,
                                child:vm.land_parks[i].park.child,
                                senior:vm.land_parks[i].park.senior
                            }
                        });
                    }
                    if (vm.parks.length==0) {
                        //document.getElementById("new_payment").reset();
                        //document.forms.new_payment.reset();
                        vm.parks_available = false;
                        vm.parks.push({value:0, label:'No parks available'});
                    } else{
                        vm.parks_available = true;
                    }
                    console.log(vm.land_parks);
                },err=>{
                });
            },


        },
        mounted:function () {
            let vm = this;
            //vm.park_options();
            vm.get_user_approvals();
        }
    }
</script>

<style lang="css" scoped>
</style>

