<template id="booking_index_vue">
    <div class="row">
        <template v-if="showLoader">
            <loader :isLoading="showLoader" >{{loaderText}}...</loader>
        </template>
        <template v-else class="booking-router">
            <router-view></router-view>
        </template>
    </div>
</template>
<script>
import  {mapGetters,mapActions} from 'vuex'
import loader from '../utils/loader.vue';
export default{
    name: 'BookingIndex',
    props:{

    },
    data:function(){
        let vm = this;
        return{

        }
    },
    components:{
        loader
    },
    methods:{
    },
    computed: {
        ...mapGetters({
            showLoader: 'app_loader_state',
            loaderText: 'app_loader_text'
        })
    },
    mounted:function(){
        let vm = this;

    }
}
</script>
<style>
</style>

