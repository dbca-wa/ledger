<template lang="html">
    <div>
        <v-select  :options="licences" @change="proposal_parks()" v-model="selected_licence" />
        <form :action="payment_form_url" method="post" name="new_payment" enctype="multipart/form-data">
            <Table ref="order_table" :disabled="!parks_available" :headers="headers" :options="parks" name="payment" label="Payment Form" id="id_payment" :value="table_values"/>
            <div>
                <!--
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                <input type='hidden' name="new_payment_id" :value="1" />
                -->
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

        <!--<Select :options="options" name="park" label="Park" id="id_park"/> -->
        <!-- <Table headers='{"Species": "text", "Quantity": "number", "Date": "date", "Taken": "checkbox"}' :readonly="readonly" name="payment" label="Payment Form" id="id_payment" :isRequired="isRequired"/> -->
        <PaymentCalc ref="payment_calc" @refreshFromResponse="refreshFromResponse"/>
    </div>
</template>

<script>
import TextArea from '@/components/forms/text-area.vue'
import Table from '@/components/forms/table.vue'
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
            Table,
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
                headers: '{"Park": "select", "Arrival": "date", "Adults": "number", "Children": "number", "Free of Charge":"number"}',
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
                        vm.licences.push({value:licences[i].current_proposal, label:licences[i].lodgement_number});
                    }
                    vm.table_values.length = 0;
                    console.log(vm.licences);
                },err=>{
                });
            },
            proposal_parks: function(e) {
                let vm = this;
                //let formData = new FormData(vm.form);
                vm.$http.get(helpers.add_endpoint_json(api_endpoints.proposals,vm.selected_licence.value+'/proposal_parks')).then((res)=>{
                    vm.land_parks = res.body.land_parks;
                    //vm.parks = [];
                    vm.parks.length = 0;
                    for (var i in vm.land_parks) {
                        vm.parks.push({value:vm.land_parks[i].park.id, label:vm.land_parks[i].park.name});
                    }
                    if (vm.parks.length==0) {
                        //document.getElementById("new_payment").reset();
                        document.forms.new_payment.reset();
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

