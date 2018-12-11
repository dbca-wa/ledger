<template lang="html">
    <div  id="cg_additional" >
        <div v-show="!isLoading">
            <form id="additionalForm">
                <div class="col-sm-12">
                <alert :show.sync="showUpdate" type="success" :duration="7000">
                    <p>Mooring successfully updated</p>
                </alert>
                <alert :show.sync="showError" type="danger">
                    <p>{{errorString}}<p/>
                </alert>
					<div class="row">
						<div class="col-lg-12">
                            <div class="row">
                                <div class="col-md-12">
                                    <div class="form-group">
                                        <label class="control-label" >Description</label>
                                        <div id="editor" class="form-control"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="row" style="margin-top: 40px;">
                                <div class="col-md-12">
                                    <div class="form-group">
                                        <label class="control-label" >Additional confirmation information</label>
                                        <textarea id="additional_info" class="form-control" v-model="campground.additional_info"/>
                                    </div>
                                </div>
                            </div>
                            <div class="row" style="margin-top: 40px;">
                                <div class="col-sm-8">
                                </div>
                                <div class="col-sm-4">
                                    <div class="col-sm-12">
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
}
from '../utils/eventBus.js';
import Editor from 'quill';
import Render from 'quill-render';
import loader from '../utils/loader.vue'
import alert from '../utils/alert.vue'
export default {
    name: 'cg_additional',
    components: {
        alert,
        loader,
    },
    data: function() {
        let vm = this;
        return {
            editor: null,
            editor_updated: false,
            form: null,
            errors: false,
            errorString: '',
            showUpdate: false,
            isLoading: false,
            reload : false,
            features_selected: [],
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
        loadingAdditional: {
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
        loadingAdditional: {
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
		validateForm:function () {
			let vm = this;
            var isValid = vm.validateEditor($('#editor'))
            return  vm.form.valid() && isValid;
		},
        create: function() {
            console.log("CREATE");
			if(this.validateForm()){
				this.sendData(api_endpoints.campgrounds, 'POST');
			}
        },
        update: function() {
			if(this.validateForm()){
				this.sendData(api_endpoints.campground(this.campground.id), 'PUT',true); 
			}	
        },
        validateEditor: function(el){
            let vm = this;
			if (el.parents('.form-group').hasClass('has-error')) {
				el.tooltip("destroy");
				el.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
			}
            if (vm.editor.getText().trim().length == 0) {
                // add or update tooltips
                el.tooltip({
                        trigger: "focus"
                    })
                    .attr("data-original-title", 'Description is required')
                    .parents('.form-group').addClass('has-error');
                return false;
            }
            return true;
        },
        sendData: function(url, method, reload=false) {
            let vm = this;
            vm.isLoading =true;
            vm.reload = reload;
            vm.$emit('updated', vm.campground);
            vm.$emit('save', url, method, reload, "additional");
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
                    for (var i = 0; i < data.features.length; i++){
                        vm.features_selected.push(data.features[i].id);
                    }
                    vm.campground.features = vm.features_selected;
                    console.log("Features updated");
                    vm.$emit('updated', vm.campground);
                }
            });
        },
    },
    mounted: function() {
        let vm = this;
        vm.fetchCampground();
        vm.editor = new Editor('#editor', {
            modules: {
                toolbar: true
            },
            theme: 'snow'
        });
        vm.editor.on('text-change', function(delta, oldDelta, source) {
            var text = $('#editor >.ql-editor').html();
            vm.campground.description = text;
			vm.validateEditor($('#editor'));
        });
        vm.form = $('#additionalForm');

        $('.form-control').blur(function(){
            vm.$emit('updated', vm.campground);
        });
    },
    updated: function() {
        let vm = this;
        var changed = false;
        if (vm.campground.description != null && vm.editor_updated == false) {
            vm.editor.clipboard.dangerouslyPasteHTML(0, vm.campground.description, 'api');
            changed = true;
        }
        if (changed) {
            vm.editor_updated = true;
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
        min-height: 300px;
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
    .empty-features{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 300px;
        color: #ccc;
        font-size: 2em;
    }
</style>
