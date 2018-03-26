<template lang="html" >
    <div class="container" >
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Apply for a new licence
                            <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="pBody">
                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                            </a>
                        </h3>
                    </div>

                    <div class="panel-body collapse in" :id="pBody">
                        <form class="form-horizontal" name="personal_form" method="post">
                          
                            <div class="col-sm-12">
                                <div class = row>  
                                <label class="col-sm-4">Select the licence you want to apply for</label>
                                </div>
                              
                                
                                
                                <div v-for="(category,index) in licence_categories" class="radio">
                                    <div class ="row">
                                        <div class="col-sm-9" >  
                                            <input type="radio"  name="licence_category" v-model="licence_category"  :value="category.id" @change="handleChange($event,index)"> {{category.name}}
                                            <div class="row">

                                                <div v-if="true" class="col-8 col-sm-6">
                                                    <div v-for="type in category.activity_type" class="checkbox">
                                                        <!-- <div class="col-sm-8" style="background-color: lightcyan;"> -->
                                                        <input type="checkbox" name ="activity_type" :value="type.id" v-model="selected_activity_type"> {{type.name}}
                                                        
                                                        <div v-for="activity in type.activity" class="checkbox">
                                                            
                                                            <div class ="col-4 col-sm-6">
                                                                <input type="checkbox">{{activity.name}}
                                                            </div>

                                                        </div>
                                                        
                                                    </div>
                                                </div> 
                                            </div>
                                        </div>
                                    </div> 
                                </div>

                                
                                
                            </div>
                            <div class="col-sm-12">
                                <button :disabled="behalf_of == ''" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import Vue from 'vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
import utils from './utils'
export default {
  data: function() {
    let vm = this;
    return {
        licence_select : this.$route.params.licence_select,
        behalf_of : this.$route.params.org_select,
        "application": null,
        agent: {},
        licence_category: null ,
        selected_activity_type: [],
        activity_type_showing : [],
        organisations:null,
        licence_categories : {
            checked:false,
            activity_type:[]
        },
        "loading": [],
        form: null,
        pBody: 'pBody' + vm._uid,
    }
  },
  components: {
  },
  // watch:{
  //   licence_category: function(){
  //       this.activity_type_showing = true;

  //   }

  // },
  computed: {
    // isLoading: function() {
    //   return this.loading.length > 0
    // },
    // org: function() {
    //     let vm = this;
    //     if (vm.behalf_of != '' || vm.behalf_of != 'other'){
    //         return vm.profile.wildlifecompliance_organisations.find(org => parseInt(org.id) === parseInt(vm.behalf_of)).name;
    //     }
    //     return '';
    // }
  },
  methods: {
    submit: function() {
        let vm = this;

        swal({
            title: "Create Application",
            text: "Are you sure you want to create a application on behalf of "+vm.org+" ?",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        }).then(() => {
            vm.createApplication();
        },(error) => {
        });
    },

    handleChange: function(e,index){
        console.log(index)
        // this.activity_type_showing[category] = true
        this.
        console.log(this.activity_type_showing[index])

    },
    createApplication:function () {
        let vm = this;
        vm.$http.post('/api/application.json',{
            behalf_of: vm.behalf_of,
            licence_activity_type:vm.selected_activity_type,
            licence_category:vm.licence_category
        }).then(res => {
              vm.application = res.body;
              vm.$router.push({
                  name:"draft_application",
                  params:{application_id:vm.application.id}
              });
          },
          err => {
            console.log(err);
          });
    },
    
  },
   
  mounted: function() {
    let vm = this;
    vm.form = document.forms.new_application;
    console.log(vm.licence_select);
    console.log("Mounted",this.licence_select)

  },
  beforeRouteEnter:function(to,from,next){
        let initialisers = [

            utils.fetchLicenceCategories()
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {

                vm.licence_categories = data[0]
                console.log(vm.licence_categories)
                
                console.log()
            });
        });
    },
}
</script>

<style lang="css">
</style>
