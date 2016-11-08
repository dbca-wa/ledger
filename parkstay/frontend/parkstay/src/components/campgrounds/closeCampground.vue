<template id="pkCgClose">
<bootstrapModal title="(Temporarily) close campground" :large=true ok="Add">
    <div class="modal-header">
        <h3>(Temporarily) Close Campground</h3>
    </div>

    <div class="modal-body">
        <form>
            <div class="form-group">
                <label for="range_start">Closure start: </label>
                <input type="text" class="form-control" id="range_start">
            </div>
            <div class="form-group">
                <label for="range_end">Closure end: </label>
                <input type="text" class="form-control" id="range_end">
            </div>
            <div class="form-group">
                <label for="reason">Reason: </label>
                <select class="form-control" id="reason">
                    <option value="1">Reason 1</option>
                    <option value="2">Reason 2</option>
                    <option value="3">Reason 3</option>
                </select>
            </div>
            <div class="form-group">
                <label for="details">Details: </label>
                <input type="textarea" class="form-control" id="details">
            </div>
        </form>
    </div>

</bootstrapModal>
</template>

<script>
import bootstrapModal from '../utils/bootstrap-modal.vue'
import {bus} from '../utils/eventBus.js'
module.exports = {
    name: 'pkCgClose',
    data: function() {
        return {
            status: '',
            id:'',
            //isModalOpen: false
        }
    },
    computed: {
        isModalOpen: function() {
            return this.$parent.isOpenCloseCG;
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
            this.close();
        }
    },
    mounted: function() {
        var vm = this;
        bus.$on('openclose', function(data){
            vm.status = data.status;
            vm.id = data.id;
        });
    }
};
</script>
