<template lang="html">
<div  id="cg_images" >
	<div v-show="!isLoading">
		<form id="imageForm">
		<div class="col-sm-12">
			<alert :show.sync="showUpdate" type="success" :duration="7000">
				<p>Mooring successfully updated</p>
			</alert>
			<alert :show.sync="showError" type="danger">
				<p>{{errorString}}<p/>
			</alert>
					<div class="row">
						<div class="col-lg-12">
                            <imagePicker :images="campground.images"></imagePicker>
                            <div class="row">
                                <div class="col-md-12" style="margin-top:20px;">
                                    <div class="form-group pull-right">
                                        <a href="#" v-if="createCampground" class="btn btn-primary" @click.prevent="create">Create</a>
                                        <a href="#" v-else class="btn btn-primary" @click.prevent="update">Update</a>
                                        <a href="#" class="btn btn-default" @click.prevent="goBack">Cancel</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

			</form>
		</div>
		<loader :isLoading.sync="isLoading">Loading...</loader>
	</div>
</template>
<style>
.alert{
    display:none;
    height:30px;
    line-height:30px;
    padding:7px 9px;
}

</style>

<script>
import {
    $,
    api_endpoints,
    helpers,
    validate
}
from '../../hooks.js'
import {
    bus,
    select2
}
from '../utils/eventBus.js';
import imagePicker from '../utils/images/imagePicker.vue'
import loader from '../utils/loader.vue'
import alert from '../utils/alert.vue'
export default {
    name: 'cg_images',
    components: {
        alert,
        loader,
        imagePicker
    },
    data: function() {
        let vm = this;
        return {
            form: null,
            errors: false,
            errorString: '',
            showUpdate: false,
            isLoading: false,
            reload : false,
        }
    },
    props: {
        createCampground: {
            default: function() {
                return true;
            }
        },
        campground: {
            default: function() {
                return {
                    address: {},
                    images: []
                };
            },
            type: Object
        },
        loadingImages: {
            type: Boolean,
            default: function(){
                return false;
            }
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
    },
    watch: {
        loadingImages: {
            immediate: true,
            deep: true,
            handler: function(n, o){
                this.isLoading = n;
            }
        },
        campground: {
            handler: function() {
                // this.loadSelectedFeatures();
            },
            deep: true

        }
    },
    methods: {
		goBack: function() {
            helpers.goBack(this);
        },
        create: function() {
            console.log("CREATE");
            this.sendData(api_endpoints.campgrounds, 'POST');
        },
        update: function() {
            this.sendData(api_endpoints.campground(this.campground.id), 'PUT',true); 
        },
        sendData: function(url, method, reload=false) {
            let vm = this;
            vm.isLoading =true;
            vm.reload = reload;
            vm.$emit('updated', vm.campground);
            vm.$emit('save', url, method, reload, "images");
        },
        showAlert: function() {
            bus.$emit('showAlert', 'alert1');
        },
        fetchCampground:function () {
            let vm =this;
            $.ajax({
                url: api_endpoints.campground(vm.$route.params.id),
                dataType: 'json',
                async: false,
                success: function(data, stat, xhr) {
                    vm.campground = data;
                    bus.$emit('campgroundFetched');
                }
            });
        },
    },
    mounted: function() {
        let vm = this;
        vm.fetchCampground();
    },
}

</script>
