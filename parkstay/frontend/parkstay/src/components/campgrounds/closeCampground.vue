<template id="pkCgClose">
<bootstrapModal title="(Temporarily) close campground" :large=true @ok="postAdd()">

    <div class="modal-body">
        <form class="form-horizontal">
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_range_start">Closure start: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' id='close_cg_range_start'>
                            <input v-model="formdata.range_start" type='text' class="form-control" />
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_range_start">Closure end: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' id='close_cg_range_end'>
                            <input v-model="formdata.range_end" type='text' class="form-control" />
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_reason">Reason: </label>
                    </div>
                    <div class="col-md-4">
                        <select v-model="formdata.reason" class="form-control" id="open_cg_reason">
                            <option value="1">Closed due to natural disaster</option>
                            <option value="2">Closed for maintenance</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
            </div>
            <div v-show="requireDetails" class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_details">Details: </label>
                    </div>
                    <div class="col-md-5">
                        <textarea v-model="formdata.details" class="form-control" id="open_cg_details"></textarea>
                    </div>
                </div>
            </div>
        </form>
    </div>

</bootstrapModal>
</template>

<script>
import bootstrapModal from '../utils/bootstrap-modal.vue'
import {bus} from '../utils/eventBus.js'
import { $, datetimepicker,api_endpoints } from '../../hooks'
module.exports = {
    name: 'pkCgClose',
    data: function() {
        return {
            status: '',
            id:'',
            formdata: {
                range_start: '',
                range_end: '',
                reason:'other',
                details: ''
            },
            closeStartPicker: '',
            closeEndPicker: ''
        }
    },
    computed: {
        isModalOpen: function() {
            return this.$parent.isOpenCloseCG;
        },
        requireDetails: function () {
            return (this.formdata.reason === 'other')? true: false;
        }
    },
    components: {
        bootstrapModal
    },
    methods: {
        close: function() {
            this.$parent.isOpenCloseCG = false;
            this.status = '';
        },
        postAdd: function() {
            let vm = this;
            var data = this.formdata;
            //data.range_start = this.closeStartPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
            //data.range_end = this.closeEndPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
            data.status = vm.formdata.reason;
            console.log(data);
            $.ajax({
                url: api_endpoints.opencloseCG(vm.id),
                method: 'POST',
                xhrFields: { withCredentials:true },
                data: data,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.close();
                    bus.$emit('refreshCGTable');
                },
                error:function (data){
                    console.log(data);
                }
            });
        }
    },
    mounted: function() {
        var vm = this;
        bus.$on('openclose', function(data){
            vm.status = data.status;
            vm.id = data.id;
        });
        vm.closeStartPicker = $('#close_cg_range_start');
        vm.closeEndPicker = $('#close_cg_range_end');
        vm.closeStartPicker.datetimepicker({
            format: 'DD/MM/YYYY',
        });
        vm.closeEndPicker.datetimepicker({
            format: 'DD/MM/YYYY',
        });
        vm.closeStartPicker.on('dp.change', function(e){
            vm.formdata.range_start = vm.closeStartPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
        vm.closeEndPicker.on('dp.change', function(e){
            vm.formdata.range_end = vm.closeEndPicker.data('DateTimePicker').date().format('DD/MM/YYYY');
        });
    }
};
</script>
