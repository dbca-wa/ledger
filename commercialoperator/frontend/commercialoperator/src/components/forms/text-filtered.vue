<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline" >{{ label }}</label>
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
                <v-select label="name" :filterable="false" :options="options" @search="onSearch">
                  <template slot="no-options">
                      type to search users/organisations.
                  </template>
                  <template slot="option" slot-scope="option">
                      <div class="d-center">
                          {{ option.name }}
                      </div>
                  </template>

                  <template slot="selected-option" slot-scope="option">
                     <div class="selected d-center" :user_id="option.id">
                        {{ option.name }}
                    </div>
                  </template>
                </v-select>
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

export default {
    props:["url", "type","name","id", "comment_value","value","isRequired","help_text","help_text_assessor","assessorMode","label","readonly","assessor_readonly", "help_text_url", "help_text_assessor_url"],
    components: {Comment, HelpText, HelpTextUrl},
    data(){
        let vm = this;
        return {
            showingComment: false,
            options: [],
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
</style>
