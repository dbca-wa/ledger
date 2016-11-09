<template lang="html" id="confirmbox">
    <div :id="confirmModal" class="modal fade">
      <div class="modal-dialog modal-sm">
      <div class="modal-content">
          <!-- dialog body -->
          <div class="modal-body">
          <div class="row">
              <div :id="icon" class="col-sm-12 text-center" style="font-size:75px; ">
                  <!--icon goes here-->
              </div>
              <div class="col-sm-12 text-center">
                  <p :id="text"><!--modal text--></p>
              </div>
          </div>
          </div>
          <!-- dialog buttons -->
          <div :id="buttons" class="modal-footer">
              <!--buttons-->
          </div>
      </div>
      </div>
  </div>
</template>

<script>
import {$} from '../../hooks.js'
import {bus} from './eventBus.js'
export default {
    data:function () {
        return {
            confirmModal: 'confirmModal'+this._uid,
            icon: 'modalIcon'+this._uid,
            text: 'modalText'+this._uid,
            buttons: 'modalButtons'+this._uid,
        }
    },
    props:{
        options:{
            required:true,
            type:Object
        },
        id:{
            required:true
        }
    },
    methods:{
        confirmBox:function(json){
            let vm = this;
            var Obj = json;
            var confirmModal = $("#"+vm.confirmModal);
            var icon = $("#"+vm.icon);
            var text = $("#"+vm.text);
            var buttons = ("#"+vm.buttons);
            $(icon).html(Obj.icon);
            $(text).html(Obj.message);
            $(buttons).html("");
            if (typeof Obj.buttons != "undefined")
            {
               $.each(Obj.buttons, function (i, btn)
               {
                   var eventHandler = (typeof btn.eventHandler != "undefined") ? btn.eventHandler : "onclick";
                   $(buttons).append("<button type=\"button\" data-dismiss=\"modal\""+ eventHandler +"=" + btn.onClick + " class=\"btn " + btn.bsColor + "\">" + btn.text + "</button>");
               });
            }
            $(buttons).append("<button type=\"button\" data-dismiss=\"modal\" class=\"btn btn-default\">Cancel</button>");
        }
   },
   mounted:function () {
       var vm = this;
       vm.confirmBox(this.options);
       bus.$on('showAlert', function(id){
          if(id === vm.id){
              $("#"+vm.confirmModal).modal('show');
          }
      });
   }
}
</script>

<style lang="css">
.modal-body,.modal-footer {
    background-color: #fff;
    color: #333;
    }
</style>
