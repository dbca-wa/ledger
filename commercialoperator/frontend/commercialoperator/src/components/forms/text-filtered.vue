<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline"  v-if="label">{{ label }}</label>
            <template v-if="help_text">
                <HelpText :help_text="help_text" />
            </template>
            <template v-if="help_text_assessor && assessorMode">
                <HelpText :help_text="help_text_assessor" assessorMode={assessorMode} isForAssessor={true} />
            </template> 

            <template v-if="help_text_url">
                <HelpTextUrl :help_text_url="help_text_url" />
            </template>
            <template v-if="help_text_assessor_url && assessorMode">
                <HelpTextUrl :help_text_url="help_text_assessor_url" assessorMode={assessorMode} isForAssessor={true} />
            </template> 


            <template v-if="assessorMode && !assessor_readonly">
                <template v-if="!showingComment">
                    <a v-if="comment_value != null && comment_value != undefined && comment_value != ''" href="" @click.prevent="toggleComment"><i style="color:red" class="fa fa-comment-o">&nbsp;</i></a>
                    <a v-else href="" @click.prevent="toggleComment"><i class="fa fa-comment-o">&nbsp;</i></a>
                </template>
                <a href="" v-else  @click.prevent="toggleComment"><i class="fa fa-ban">&nbsp;</i></a>
            </template>

            <template v-if="readonly">
                <input :readonly="readonly" :type="type" class="form-control" :name="name" :value="value" :required="isRequired" />
            </template>
            <template v-else>
                <v-select label="name" name="fullname" :filterable="false" :options="options" @search="onSearch" v-validate="'required|fullname'">
                  <template slot="no-options">
                      type to search users/organisations.
                  </template>
                  <template slot="option" slot-scope="option">
                      <div v-if="option.email==''" class="d-center">
                          {{ option.name }}
                      </div>
                      <div v-else class="d-center">
                          {{ option.name }} ({{ option.email }})
                      </div>
                  </template>

                  <template slot="selected-option" slot-scope="option">
                     <div class="selected d-center"  :user_id="option.id">
                        <input type="hidden" class="form-control" :name="name+'-selected'" :value="option.id" />
                        <span v-if="option.email==''">
                          {{ option.name }}
                        </span>
                        <span v-else>
                          {{ option.name }} ({{ option.email }})
                        </span>
                    </div>
                  </template>
                </v-select>

<!--
                <span v-show="errors.has('fullname')">{{ errors.first('fullname') }}</span>

                <span v-show="errors.has('fullname')" class="danger">
                    {{ errors.first('fullname') }}
                </span>

                <validation-provider name="fullname" rules="required|fullname">
                  <div slot-scope="{ errors }">
                    <input v-model="fullname">
                    <p>{{ errors[0] }}</p>
                  </div>
                </validation-provider>
-->
            </template>


        </div>
        <Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value"/> 
    </div>
</template>

<script>
import Comment from './comment.vue'
import HelpText from './help_text.vue'
import HelpTextUrl from './help_text_url.vue'

import Vue from 'vue'
import vSelect from "vue-select"
Vue.component('v-select', vSelect)

//import VeeValidate from 'vee-validate';
//Vue.use(VeeValidate)

//import { ValidationProvider } from 'vee-validate';
//Vue.component('ValidationProvider', ValidationProvider);

export default {
    props:["url", "type","name","id", "comment_value","value","isRequired","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly", "help_text_url", "help_text_assessor_url"],
    components: {Comment, HelpText, HelpTextUrl},
    data(){
        let vm = this;
        return {
            showingComment: false,
            options: [],
            fullname: null,
        }
    },
    methods: {
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
        onSearch(search, loading) {
            loading(true);
            this.search(loading, search, this);
        },
        search: _.debounce((loading, search, vm) => {

            //vm.$http.get(vm.filtered_users_url+escape(search),{
            vm.$http.get(vm.url+escape(search),{
                emulateJSON: true
            }).then(res=>{
                //vm.options = JSON.parse(res.body);
                vm.options = res.body;
                //console.log(vm.options);
                loading(false);
            });
        }, 350),


    }
}
</script>

<style lang="css">
    input {
        box-shadow:none;
    }

    .v-select {
        color: #147688;
        background-color: white;
        border-color: #91ddec;
    }
</style>
