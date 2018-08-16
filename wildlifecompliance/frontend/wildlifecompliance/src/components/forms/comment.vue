<template lang="html">
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <div class="row">
                  <label class="col-md-3" for="label" >Deficiency</label>
                  <div class="col-md-9">
                      <textarea :readonly="readonly" :data-question="question" class="form-control deficiency" :name="name" :value="value" :data-tabname="tabname" :data-tabid="tabid"@click.prevent="getTab()"></textarea>
                  </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props:["name","question","value","readonly","tabname","tabid"],
    data:function () {
       let vm = this;
        return {
          tabname:null,
          tabid:null
        }
    },
    methods:{
      getTab(){
        let vm=this;
        var selectedTabTitle = $("#tabs-section li.active");
        var tab_id=selectedTabTitle.children().attr('href').split(/(\d)/)[1]
        console.log(tab_id)
        vm.tabname = $(selectedTabTitle).text();
        vm.tabid = tab_id
        
        // console.log('hello from comment')
        // console.log(vm.tabname)
        // console.log($(selectedTabTitle).attr('id'))
        // console.log(selectedTabTitle)
        // console.log(selectedTabTitle.children().attr('href').split(/(\d)/)[1])
      }
    }
}
</script>

<style lang="css" scoped>
.buffer {
    margin-top: 5px;
}
</style>
