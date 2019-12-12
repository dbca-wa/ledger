<template>
<div class="container" id="internalDash">
    <div v-if="one_row_per_park">
        <ParkBookingDash level="internal"/>
    </div>
    <div v-else>
        <PaymentDash level="internal"/>
    </div>
</div>
</template>
<script>
import ParkBookingDash from '@common-utils/parkbookings_dashboard.vue'
import PaymentDash from '@common-utils/payments_dashboard.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
    name: 'ParkEntryFeesDashboard',
    data() {
        let vm = this;
        return {
            profile: {},
            one_row_per_park: false,
        }
    
    },
    watch: {},
    components: {
        ParkBookingDash,
        PaymentDash,
    },
    computed: {
        
    },
    methods: {
        fetchProfile: function(){
          let vm=this;
          vm.$http.get(api_endpoints.profile).then((response) => {
                    vm.profile = response.body
                    if (vm.profile.system_settings == null){ vm.one_row_per_park = false; }
                    else { vm.one_row_per_park = vm.profile.system_settings.one_row_per_park; }
        },(error) => {
            console.log(error);
        })

        },
    },
    mounted: function () {
        this.fetchProfile();
    }
}
</script>
