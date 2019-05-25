<template lang="html">
    <div>
        <div class="container">
            <div class="row"><div class="col-sm-12">
            <form action="/payment/46/" method="post" name="new_payment" @submit.prevent="validate()" novalidate>
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                
                <label>Licence</label><v-select :options="licences" @change="proposal_parks()" v-model="selected_licence" />
                <OrderTable ref="order_table" :expiry_date="selected_licence.expiry_date" :disabled="!parks_available" :headers="headers" :options="parks" name="payment" label="" id="id_payment" />

                <button :disabled="!parks_available" class="btn btn-primary pull-right" type="submit" style="margin-top:5px;">Proceed to Payment</button>
            </form>

            </div>
        </div>
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
            payment_url: function(){
                return `/api/payment/${to.params.proposal_id}.json`;
            },
            csrf_token: function() {
                return helpers.getCookie('csrftoken')
            },

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
            payment: function() {
                let vm = this;
                var proposal_id = vm.selected_licence.value;

                let formData = new FormData(vm.form);
                formData.append('tbody', JSON.stringify(vm.$refs.order_table.table.tbody))
                //vm.$http.post(vm.payment_form_url,formData).then(res=>{
                //vm.$http.post(`/api/payment/${vm.selected_licence.value}/park_payment/`, JSON.stringify(formData),{
                //vm.$http.post(`/api/payment/${proposal_id}/park_payment/`, formData,{
                vm.$http.post(`/payment/${proposal_id}/`, formData,{
                    emulateJSON:true
                }).then((res) => {
                //vm.$http.post(`/api/payment/${vm.selected_licence.value}/park_payment/`,formData).then(res=>{
                    swal(
                        'Payment',
                        'Your payment has been completed',
                        'success'
                    )
                },err=>{
                });
            },
            validate: function (e) {
                var isValid = true;
                var form = document.forms.new_payment;
//                var fields = $(form).find(':input');
//                $('.tooltip-err').tooltip("destroy");
//                $.each(fields, function(i, field) {
//                    $(field).removeClass('tooltip-err');
//                    $(field).closest('.form-group').removeClass('has-error');
//                    if ($(field).attr('required') == 'required' || $(field).attr('required') == 'true') {
//                        var inputStr = $(field).val();
//                        if (inputStr == "" || inputStr == null) {
//                             var errMsg = $(field).attr('data-error-msg') ? $(field).attr('data-error-msg') : "Field is required";
//                             $(field).closest('.form-group').addClass('has-error');
//                               $(field).focus();
//                               $(field).select();
//                               $(field).addClass('tooltip-err');
//                               $(field).tooltip()
//                                   .attr("data-original-title", errMsg)
//                             isValid = false;
//                         }
//                    }
//                });
                if (isValid) {
                    form.submit();
                }
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
                                adult:vm.land_parks[i].park.adult_price,
                                child:vm.land_parks[i].park.child_price,
                                //senior:vm.land_parks[i].park.senior
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

