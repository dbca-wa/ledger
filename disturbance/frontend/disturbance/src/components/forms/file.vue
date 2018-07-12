<template lang="html">
    <div>
        <div class="form-group">

            <!-- using num_files to determine if files have been uploaded for this question/label (used in disturbance/frontend/disturbance/src/components/external/proposal.vue) -->
            <label :id="id" :num_files="files.length">{{label}}</label>
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
            <div v-if="files">
                <div v-for="v in files">
                    <p>
                        File: <a :href="docsUrl+v" target="_blank">{{v}}</a> &nbsp;
                        <span v-if="!readonly">
                            <a @click="removeImage(v)" class="fa fa-trash-o" title="Remove file" :filename="v" style="cursor: pointer; color:red;"></a>
                        </span>
                    </p>
                    <input :name="name+'-existing'" type="hidden" :value="value"/>
                </div>
            </div>
            <div v-if="!readonly" v-for="n in repeat">
                <input :name="name" type="file" class="form-control" :data-que="n" :accept="fileTypes" @change="handleChange" :required="isRequired"/><br/>
            </div>

        </div>
        <Comment :question="label" :readonly="assessor_readonly" :name="name+'-comment-field'" v-show="showingComment && assessorMode" :value="comment_value" :required="isRequired"/> 
    </div>
</template>

<script>
import Comment from './comment.vue'
import HelpText from './help_text.vue'
export default {
    props:{
        proposal_id: null,
        name:String,
        label:String,
        id:String,
        isRequired:String,
        comment_value: String,
        assessor_readonly: Boolean,
        help_text:String,
        help_text_assessor:String,
        assessorMode:{
            default:function(){
                return false;
            }
        },
        value:{
            default:function () {
                return null;
            }
        },
        fileTypes:{
            default:function () {
                return "image/*,application/pdf,text/csv,application/msword"
            }
        },
        isRepeatable:Boolean,
        readonly:Boolean,
        docsUrl: String
    },
    components: {Comment, HelpText},
    data:function(){
        return {
            repeat:1,
            files:[],
            showingComment: false
        }
    },

    //computed: {
    //    csrf_token: function() {
    //        return helpers.getCookie('csrftoken')
    //    }
    //},

    methods:{
        toggleComment(){
            this.showingComment = ! this.showingComment;
        },
        handleChange:function (e) {
            if (e.target.files.length > 0) {
                this.upload_file(e)
            }
            if (this.isRepeatable) {
                let  el = $(e.target).attr('data-que');
                let avail = $('input[name='+e.target.name+']');
                avail = [...avail.map(id => {
                    return $(avail[id]).attr('data-que');
                })];
                avail.pop();
                if (this.repeat == 1) {
                    this.repeat+=1;
                }else {
                    if (avail.indexOf(el) < 0 ){
                        this.repeat+=1;
                    }
                }
            }
        },
        upload_file: function(e) {
            let vm = this;
            var filename = e.target.files[0].name;
            $("[id=save_and_continue_btn][value='Save Without Confirmation']").trigger( "click" );
            this.files = [e.target.files[0].name];
        },
        removeImage: function (filename) {
            let vm = this;
            //var filename = e.target.getAttribute('filename');
            if (filename) {
                vm.files.pop(filename);
                $('input[name='+vm.name+']').val(null);

                this.$nextTick(() => {
                    $("[id=save_and_continue_btn][value='Save Without Confirmation']").trigger( "click" );
                });
            }
        }

    },
    mounted:function () {
        let vm = this;
        if (vm.value) {
            vm.files = (Array.isArray(vm.value))? vm.value : [vm.value];
        }
    }
}

</script>

<style lang="css">
</style>
