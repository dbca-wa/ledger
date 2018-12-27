<template lang="html">
    <div class="panel panel-default" >
      <div class="panel-heading">
        <h3 class="panel-title">{{label}}
            <a :href="'#'+section_id" class="panelClicker" data-toggle="collapse" expanded="true" :aria-controls="section_id">
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
            title:"Section title",
            eventInitialised: false
        }
    },
    computed:{
        section_id:function () {
            return "section_"+this.Key
        }
    },
    updated:function () {
        let vm = this;
        vm.$nextTick(()=>{
            if (!vm.eventInitialised){
                $('.panelClicker[data-toggle="collapse"]').on('click',function () {
                    var chev = $(this).children()[0];
                    window.setTimeout(function () {
                        $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
                    },100);
                });
                this.eventInitialised = true;
            }
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
