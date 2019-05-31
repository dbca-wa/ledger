<template lang="html">
    <div id="CallWorkflow">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Forward to Wildlife Protection Branch" large>
          <div class="container-fluid">
            <div class="row">
                    <form class="form-horizontal" name="amendForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row">
                                <label class="control-label">Request Amendment for the application</label>
                            </div>
                            <div class="row">
                                <div class="form-group">
                                    <div class="col-sm-offset-2 col-sm-8">
                                        <label class="control-label" for="Name">Select licensed activities to amend</label>
                                        <div v-for="activity in amendableActivities">
                                            <div>
                                                <input type="checkbox" :value ="activity.id" :name="activity.name" :id="activity.id" v-model="amendment.activity_list">{{activity.name}}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Reason</label>
                                        <select class="form-control" name="reason" ref="reason" v-model="amendment.reason">
                                            <option v-for="item in reason_choices" :value="item.key">{{item.value}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <label class="control-label pull-left"  for="Name">Additional Comments to User</label>
                                        <textarea class="form-control" name="name" v-model="amendment.text">{{amendment.text}}</textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
          </div>
        </modal>
    </div>
</template>
<script>
import Vue from "vue";
import modal from '@vue-utils/bootstrap-modal.vue';

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
    
  },
  filters: {
    formatDate: function(data) {
      return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
    }
  },
  methods: {
    ok: () => {
            // if($(this.form).valid()){
            //     vm.sendData();
            // }
        this.isModalOpen = false;
        this.close();
    },
    cancel: () => {
        // let vm = this;
        // vm.close();
        this.isModalOpen = false;
        this.close();
    },
    close:function () {
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
