<template lang="html">
    <div id="flsearch">
        <booking-picker></booking-picker>
    </div>

</template>

<script>
import bookingPicker from '../utils/bookingpicker.vue'
export default {
    name:"flsearch",
    data:function () {
        return{

        }
    },
    components:{
        "booking-picker": bookingPicker
    },
    mounted:function () {

    }
}
</script>

<style lang="css">
</style>
