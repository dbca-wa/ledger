<template lang="html">
   <div  id="cg_attr">
      <div v-if="!createCampground" class="col-sm-12">
       <div class="col-sm-8 col-sm-offset-2">
          <slot name="cg_name">
              <h3>{{campground.name}}</h3>
          </slot>
          <slot name="cg_description">
              <div v-html="campground.description"></div>
         </slot>
         <slot></slot>
       </div>
      </div>
      <div class="col-sm-12" v-else>
          <form >
              <div class="row">
                <div class="col-md-6">
                  <div class="form-group ">
                    <label class="control-label" >Campground Name</label>
                    <input type="text" class="form-control" v-model="campground.name" />
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group ">
                    <label class="control-label" >Park</label>
                    <select class="form-control" v-model="selected_park">
                        <option value="All">All</option>
                        <option v-for="park in parks" :value="park.url">{{ park.name }}</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-4">
                  <div class="form-group ">
                    <label class="control-label" >Campground Type</label>
                    <select class="form-control"  v-model="campground.campground_type">
                        <option value="0">Campground: no bookings</option>
                        <option value="1">Campground: book online</option>
                        <option value="2">Campground: book by phone</option>
                        <option value="3">Other accommodation</option>
                        <option value="4">Not Published</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="form-group ">
                    <label class="control-label" >Site Type</label>
                    <select class="form-control">
                        <option value="0">Unnumbered Site</option>
                        <option value="1">Numbered Site</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="form-group ">
                    <label class="control-label" >Dogs Permitted</label>
                    <input type="checkbox" v-model="campground.dog_permitted">
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-3">
                  <div class="form-group">
                    <label for="">Street</label>
                    <input type="text" class="form-control" v-model="campground.address.street"  placeholder="">
                  </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                      <label for="">email</label>
                      <input type="email" class="form-control"v-model="campground.address.email" placeholder="">
                    </div>
                </div>
                <div class="col-md-3">
                  <div class="form-group">
                    <label for="">telephone</label>
                    <input type="text" class="form-control" v-model="campground.address.telephone" placeholder="">
                  </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                      <label for="">postcode</label>
                      <input type="text" class="form-control" v-model="campground.address.postcode" placeholder="">
                    </div>
                </div>
              </div>
              <div class="row">
                <div class="col-md-12">
                    <div class="form-group">
                      <label class="control-label" >Description</label>
                      <div id="editor" class="form-control">
                      </div>
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
                  <select class="form-control" v-model="selected_price_set">
                     <option v-for="level in priceSet" :value="level">{{ level }}</option>
                  </select>
               </div>
            </div>
         </div>
         <div class="col-sm-4">
            <div class="col-sm-12">
               <div class="form-group pull-right">
                  <a href="#" v-if="createCampground" class="btn btn-primary" @click="showAlert">Create</a>
                  <a href="#" v-else class="btn btn-primary" @click="showAlert">Update</a>
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
    api_endpoints
}
from '../../hooks.js'
import {
    bus
}
from '../utils/eventBus.js';
import Editor from 'quill';
import Render from 'quill-render';
export default {
    name: 'cg_attr',
    components: {},
    data: function() {
        let vm = this;
        return {
            selected_price_set: this.priceSet[0],
            parks: '',
            selected_park: ''
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
                return ['Campsite level', 'Campground level'];
            }
        },
        campground: {
            default: function() {
                return {
                    address: {}
                };
            },
            type: Object
        }
    },
    methods: {
        create: function() {
            this.$emit('create');
        },
        update: function() {
            this.$emit('update');
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
    },
    watch: {

    },
    mounted: function() {
        let vm = this;
        vm.loadParks();
        if (this.createCampground) {
            var editor = new Editor('#editor', {
                modules: {
                    toolbar: true
                },
                theme: 'snow'
            });
            editor.on('text-change', function(delta, oldDelta, source) {

                var text = $('#editor >.ql-editor').html();
                vm.campground.description = text;
                console.log(vm.campground);
            });
        }
    }
}

</script>

<style lang="css">
    #editor{
        height: 200px;
    }
</style>
