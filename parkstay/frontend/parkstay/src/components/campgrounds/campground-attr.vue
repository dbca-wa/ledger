<template lang="html">
   <div  id="cg_attr">
        <div class="col-sm-12">
            <alert :show.sync="showUpdate" type="success" :duration="3000">
                <p>Campground successfully updated</p>
            </alert>
            <alert :show.sync="showError" type="danger">
                <p>{{errorString}}<p/>
            </alert>
          <form id="attForm">
              <div class="row">
                  <div class="col-lg-12">
                      <div class="panel panel-primary">
                        <div class="panel-heading">
                          <h3 class="panel-title">Campground Details</h3>
                        </div>
                        <div class="panel-body">
                            <div class="row">
                              <div class="col-md-6">
                                <div class="form-group">
                                  <label class="control-label" >Campground Name</label>
                                  <input type="text" name="name" id="name" class="form-control" v-model="campground.name" required/>
                                </div>
                              </div>
                              <div class="col-md-6">
                                <div class="form-group ">
                                  <label class="control-label" >Park</label>
                                  <select id="park" name="park" class="form-control" v-model="campground.park">
                                      <option v-for="park in parks" :value="park.url">{{ park.name }}</option>
                                  </select>
                                </div>
                              </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                  <div class="form-group ">
                                    <label class="control-label" >Campground Type</label>
                                    <select id="campground_type" name="campground_type" class="form-control"  v-model="campground.campground_type">
                                        <option value="0">Campground: no bookings</option>
                                        <option value="1">Campground: book online</option>
                                        <option value="2">Campground: book by phone</option>
                                        <option value="3">Other accommodation</option>
                                        <option value="4">Not Published</option>
                                    </select>
                                  </div>
                                </div>
                                <div class="col-md-6">
                                  <div class="form-group ">
                                    <label class="control-label" >Site Type</label>
                                    <select id="site_type" name="site_type" class="form-control"  v-model="campground.site_type">
                                        <option value="0">Unnumbered Site</option>
                                        <option value="1">Numbered Site</option>
                                    </select>
                                  </div>
                                </div>
                            </div>
                        </div>
                      </div>
                  </div>
              </div>
              <div class="row" style="margin-top: 40px;">
                 <div class="col-lg-12">
                     <div class="panel panel-primary">
                       <div class="panel-heading">
                         <h3 class="panel-title">Address</h3>
                       </div>
                       <div class="panel-body">
                           <div class="col-md-3">
                             <div class="form-group">
                               <label for="">Street</label>
                               <input id="street" name="street" type="text" class="form-control" v-model="campground.address.street"  placeholder=""/>
                             </div>
                           </div>
                           <div class="col-md-3">
                               <div class="form-group">
                                 <label for="">email</label>
                                 <input id="email" name="email" type="email" class="form-control"v-model="campground.address.email" placeholder=""/>
                               </div>
                           </div>
                           <div class="col-md-3">
                             <div class="form-group">
                               <label for="">telephone</label>
                               <input id="telephone" name="telephone" type="text" class="form-control" v-model="campground.address.telephone" placeholder=""/>
                             </div>
                           </div>
                           <div class="col-md-3">
                               <div class="form-group">
                                 <label for="">postcode</label>
                                 <input id="postcode" name="postcode" type="text" class="form-control" v-model="campground.address.postcode" placeholder=""/>
                               </div>
                           </div>
                       </div>
                     </div>
                 </div>
              </div>
              <div class="row" style="margin-top: 40px;">
                  <div class="col-sm-6 features">
                    <div class="panel panel-primary">
                      <div class="panel-heading">
                        <h3 class="panel-title">Features</h3>
                      </div>
                      <div class="panel-body">
                          <ul class="list-group">
                              <a href="" v-for="feature,key in features"  @click.prevent="addSelectedFeature(feature,key)" class="list-group-item list-group-item-primary">{{feature.name}}</a>
                          </ul>
                      </div>
                    </div>
                  </div>

                  <div class="col-sm-6 features">
                    <div class="panel panel-primary">
                      <div class="panel-heading">
                        <h3 class="panel-title">Selected Feautures</h3>
                      </div>
                      <div class="panel-body">
                          <a href="" v-for="feature,key in selected_features"  @click.prevent="removeSelectedFeature(feature, key)" class="list-group-item ">{{feature.name}}</a>
                      </div>
                    </div>
                  </div>
              </div>
              <div class="row" style="margin-top: 40px;">
                <div class="col-md-12">
                    <div class="form-group">
                        <label class="control-label" >Description</label>
                        <div name="editor" id="editor" class="form-control"></div>
                    </div>
                </div>
              </div>
          </form>
      </div>
      <div class="row" style="margin-top: 40px;">
         <div class="col-sm-8">
            <div class="form-group">
               <div class="col-sm-4 col-md-3 col-lg-2">
                  <label style="line-height: 2.5;">Price set at: </label>
               </div>
               <div class="col-sm-8 col-md-9 col-lg-10">
                  <select id="price_level" name="price_level" class="form-control" v-model="campground.price_level">
                     <option v-for="level in priceSet" :value="level.val">{{ level.name }}</option>
                  </select>
               </div>
            </div>
         </div>
         <div class="col-sm-4">
            <div class="col-sm-12">
               <div class="form-group pull-right">
                  <a href="#" v-if="createCampground" class="btn btn-primary" @click.prevent="create">Create</a>
                  <a href="#" v-else class="btn btn-primary" @click.prevent="update">Update</a>
                  <a href="#" class="btn btn-default">Cancel</a>
               </div>
            </div>
         </div>
      </div>
      <div id="text">

      </div>
   </div>
