<template lang="html">
    <div class="panel panel-default" >
      <div class="panel-heading">
        <h3 class="panel-title">{{label}}
            <a :href="'#'+section_id" data-toggle="collapse" expanded="true" :aria-controls="section_id">
                <span class="glyphicon glyphicon-chevron-down pull-right "></span>
            </a>
        </h3>
      </div>
      <div class="panel-body collapse in" :id="section_id">
          <slot></slot>
      </div>
    </div>
</template>

<script>
export default {
    name:"section",
    props:["label","Key"],
    data:function () {
        return {
            title:"Section title"
        }
    },
    computed:{
        section_id:function () {
            return "section_"+this.Key
        }
    },
    mounted:function () {
        $("a[data-toggle]").on('click',function () {
        });
    }
}
</script>

<style lang="css">
    h3.panel-title{
        font-weight: bold;
        font-size: 25px;
        padding:20px;
    }
</style>
