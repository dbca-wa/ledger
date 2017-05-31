<template lang="html">
    <div class="form-group">
        <label>{{label}}</label>
         <i data-toggle="tooltip" v-if="help_text" data-placement="right" class="fa fa-question-circle" :title="help_text"> &nbsp; </i>
        <div v-if="value">
            <div  v-for="v in value">
                <p>
                    Currently: <a :href="value" target="_blank">{{v.value}}</a>
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
        value:Array,
        fileTypes:{
            default:function () {
                return "image/*,application/pdf,text/csv,application/msword"
            }
        },
        isRepeatable:Boolean
    },
    data:function(){
        return {
            repeat:1
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
    }
}

</script>

<style lang="css">
</style>
