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
                                </div>

                                
                                <div class="margin-left-20">
                                <div v-for="(category,index) in licence_categories" class="radio">
                                    <div class ="row">
                                        <div class="col-sm-9" >  
                                            <input type="radio"  :id="category.id" name="licence_category" v-model="licence_categories.id"  :value="category.id" @change="handleRadioChange($event,index)"> {{category.short_name}}
                                             
                                            <div class="row">


                                                <div  v-if="category.checked" class="col-sm-9">

                                                    <div v-if="!(behalf_of_org != '' && type.not_for_organisation == true)" v-for="(type,index1) in category.activity" class="checkbox margin-left-20">
                                                        <input type="checkbox" ref="selected_activity_type" name ="activity" :value="type.id" :id = "type.id" v-model="category.activity[index1].selected" @click="handleActivityCheckboxChange(index,index1)"> {{type.short_name}}

                                                        <div v-if="type.selected">
                                                            <div v-for="(purpose,index2) in type.purpose" class="checkbox purpose-clear-left">

                                                                <div class ="col-sm-12">
                                                                    <input type="checkbox" :value="purpose.id" :id="purpose.id" v-model="type.purpose[index2].selected" @click="handlePurposeCheckboxChange(index,index1,index2,$event)">{{purpose.name}}<span> ({{purpose.base_application_fee}} + {{purpose.base_licence_fee}})</span>
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
                                <button :disabled="behalf_of == '' && yourself == ''" @click.prevent="submit()" class="btn btn-primary pull-right" style="margin-left: 10px;">Continue</button>
                                <div class="pull-right" style="font-size: 18px;">
                                    <strong>Estimated application fee: {{application_fee | toCurrency}}</strong><br>
                                    <strong>Estimated licence fee: {{licence_fee | toCurrency}}</strong><br>
                                </div>
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
        behalf_of_proxy : this.$route.params.proxy_select,
        behalf_of: '',
        yourself : this.$route.params.yourself,
        "application": null,
        agent: {},
        activity :{
            id:null,
            purpose:[]
        },
        
        radio_selected : [],
        selected_activity:[],
        activity_type_showing : [],
        organisations:null,
        licence_categories : {
            checked:false,
            activity:[
             { 
             	id:null,
                selected:false,
                purpose:[]
             }
            ]
        },
        licence_category:{
            id:null,
            activity:[]
        },
        "loading": [],
        form: null,
        pBody: 'pBody' + vm._uid,
        application_fee: 0,
        licence_fee: 0,
    }
  },
  components: {
  },
  computed: {
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
        for(var i=0,_len=vm.licence_categories.length;i<_len;i++){
            if(i===index){
                vm.licence_categories[i].checked = true;
            }else{
                for(var activity_type_index=0, len1=vm.licence_categories[i].activity.length; activity_type_index<len1; activity_type_index++){
                        if (vm.licence_categories[i].activity[activity_type_index].selected){
                            vm.licence_categories[i].activity[activity_type_index].selected=false;
                            for(var activity_index=0, len2=vm.licence_categories[i].activity[activity_type_index].purpose.length; activity_index<len2; activity_index++){
                                vm.licence_categories[i].activity[activity_type_index].purpose[activity_index].selected = false;
                                vm.application_fee = 0;
                                vm.licence_fee = 0;
                            }    
                        }
                }
                vm.licence_categories[i].checked=false;
            }

        }
        console.log("This is the value to pass on",vm.licence_category);

    },
    handleActivityCheckboxChange:function(index,index1){
        let vm = this
        var input = $(vm.$refs.selected_activity_type)[0];
        if(vm.licence_categories[index].activity[index1].selected){
            for(var activity_index=0, len2=vm.licence_categories[index].activity[index1].purpose.length; activity_index<len2; activity_index++){
                         vm.licence_categories[index].activity[index1].purpose[activity_index].selected= false;
                            }
        }
    },
    handlePurposeCheckboxChange:function(index,index1,index2,event){
        let vm = this
        var purpose = vm.licence_categories[index].activity[index1].purpose[index2]
        if(event.target.checked){
            vm.application_fee += Number(purpose.base_application_fee);
            vm.licence_fee += Number(purpose.base_licence_fee);
        } else {
            vm.application_fee -= Number(purpose.base_application_fee);
            vm.licence_fee -= Number(purpose.base_licence_fee);
        }
    },
    createApplication:function () {
        let vm = this;
        // clear out licence class
        vm.licence_category = {
            id: null,
            name: null,
            activity: []
        }
        let licence_purposes = [];
        let count_total_licence_categories = 0
        let count_total_activities = 0
        let count_total_purposes = 0
        let count_selected_purposes_this_loop = 0
        let data = new FormData()

        // loop through level 1 and find selected licence class (radio option, only one)
        for(var i=0,_len1=vm.licence_categories.length;i<_len1;i++){

            // if licence class selected
            if(vm.licence_categories[i].checked){

                // set licence class information
                vm.licence_category.id         = vm.licence_categories[i].id
                vm.licence_category.name       = vm.licence_categories[i].name
                vm.licence_category.short_name = vm.licence_categories[i].short_name

                // loop through level 2 and find selected activity type (checkboxes, one or more)
                for(var j=0,_len2=vm.licence_categories[i].activity.length;j<_len2;j++){

                    // if activity type selected
                    if(vm.licence_categories[i].activity[j].selected){

                        // reset current loop total of selected purposes for this activity type (level 3)
                        count_selected_purposes_this_loop = 0

                        // loop through level 3 and find selected activity (checkboxes, one or more)
                        for(var k=0,_len3=vm.licence_categories[i].activity[j].purpose.length;k<_len3;k++){

                            // if activity selected
                            if(vm.licence_categories[i].activity[j].purpose[k].selected){

                                // if this is the first level 3 item
                                // start of list for the selected activity type
                                if(count_selected_purposes_this_loop == 0){

                                    // add activity type to the licence_category.activity list
                                    // only do if at least one activity is selected (hence why it is in this loop)
                                    vm.licence_category.activity.push({
                                        id:         vm.licence_categories[i].activity[j].id,
                                        name:       vm.licence_categories[i].activity[j].name,
                                        short_name: vm.licence_categories[i].activity[j].short_name
                                    })

                                    // initialise activity list for selected activity type
                                    vm.licence_category.activity[count_total_activities].purpose = []
                                }

                                // add activity to the licence_category.activity.activity list
                                vm.licence_category.activity[count_total_activities].purpose.push({
                                    id:     vm.licence_categories[i].activity[j].purpose[k].id,
                                    name:   vm.licence_categories[i].activity[j].purpose[k].name,
                                    short_name:   vm.licence_categories[i].activity[j].purpose[k].short_name
                                });

                                count_selected_purposes_this_loop++;
                                count_total_purposes++;

                                licence_purposes.push(vm.licence_categories[i].activity[j].purpose[k].id);
                                // end of selected activity loop
                        	}
                        }

                        // only if there is at least one activity selected for this activity type
                        if(count_selected_purposes_this_loop > 0){
                            count_total_activities++;
                        }

                        // end of selected activity type loop
                    }

                }

                count_total_licence_categories++; // this should always be 1 at end of full loop

                // end of selected licence class loop
            }
        }

        // if no selections, display error do not continue
        if(count_total_purposes == 0){
            swal({
                title: "Create Application",
                text: "Please ensure at least one licence purpose is selected",
                type: "error",
            })
        } else {
            data.org_applicant=vm.behalf_of_org;
            data.proxy_applicant=vm.behalf_of_proxy;
            data.licence_category_data=vm.licence_category;
            data.application_fee=vm.application_fee;
            data.licence_fee=vm.licence_fee;
            data.licence_purposes=licence_purposes
            console.log(' ---- application apply licence createApplication() ---- ');
            console.log(`Licence category ID: ${data.licence_category_id}`);
            console.log(vm.application_fee)
            console.log(vm.licence_fee)
            console.log(data.licence_category)
            console.log(' ==== licence category data ==== ')
            console.log(JSON.stringify(data));
            vm.$http.post('/api/application.json',JSON.stringify(data),{emulateJSON:true}).then(res => {
                console.log('New application response: ', res.body);
                vm.application = res.body;
                vm.$router.push({
                    name:"draft_application",
                    params:{application_id:vm.application.id}
                });
            }, err => {
                console.log(err);
            });
        }
    },
    
  },
  beforeRouteEnter:function(to,from,next){
    let data = new FormData()
    data.org_applicant = window.v_org_applicant;
    let initialisers = [
        utils.fetchLicenceAvailablePurposes(data)
    ]
    Promise.all(initialisers).then(data => {
        next(vm => {
            console.log(window.v_org_applicant);
            vm.licence_categories = data[0]
        });
    });
  },
}
</script>

<style lang="css">
div.margin-left-20 {
    margin-left: 20px;
}
div.purpose-clear-left {
    clear: left;
}
</style>
