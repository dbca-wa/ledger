<template lang="html" id="pkCGADD">

   <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
      <div class="panel panel-default" id="applications">
        <div class="panel-heading" role="tab" id="applications-heading">
            <h4 class="panel-title">
                <a role="button" data-toggle="collapse" href="#applications-collapse"
                   aria-expanded="false" aria-controls="applications-collapse">
                    <h3>Add Campground</h3>
                </a>
            </h4>
        </div>
        <div id="applications-collapse" class="panel-collapse collapse in" role="tabpanel"
             aria-labelledby="applications-heading">
            <div class="panel-body">
               <div class="col-lg-12">
                  <div class="row">
                     <campgroundAttr @create="create" :campground.sync="campground" >
                        <h1 slot="cg_name">My Slot</h1>
                     </campgroundAttr>
                  </div>
               </div>
            </div>
         </div>
      </div>
   </div>

</template>

<script>
import campgroundAttr from './campground-attr.vue'
import {
    $,
    Moment,
    api_endpoints
} from '../../hooks.js'

export default {
    name: 'addCampground',
    components: {
        campgroundAttr
    },
    data: function() {
        return {
            campground:{
                name:'',
                campground_type:'',
                address: {
                    telephone: "",
                    street: "",
                    email: "",
                    postcode: ""
                },
                contact: null,
                description:'',
                dog_permitted: '',
                check_in: '',
                check_out: '',
            },
            title:''
        }
    },
    methods: {
        create: function() {
            let vm = this;
            $.ajax({
                url: api_endpoints.campgrounds,
                method: 'POST',
                xhrFields: { withCredentials:true },
                data: vm.campground,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.$router.push({
                        name: 'cg_detail',
                        params: {
                            id: data.id
                        }
                    });
                },
                error:function (data){
                    console.log(data);
                }
            });
        },
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