</template>

<script>
import {
    $,
    api_endpoints,
    helpers,
    validate
}
from '../../hooks.js'
import {
    bus
}
from '../utils/eventBus.js';
import Editor from 'quill';
import Render from 'quill-render';
import loader from '../utils/loader.vue'
import alert from '../utils/alert.vue'
export default {
    name: 'cg_attr',
    components: {alert, loader},
    data: function() {
        let vm = this;
        return {
            selected_price_set: this.priceSet[0],
            parks: '',
            editor:null,
            editor_updated:false,
            features:null,
            selected_features_loaded :false,
            selected_features: Array(),
            form: null,
            errors: false,
            errorString:'',
            showUpdate: false
        }
    },
    props: {
        createCampground: {
            default: function() {
                return true;
            }
        },
        priceSet: {
            default: function() {
                return [
                    {'val':0, name:'Campground level'},
                    {'val':1, name:'Campsite class level'},
                    {'val':2, name:'Campsite level'}
                    ];
            }
        },
        campground: {
            default: function() {
                return {
                    address: {},
                    contact: {}
                };
            },
            type: Object
        },
    },
    computed: {
        showError: function(){
            var vm = this;
            return vm.errors;
        }
    },
    watch:{
        campground: {
            handler:function () {
                this.loadSelectedFeatures();
            },
            deep:true

        }
    },
    methods: {
        create: function() {
            if (this.form.valid()){ 
                this.sendData(api_endpoints.campgrounds,'POST');
            }
        },
        update: function() {
            if (this.form.valid()){ 
                this.sendData(api_endpoints.campground(this.campground.id),'PUT');
            }
        },
        sendData: function(url,method) {
            let vm = this;
            var featuresURL = new Array();
            var temp_features = vm.selected_features; 
            vm.campground.features.forEach(function(f){
                featuresURL.push(f.url);
            });
            vm.campground.features = featuresURL;
            if (vm.campground.contact == null){
                delete vm.campground.contact;
            }
            vm.isLoading = true;
            $.ajax({
                beforeSend: function(xhrObj){
                  xhrObj.setRequestHeader("Content-Type","application/json");
                  xhrObj.setRequestHeader("Accept","application/json");
                },
                url: url,
                method: method,
                xhrFields: { withCredentials:true },
                data: JSON.stringify(vm.campground),
                dataType: 'json',
                success: function(data, stat, xhr) {
                    if (method == 'POST'){
                        vm.$router.push({
                            name: 'cg_detail',
                            params: {
                                id: data.id
                            }
                        });
                    }else if (method == 'PUT'){
                        vm.campground.features = temp_features;
                        vm.showUpdate = true;
                    }
                },
                error:function (resp){
                    vm.errors = true;
                    vm.errorString = helpers.apiError(resp); 
                }
            });
        },
        showAlert: function() {
            bus.$emit('showAlert', 'alert1');
        },
        loadParks: function() {
            var vm = this;
            var url = api_endpoints.parks;
            $.ajax({
                url: url,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.parks = data;
                }
            });
        },
        loadFeatures: function() {
            var vm = this;
            var url = api_endpoints.features;
            $.ajax({
                url: url,
                dataType: 'json',
                success: function(data, stat, xhr) {
                    vm.features = data;
                }
            });
        },
        addSelectedFeature:function (feature,key) {
            let vm = this;
            vm.selected_features.push(feature);
            vm.features.splice(key,1);
            vm.selected_features.sort(function(a,b){ return parseInt(a.id) - parseInt(b.id)});
        },
        removeSelectedFeature:function (feature,key) {
            let vm = this;
            vm.features.push(feature);
            vm.selected_features.splice(key,1);
            vm.features.sort(function(a,b){ return parseInt(a.id) - parseInt(b.id)});
        },
        addFormValidations: function(){
            this.form.validate({
                rules: {
                    name: "required",
                    park: "required",
                    campground_type: "required",
                    site_type: "required",
                    street: "required",
                    email: {
                        required: true,
                        email: true
                    },
                    telephone: "required",
                    postcode: "required",
                    editor: "required",
                    price_level: "required"
                },
                messages: {
                    name: "Enter a campground name",
                    park: "Select a park from the options",
                    campground_type: "Select a campground type from the options",
                    site_type: "Select a site type from the options",
                    editor: "required",
                    price_level: "Select a price level from the options"
                },
                showErrors: function (errorMap, errorList) {
                                        
                    $.each(this.validElements(), function (index, element) {
                        var $element = $(element);
                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });
                    
                    // destroy tooltips on valid elements                              
                    $("." + this.settings.validClass).tooltip("destroy");       
                      
                    // add or update tooltips 
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                                            
                        $("#" + error.element.id)
                            .tooltip({ trigger: "focus" })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
        },
        loadSelectedFeatures:function () {
            let vm =this;
            if (vm.campground.features){
                if (!vm.createCampground){
                    vm.selected_features = vm.campground.features;
                }
                $.each(vm.campground.features,function (i,cgfeature) {
                    $.each(vm.features,function (j,feat) {
                        if(feat != null){
                            if(cgfeature.id == feat.id ){
                                vm.features.splice(j,1);
                            }
                        }
                    })
                });
            }

        }
    },
    mounted: function() {
        let vm = this;
        vm.loadParks();
        vm.loadFeatures();
        vm.editor = new Editor('#editor', {
            modules: {
                toolbar: true
            },
            theme: 'snow'
        });
        vm.editor.clipboard.dangerouslyPasteHTML(0,vm.campground.description, 'api');
        vm.editor.on('text-change', function(delta, oldDelta, source) {

            var text = $('#editor >.ql-editor').html();
            vm.campground.description = text;
        });

        vm.form = $('#attForm');
        vm.addFormValidations();
    },
    updated:function () {
        let vm =this;
        if(vm.campground.description != null && vm.editor_updated ==false){
            vm.editor.clipboard.dangerouslyPasteHTML(0,vm.campground.description, 'api');
            vm.editor_updated =true;
        }
    }
}

</script>

<style lang="css">
    #editor{
        height: 200px;
    }
    .features >.panel>.panel-body{
        padding:0;
        max-height: 300px;
        overflow: auto;
    }
    .features .list-group{
        margin-bottom: 0;
    }
    .features .list-group-item{
        border-radius: 0;
    }
    .list-group-item:last-child{
        border-bottom-left-radius: 5px;
        border-bottom-right-radius: 5px;
    }
</style>
