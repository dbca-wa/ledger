<template lang="html">
    <div class="form-group">
        <label>{{label}}</label>
        <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" style="color:blue" :title="help_text">&nbsp;</i>
        <i data-toggle="tooltip" v-if="help_text_assessor && assessorMode" data-placement="right" class="fa fa-question-circle" style="color:green" :title="help_text_assessor">&nbsp;</i>
        <div v-if="files">
            <div v-for="v in files">
                <p>
                    File: <a :href="v" target="_blank">{{v}}</a>
                </p>
                <input :name="name+'-existing'" type="hidden" :value="value"/>
            </div>
        </div>
        <div v-for="n in repeat">
            <input :name="name" type="file" class="form-control" :data-que="n" :accept="fileTypes" @change="handleChange"/><br/>
        </div>

    </div>
</template>

<script>
export default {
    props:{
        name:String,
        label:String,
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
        isRepeatable:Boolean
    },
    data:function(){
        return {
            repeat:1,
            files:[]
        }
    },
    methods:{
        handleChange:function (e) {
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
