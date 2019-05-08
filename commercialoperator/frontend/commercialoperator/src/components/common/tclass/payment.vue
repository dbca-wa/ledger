<template lang="html">
    <div>
        Payment: <input type="text" name="payment1"><br>

        <Table :headers="headers" name="payment" label="Payment Form" id="id_payment"/>
        <Select :options="options" name="park" label="Park" id="id_park"/>
        <!-- <Table headers='{"Species": "text", "Quantity": "number", "Date": "date", "Taken": "checkbox"}' :readonly="readonly" name="payment" label="Payment Form" id="id_payment" :isRequired="isRequired"/> -->
    </div>
</template>

<script>
import TextArea from '@/components/forms/text-area.vue'
import Table from '@/components/forms/table.vue'
import Select from '@/components/forms/select.vue'
    export default {
        name:'payment',
        components:{
            TextArea,
            Table,
            Select,
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
                options: [
                    {'label': 'Nungarin', 'value': 'Nungarin'},
                    {'label': 'Ngaanyatjarraku', 'value': 'Ngaanyatjarraku'},
                    {'label': 'Cuballing', 'value': 'Cuballing'}
                ],
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
        }
    }
</script>

<style lang="css" scoped>
</style>

