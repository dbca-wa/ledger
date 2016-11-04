<template id="pkCgStatus">
    <bootstrapModal>
        <div class="modal-header">
            <h3>New Comment</h3>
        </div>

        <div class="modal-body">
            <label class="form-label">
                Comment
                <textarea rows="5" class="form-control"></textarea>
            </label>
        </div>

        <div class="modal-footer text-right">
            <button class="modal-default-button" @click="postAdd()">
                Post
            </button>
        </div>
    </bootstrapModal>
</template>

<script>
import bootstrapModal from '../utils/bootstrap-modal.vue'

module.exports = {
    name: 'pkCgStatus',
    data: function() {
        return{
            status: '',
            //isModalOpen: false
        }
    },
    computed: {
        isModalOpen: function () {
            return this.$parent.isOpenStatus;
        }
    },
    components: { bootstrapModal },
    methods: {
        close: function (){
            this.$parent.isOpenStatus = false;
            this.status = '';
        },
        postAdd: function (){
            this.close();
        }
    }
}; 
</script>
