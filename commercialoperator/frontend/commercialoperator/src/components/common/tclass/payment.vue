<template lang="html">
    <div>
        <form :action="payment_form_url" method="post" name="new_payment" enctype="multipart/form-data">
            <Table :headers="headers" :options="parks" name="payment" label="Payment Form" id="id_payment" :value="table_value"/>
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
                            <button class="btn btn-primary pull-right" style="margin-top:5px;" @click.prevent="calc_order()">Next</button>
                          </p>
                        </div>
                    </div>
                  </div>
                </div>
            </div>

        </form>

        <!--<Select :options="options" name="park" label="Park" id="id_park"/> -->
        <!-- <Table headers='{"Species": "text", "Quantity": "number", "Date": "date", "Taken": "checkbox"}' :readonly="readonly" name="payment" label="Payment Form" id="id_payment" :isRequired="isRequired"/> -->
        <CalcOrder ref="calc_order" :order_details="order_details" :proposal="proposal" @refreshFromResponse="refreshFromResponse"/>
    </div>
</template>

<script>
import TextArea from '@/components/forms/text-area.vue'
import Table from '@/components/forms/table.vue'
import Select from '@/components/forms/select.vue'
import CalcOrder from '@/components/common/proposal_calc_order.vue'
    export default {
        name:'payment',
        components:{
            TextArea,
            Table,
            Select,
            CalcOrder,
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
                this.$refs.calc_order.isModalOpen = true;
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
        },
        mounted:function () {
            let vm = this;
            vm.park_options();
        }
    }
</script>

<style lang="css" scoped>
</style>

