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
                                            <input type="radio"  :id="category.id" name="licence_category" v-model="licence_categories.id"  :value="category.id" @change="handleRadioChange($event,index)"> {{category.name}} 
                                             
                                            <div class="row">

                                                
                                                <div  v-if="category.checked" class="col-sm-9"> 

                                                    <div v-for="(type,index1) in category.activity_type" class="checkbox">
                                                        <input type="checkbox" ref="selected_activity_type" name ="activity_type" :value="type.id" :id = "type.id" v-model="category.activity_type[index1].selected" @click="handleActivityTypeCheckboxChange(index,index1)"> {{type.name}} 
                                                        
                                                        <div v-if="type.selected">
                                                            <div v-for="(activity,index2) in type.activity" class="checkbox">
                                                                
                                                                <div class ="col-sm-6">
                                                                    <input type="checkbox" :value="activity.id" :id="activity.id" v-model="type.activity[index2].selected"@click="handleActivityCheckboxChange()" >{{activity.name}}
                                                                </div>

                                                            </div>
                                                        </div>
                                                        
                                                    </div>
                                                </div> 
                                                <div v-else="!radio_selected[index]" class="col-sm-4">
                                                    
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
        activity_type :{
            id:null,
            activity:[]
        },
        
        radio_selected : [],
        // selected_activity_type: [],
        selected_activity:[],
        activity_type_showing : [],
        organisations:null,
        licence_categories : {
            checked:false,
            activity_type:[
             { 
             	id:null,
                selected:false,
                activity:[]
             }
            ]
        },
        "loading": [],
        form: null,
        pBody: 'pBody' + vm._uid,
    }
  },
  components: {
  },
  watch:{
    // selected_activity_type: function(){
    //     this.activity_type.id = this.selected_activity_type;

    // }

  },
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
            text: "Are you sure you want to create a application ",
            type: "question",
            showCancelButton: true,
            confirmButtonText: 'Accept'
        }).then(() => {
            vm.createApplication();
        },(error) => {
        });
    },

    handleRadioChange: function(e,index){
        let vm=this
        for(var i=0,_len=vm.licence_categories.length;i<_len;i++){
            if(i===index){
                vm.licence_categories[i].checked = true;
            }else{
                for(var activity_type_index=0, len1=vm.licence_categories[i].activity_type.length; activity_type_index<len1; activity_type_index++){
                        if (vm.licence_categories[i].activity_type[activity_type_index].selected){
                            vm.licence_categories[i].activity_type[activity_type_index].selected=false;
                            for(var activity_index=0, len2=vm.licence_categories[i].activity_type[activity_type_index].activity.length; activity_index<len2; activity_index++){

                            }    
                        }
                }
                vm.licence_categories[i].checked=false;
            }

        }

    },
    handleActivityTypeCheckboxChange:function(index,index1){
        let vm = this
        var input = $(vm.$refs.selected_activity_type)[0];
        if(!vm.licence_categories[index].activity_type[index1].selected){
            for(var activity_index=0, len2=vm.licence_categories[index].activity_type[index1].activity.length; activity_index<len2; activity_index++){
                         vm.licence_categories[index].activity_type[index1].activity[activity_index].selected= false;
                            }    
        }
    },
    createApplication:function () {
        let vm = this;
        let category = JSON.stringify(vm.licence_categories)
        console.log("from areate application",category)
        vm.$http.post('/api/application.json',{
            behalf_of: vm.behalf_of,
            licence_activity_type:vm.selected_activity_type,
            licence_activity:vm.selected_activity,
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
 
  created:function(){
    console.log("created application apply licence")
  },
  beforeMount:function(){
    console.log("Before mpunt application apply licence")
  },
   
  mounted: function() {
    let vm = this;
    console.log("1inside mounted")
    vm.form = document.forms.new_application;
    console.log(vm.licence_select);
    console.log("Mounted",this.licence_select)
    console.log("2. Inside mounted end")

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
