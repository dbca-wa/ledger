<template lang="html" id="pkCGADD">

   <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
      <div class="panel panel-default" id="applications">
        <div class="panel-heading" role="tab" id="applications-heading">
            <h4 class="panel-title">
                <a role="button" data-toggle="collapse" href="#applications-collapse"
                   aria-expanded="false" aria-controls="applications-collapse">
                    <h3>Add Mooring</h3>
                </a>
            </h4>
        </div>
        <div id="applications-collapse" class="panel-collapse collapse in" role="tabpanel"
             aria-labelledby="applications-heading">
            <div class="panel-body">
               <div class="col-lg-12">
                  <div class="row">
                    <div class="col-sm-12" style="overflow:visible;">
                    </div>
                     <campgroundAttr :campground="campground" :loadingDetails="loadingDetails" @updated="updateCampground" @save="sendData">
                     </campgroundAttr>
                  </div>
               </div>
            </div>
         </div>
      </div>
   </div>

</template>

<script>
import campgroundAttr from './campground-details.vue'
import {
    $,
    Moment,
    api_endpoints,
    helpers,
} from '../../hooks.js'
import alert from '../utils/alert.vue'
export default {
    name: 'addCampground',
    components: {
        campgroundAttr,
        alert
    },
    data: function() {
        return {
            campground:{
                address: {},
                images:[]
            },
            loadingDetails: false,
            title:'',
            errors:false,
            errorString: '',
        }
    },
    methods: {
       updateCampground: function(value){
            var vm = this;
            vm.campground = value;
        },
        sendData: function(url, method, reload, section){
            let vm = this;
            $.ajax({
                beforeSend: function(xhrObj) {
                    xhrObj.setRequestHeader("Content-Type", "application/json");
                    xhrObj.setRequestHeader("Accept", "application/json");
                },
                url: url,
                method: method,
                xhrFields: {
                    withCredentials: true
                },
                data: JSON.stringify(vm.campground),
                headers: {'X-CSRFToken': helpers.getCookie('csrftoken')},
                contentType: "application/x-www-form-urlencoded",
                dataType: 'json',
                success: function(data, stat, xhr) {
                    console.log("SUCCESS!!");
                    if (method == 'POST') {
                        vm.$router.push({
                            name: 'cg_detail',
                            params: {
                                id: data.id
                            }
                        });
                    }
                    else if (method == 'PUT') {
                        vm.showUpdate = true;
                    }
                  vm.$store.dispatch("updateAlert",{
                     visible:false,
                     type:"danger",
                     message: ""
                  });
                },
                error: function(resp) {
                    console.log("There was an error sending data.");
                    console.log(resp);
					vm.$store.dispatch("updateAlert",{
						visible:true,
						type:"danger",
						message: helpers.apiError(resp)
					});
                }
            });
        }
    },
    mounted:function () {
    }
}
</script>

<style lang="css">
.well{
   background-color: #fff;
}
.btn{
   margin-bottom: 10px;
}
</style>
