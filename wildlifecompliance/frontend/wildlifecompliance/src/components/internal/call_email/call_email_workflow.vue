<template lang="html">
    <div id="CallWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Forward to Wildlife Protection Branch" large>
          <div class="container-fluid">
            <div class="row">
                <div class="col-sm-12">
                    <div class="form-group">
                        <div class="row">
                            <div class="col-sm-3">
                                <label class="control-label pull-left" for="details">Details</label>
                            </div>
                            <div class="col-sm-4">
                                <textarea placeholder="write text" id="details" v-model="call_email.forwardDetails"/>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
          </div>
        </modal>
    </div>
</template>
<script>
import Vue from "vue";
import modal from '@vue-utils/bootstrap-modal.vue';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";

export default {
  name: "CallEmailWorking",
  data: function() {
    return {
      isModalOpen: false,
    };
  },
  components: {
    modal,
  },
  computed: {
    ...mapGetters('callemailStore', {
      call_email: "call_email",
    }),
  },
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },
  methods: {
    ok: function() {
            // if($(this.form).valid()){
            //     vm.sendData();
            // }
        this.isModalOpen = false;
        // this.close();
    },
    cancel: function() {
        // let vm = this;
        // vm.close();
        this.isModalOpen = false;
        // this.close();
    },
    close: function () {
        // let vm = this;
        // this.isModalOpen = false;
        // this.comms = {};
        // this.errors = false;
        // $('.has-error').removeClass('has-error');
        // this.validation_form.resetForm();
        // let file_length = vm.files.length;
        // this.files = [];
        // for (var i = 0; i < file_length;i++){
        //     vm.$nextTick(() => {
        //         $('.file-row-'+i).remove();
        //     });
        // }
        // this.attachAnother();
    },
    
  },
  created: function() {
    
  },
  mounted: function() {
        
  }
};
</script>

<style lang="css">
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
.top-buffer{margin-top: 5px;}
.top-buffer-2x{margin-top: 10px;}
</style>
