<template lang="html">
   <div class="well" id="cg_attr">
      <div class="col-sm-12">
       <div class="col-sm-4">
          <slot name="cg_img">
             <a href="#">
               <img class="img-responsive" src="//placehold.it/150x150/333333" alt="...">
             </a>
         </slot>
       </div>
       <div class="col-sm-8">
          <slot name="cg_name">
              <h3>CampGround Name</h3>
          </slot>
          <slot name="cg_description">
             <p>
                Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
             </p>
         </slot>
         <slot></slot>
       </div>
      </div>
      <div class="row" style="margin-top: 40px;">
         <div class="col-sm-8">
            <div class="form-group">
               <div class="col-sm-4 col-md-3 col-lg-2">
                  <label style="line-height: 2.5;">Price set at: </label>
               </div>
               <div class="col-sm-8 col-md-9 col-lg-10">
                  <select class="form-control" v-model="selected_price_set">
                     <option v-for="level in priceSet" :value="level">{{ level }}</option>
                  </select>
               </div>
            </div>
         </div>
         <div class="col-sm-4">
            <div class="col-sm-12">
               <div class="form-group pull-right">
                  <a href="#" class="btn btn-primary" @click="showAlert">Create</a>
                  <a href="#" class="btn btn-default">Cancel</a>
               </div>
            </div>
         </div>
      </div>
      <confirmBox :options="alertOptions" id="alert1" ></confirmBox>
   </div>
</template>

<script>
import confirmBox from '../utils/confirmbox.vue'
import {bus} from '../utils/eventBus.js'
export default {
    name: 'cg_attr',
    components:{
        confirmBox
    },
    data: function() {
        return {
            selected_price_set: this.priceSet[0],
            alertOptions:{
                icon:"<i class='fa fa-exclamation-triangle fa-2x text-danger' aria-hidden='true'></i>",
                message:"Are you sure you want to Delete!!!" ,
                buttons:[
                    {
                      text:"Delete",
                      event: "delete",
                      bsColor:"btn-danger",
                      handler:function(e) {
                          console.log('delete event fired');
                      },
                      autoclose:false
                    }
                ]
            }
        }
    },
    props: {
        priceSet: {
            default: function() {
                return ['Campsite level', 'Campground level'];
            }
        }
    },
    methods: {
        create: function() {
            this.$emit('create')
        },
        showAlert:function () {
            bus.$emit('showAlert','alert1');
        }
    }
}
</script>

<style lang="css">
</style>
