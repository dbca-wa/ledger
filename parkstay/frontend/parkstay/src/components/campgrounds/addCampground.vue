<template id="pkCgAdd">
    <bootstrapModal title="Add Campground" large=true ok="Add">
        <slot name="title">
            <h3>Add Campground</h3>
        </slot>


    </bootstrapModal>
</template>

<script>
import bootstrapModal from '../utils/bootstrap-modal.vue'

module.exports = {
    name: 'pkCgAdd',
    data: function() {
        return{
            status: '',
            //isModalOpen: false
        }
    },
    computed: {
        isModalOpen: function () {
            return this.$parent.isOpenAddCampground;
        }
    },
    components: { bootstrapModal },
    methods: {
        close: function (){
            this.$parent.isOpenAddCampground = false;
            this.status = '';
        },
        postAdd: function (){
            this.close();
        }
    }
}; 
</script>
