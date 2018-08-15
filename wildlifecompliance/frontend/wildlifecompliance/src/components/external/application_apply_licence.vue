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
            id: null,
            name: null,
            activity_type: []
        }
        let count_total_licence_classes = 0
        let count_total_activity_types = 0
        let count_total_activities = 0
        let count_selected_activities_this_loop = 0
        let data = new FormData()
        vm.licence_type_name = ''

        // loop through level 1 and find selected licence class (radio option, only one)
        for(var i=0,_len1=vm.licence_classes.length;i<_len1;i++){

            // if licence class selected
            if(vm.licence_classes[i].checked){

                // set licence class information
                vm.licence_class.id         = vm.licence_classes[i].id
                vm.licence_class.name       = vm.licence_classes[i].name
                vm.licence_class.short_name = vm.licence_classes[i].short_name

                // initialise licence_type_name
                vm.licence_type_name        += vm.licence_classes[i].short_name + ' - '

                // loop through level 2 and find selected activity type (checkboxes, one or more)
                for(var j=0,_len2=vm.licence_classes[i].activity_type.length;j<_len2;j++){

                    // if activity type selected
                    if(vm.licence_classes[i].activity_type[j].selected){

                        // if this is not the first level 2 item, prepend licence_type_name with a comma
                        if(count_total_activity_types > 0){
                            vm.licence_type_name += ', '
                        }

                        // initialise activity list for selected activity type
                        vm.licence_class.activity_type[j].activity = []

                        // reset current loop total of selected activities for this activity type (level 3)
                        count_selected_activities_this_loop = 0

                        // loop through level 3 and find selected activity (checkboxes, one or more)
                        for(var k=0,_len3=vm.licence_classes[i].activity_type[j].activity.length;k<_len3;k++){

                            // if activity selected
                            if(vm.licence_classes[i].activity_type[j].activity[k].selected){

                                // if this is the first level 3 item, prepend licence_type_name with an open parentheses
                                // start of list in licence_type_name for the selected activity type
                                if(count_selected_activities_this_loop == 0){

                                    // add activity type to the licence_class.activity_type list
                                    // only do if at least one activity is selected (hence why it is in this loop)
                                    vm.licence_class.activity_type.push({
                                        id:         vm.licence_classes[i].activity_type[j].id,
                                        name:       vm.licence_classes[i].activity_type[j].name,
                                        short_name: vm.licence_classes[i].activity_type[j].short_name
                                    })
                                    vm.licence_type_name += vm.licence_classes[i].activity_type[j].short_name + ' ('
                                }

                                // if this is not the first level 3 item, prepend licence_type_name with a comma
                                if(count_selected_activities_this_loop > 0){
                                    vm.licence_type_name += ', '
                                }

                                // add activity to the licence_class.activity_type.activity list
                                vm.licence_class.activity_type[j].activity.push({
                                    id:     vm.licence_classes[i].activity_type[j].activity[k].id,
                                    name:   vm.licence_classes[i].activity_type[j].activity[k].short_name
                                })

                                // add activity short name to licence_type_name
                                vm.licence_type_name += vm.licence_classes[i].activity_type[j].activity[k].short_name

                                count_selected_activities_this_loop++;
                                count_total_activities++;

                                // end of selected activity loop
                        	}
                        }

                        // only if there is at least one activity selected for this activity type
                        if(count_selected_activities_this_loop > 0){
                            // list activities for each activity type inside parentheses for licence_type_name
                            vm.licence_type_name += ')'
                            count_total_activity_types++;
                        }

                        // end of selected activity type loop
                    }

                }

                count_total_licence_classes++; // this should always be 1 at end of full loop
                // end of selected licence class loop
            }
        }
        // TODO: if no selections, display error do not continue

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
