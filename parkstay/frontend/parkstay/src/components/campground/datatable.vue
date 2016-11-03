<template lang="html">
   <div id="DataTable">
      <table class="hover table table-striped table-bordered dt-responsive nowrap" cellspacing="0" width="100%"  id="table">
            <thead>
                <tr>
                    <th v-for="header in dtHeaders"> {{ header}}</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
   </div>

</template>

<script>
import {$, DataTable, DataTableBs,DataTableRes} from '../../hooks'

module.exports = {
   name : 'DataTable',
   props:{
      dtHeaders:{
         type:Array,
         required:true
      },
      dtOptions: {
         type:Object,
         required:true
      }
   },
   data : function () {
      return {
         vmDataTable: null
      }
   },
   watch:{

   },
   methods:{

   },
   mounted:function () {
      let vm = this;
      var table =$('#table');
      vm.vmDataTable = $(table).DataTable(vm.dtOptions);
   }
};
</script>

<style lang="css">
</style>
