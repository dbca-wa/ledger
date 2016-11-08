<template id="pkCgOpen">
<bootstrapModal title="Open campground" :large=true @ok="postAdd()">

    <div class="modal-body">
        <form class="form-horizontal">
            <p>Current Closure Period: </p>
            <div class="row">
                <div class="form-group">
                    <div class="col-md-2">
                        <label for="open_cg_range_start">Open per: </label>
                    </div>
                    <div class="col-md-4">
                        <div class='input-group date' id='open_cg_range_start'>
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
                        <label for="open_cg_reason">Reason: </label>
                    </div>
                    <div class="col-md-4">
                        <select v-model="formdata.reason" class="form-control" id="open_cg_reason">
                            <option value="1">Reason 1</option>
                            <option value="2">Reason 2</option>
                            <option value="3">Reason 3</option>
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
import { $, datetimepicker } from '../../hooks'
module.exports = {
    name: 'pkCgOpen',
    data: function() {
        return {
            status: '',
            id:'',
            formdata: {
                range_start: '',
                reason:'other',
                details: ''
            },
            picker: ''
            //isModalOpen: false
        }
    },
    computed: {
        isModalOpen: function() {
            return this.$parent.isOpenOpenCG;
        },
        requireDetails: function () {
            return (this.formdata.reason === 'other')? true: false;
        }
    },
    components: {
        bootstrapModal,
    },
    methods: {
        close: function() {
            this.$parent.isOpenOpenCG = false;
            this.status = '';
        },
        postAdd: function() {
            var data = this.formdata;
            var url = '';
            data.range_start = this.picker.data('DateTimePicker').date().format('DD/MM/YYYY');
            data.status = 0;
            console.log(data);
            $.ajax({
                url: url,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.days = data.days;
                    vm.classes = data.classes;
                    data.sites.forEach(function(el) {
                        el.showBreakdown = false;
                    });
                    vm.sites = data.sites;
                }
            });
            this.close();
        }
    },
    mounted: function() {
        var vm = this;
        bus.$on('openclose', function(data){
            vm.status = data.status;
            vm.id = data.id;
        });
        vm.picker = $('#open_cg_range_start');
        vm.picker.datetimepicker({
            format: 'DD/MM/YYYY'
        });
    }
};
</script>
