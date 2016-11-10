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
import mix from './mixins.js'
var confirmModal = module.exports = {
    data:function () {
        return {
            confirmModal: 'confirmModal'+this._uid,
            icon: 'modalIcon'+this._uid,
            text: 'modalText'+this._uid,
            buttons: 'modalButtons'+this._uid,
            eventHandler: Array()
        }
    },
    mixins:[mix],
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
            var autoclose = (typeof Obj.autoclose != "undefined")? true: Obj.autoclose;
            $(icon).html(Obj.icon);
            $(text).html(Obj.message);
            $(buttons).html("");
            if (typeof Obj.buttons != "undefined")
            {
               $.each(Obj.buttons, function (i, btn)
               {
                   var eventHandler = (typeof btn.eventHandler != "undefined") ? btn.eventHandler : "@click";
                   mix.methods[btn.event] = btn.handler;
                   console.log(vm.delete);
                   $(buttons).append("<button type=\"button\" data-click="+btn.event+"\" class=\"btn " + btn.bsColor + "\">" + btn.text + "</button>");
                   $(function () {
                       $('button[data-click]').on('click',function () {
                           btn.handler();
                           if(autoclose){
                               $(confirmModal).hide();
                           }
                       });
                   })
               });
            }
            $(buttons).append("<button type=\"button\" data-dismiss=\"modal\" class=\"btn btn-default\">Cancel</button>");
        },
        eventHandler:function(run){
            run();
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
