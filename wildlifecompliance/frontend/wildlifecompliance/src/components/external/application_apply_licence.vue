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
                                <div class="row">
                                <label class="col-sm-4">Select the class of licence you wish to apply for:</label>
                                <div class="pull-right" style="font-size: 18px;"><strong>Estimated fee: {{application_fee | toCurrency}}</strong></div>
                                </div>

                                
                                <div class="margin-left-20">
                                <div v-for="(category,index) in licence_classes" class="radio">
                                    <div class ="row">
                                        <div class="col-sm-9" >  
                                            <input type="radio"  :id="category.id" name="licence_category" v-model="licence_classes.id"  :value="category.id" @change="handleRadioChange($event,index)"> {{category.short_name}}
                                             
                                            <div class="row">


                                                <div  v-if="category.checked" class="col-sm-9">

                                                    <div v-for="(type,index1) in category.activity_type" class="checkbox margin-left-20">
                                                        <input type="checkbox" ref="selected_activity_type" name ="activity_type" :value="type.id" :id = "type.id" v-model="category.activity_type[index1].selected" @click="handleActivityTypeCheckboxChange(index,index1)"> {{type.short_name}}

                                                        <div v-if="type.selected">
                                                            <div v-for="(activity,index2) in type.activity" class="checkbox activity-clear-left">
                                                                
                                                                <div class ="col-sm-12">
                                                                    <input type="checkbox" :value="activity.id" :id="activity.id" v-model="type.activity[index2].selected" @click="handleActivityCheckboxChange(index,index1,index2,$event)">{{activity.name}} ({{activity.base_fee}})
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

                                
                                
                            </div>
                            <div class="col-sm-12">
                                <button :disabled="behalf_of == '' && yourself == ''" @click.prevent="submit()" class="btn btn-primary pull-right">Continue</button>
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
        behalf_of_org : this.$route.params.org_select,
        yourself : this.$route.params.yourself,
        "application": null,
        agent: {},
        activity_type :{
            id:null,
            activity:[]
        },
        
        radio_selected : [],
        selected_activity:[],
        activity_type_showing : [],
        organisations:null,
        licence_classes : {
            checked:false,
            activity_type:[
             { 
             	id:null,
                selected:false,
                activity:[]
             }
            ]
        },
        licence_class:{
            id:null,
            activity_type:[]
        },
        licence_type_name: '',
        "loading": [],
        form: null,
        pBody: 'pBody' + vm._uid,
        application_fee: 0,
    }
  },
  components: {
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
        }).then((result) => {
            if (result.value) {
               vm.createApplication();
            }
        },(error) => {
        });
    },

    handleRadioChange: function(e,index){
        let vm=this
        for(var i=0,_len=vm.licence_classes.length;i<_len;i++){
            if(i===index){
                vm.licence_classes[i].checked = true;
            }else{
                for(var activity_type_index=0, len1=vm.licence_classes[i].activity_type.length; activity_type_index<len1; activity_type_index++){
                        if (vm.licence_classes[i].activity_type[activity_type_index].selected){
                            vm.licence_classes[i].activity_type[activity_type_index].selected=false;
                            for(var activity_index=0, len2=vm.licence_classes[i].activity_type[activity_type_index].activity.length; activity_index<len2; activity_index++){
                                vm.licence_classes[i].activity_type[activity_type_index].activity[activity_index].selected = false;
                                vm.application_fee = 0;
                            }    
                        }
                }
                vm.licence_classes[i].checked=false;
            }

        }
        console.log("This is the value to pass on",vm.licence_class);

    },
    handleActivityTypeCheckboxChange:function(index,index1){
        let vm = this
        var input = $(vm.$refs.selected_activity_type)[0];
        if(vm.licence_classes[index].activity_type[index1].selected){
            for(var activity_index=0, len2=vm.licence_classes[index].activity_type[index1].activity.length; activity_index<len2; activity_index++){
                         vm.licence_classes[index].activity_type[index1].activity[activity_index].selected= false;
                            }
        }
    },
    handleActivityCheckboxChange:function(index,index1,index2,event){
        let vm = this
        var activity = vm.licence_classes[index].activity_type[index1].activity[index2]
        if(event.target.checked){
            vm.application_fee += Number(activity.base_fee);
        } else {
            vm.application_fee -= Number(activity.base_fee);
        }
    },
    createApplication:function () {
        let vm = this;
        // clear out licence class
        vm.licence_class = {
            id:null,
            name:null,
            activity_type:[]
        }
        let index=0
        let count_activity_types = 0
        let count_activities = 0
        let data = new FormData()
        vm.licence_type_name = ''
        for(var i=0,_len=vm.licence_classes.length;i<_len;i++){
        	console.log('length of licence_classes',_len)
            // loop through level 1 and find selected
            if(vm.licence_classes[i].checked){
                vm.licence_class.id=vm.licence_classes[i].id
                vm.licence_class.name=vm.licence_classes[i].short_name
                vm.licence_class.short_name=vm.licence_classes[i].short_name
                vm.licence_type_name += vm.licence_classes[i].name + ' - '
                // loop through level 2 and find selected
                for(var j=0,_len1=vm.licence_classes[i].activity_type.length;j<_len1;j++){
                	console.log('length of activity type',_len1)
                    count_activities = 0
                    if(vm.licence_classes[i].activity_type[j].selected){
                        if(count_activity_types !=0 && count_activity_types<_len1){
                            vm.licence_type_name += ', '
                        }
                        // console.log("activity type selected",vm.licence_classes[i].activity_type[j].id)
                        vm.licence_class.activity_type.push({id:vm.licence_classes[i].activity_type[j].id,name:vm.licence_classes[i].activity_type[j].short_name,short_name:vm.licence_classes[i].activity_type[j].short_name})
                        vm.licence_class.activity_type[index].activity=[]
                        vm.licence_type_name += vm.licence_classes[i].activity_type[j].short_name + ' ('
                        // loop through level 3 and find selected
                        for(var k=0,_len2=vm.licence_classes[i].activity_type[j].activity.length;k<_len2;k++){
                            if(vm.licence_classes[i].activity_type[j].activity[k].selected){
                                if(count_activities!=0 && count_activities<_len2){
                                    vm.licence_type_name += ', '
                                }
                            	vm.licence_class.activity_type[index].activity.push({id:vm.licence_classes[i].activity_type[j].activity[k].id,name:vm.licence_classes[i].activity_type[j].activity[k].name})
                                vm.licence_type_name += vm.licence_classes[i].activity_type[j].activity[k].name
                                count_activities++;
                        	}
                        }
                        vm.licence_type_name += ')'
                        index++;
                        count_activity_types++;
                    }
                }
            }
        }
        data.org_applicant=vm.behalf_of_org
        data.licence_class_data=vm.licence_class
        data.licence_type_name=vm.licence_type_name
        data.application_fee=vm.application_fee
        console.log(' ---- application apply licence createApplication() ---- ');
        console.log(vm.application_fee)
        console.log(data.licence_type_name);
        console.log(data.licence_class)
        console.log(' ==== licence class data ==== ')
        console.log(JSON.stringify(data));
        vm.$http.post('/api/application.json',JSON.stringify(data),{emulateJSON:true}).then(res => {
              console.log(res.body);
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
 
  beforeRouteEnter:function(to,from,next){
        let initialisers = [

            utils.fetchLicenceClasses()
        ]
        Promise.all(initialisers).then(data => {
            next(vm => {

                vm.licence_classes = data[0]
            });
        });
    },
}
</script>

<style lang="css">
div.margin-left-20 {
    margin-left: 20px;
}
div.activity-clear-left {
    clear: left;
}
</style>
