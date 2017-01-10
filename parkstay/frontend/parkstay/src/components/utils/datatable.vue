<template lang="html">
   <div id="DataTable">
      <table class="hover table table-striped table-bordered dt-responsive nowrap" cellspacing="0" width="100%" :id="id">
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
     },
     id:{
         required:true
     }
   },
   data : function () {
      return {
         vmDataTable: null,
      }
   },
   computed:{

   },
   methods:{

   },
   mounted:function () {
      let vm = this;
      var table =$('#'+vm.id);
        $.fn.dataTable.ext.errMode = 'throw';
      vm.vmDataTable = $(table).DataTable(vm.dtOptions);
   }
};
</script>

<style lang="css">
td > a{
    border: none;
    border-radius: 2px;
    position: relative;
    padding: 8px 10px;
    margin: 10px 1px;
    font-weight: 500;
    text-transform: capitalize;
    letter-spacing: 0;
    will-change: box-shadow, transform;
    -webkit-transition: -webkit-box-shadow 0.2s cubic-bezier(0.4, 0, 1, 1), background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1), color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    -o-transition: box-shadow 0.2s cubic-bezier(0.4, 0, 1, 1), background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1), color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    transition: box-shadow 0.2s cubic-bezier(0.4, 0, 1, 1), background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1), color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    outline: 0;
    cursor: pointer;
    text-decoration: none;
    background: transparent;
    color: #03a9f4;
}
td > a:hover{
    /*background-color: rgba(153, 153, 153, 0.2);
    text-decoration: none !important;
    margin: 30px 1px;*/
}
table.table-bordered.dataTable tbody th, table.table-bordered.dataTable tbody td {
    border-bottom-width: 0;
    vertical-align: middle;
    text-align: left;
}
</style>
