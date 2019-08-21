<template lang="html">
    <div>
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" :title="modalTitle" large force>
            <div class="container-fluid">
                <div class="row col-sm-12">

                    <div class="form-group"><div class="row">
                        <div class="col-sm-3">
                            <label class="control-label pull-left">Reason</label>
                        </div>
                        <div class="col-sm-7">
                            <textarea class="form-control" placeholder="add reason" id="reason" v-model="workflowDetails"/>
                        </div>
                    </div></div>

                    <div class="form-group"><div class="row">
                        <div class="col-sm-3">
                            <label class="control-label pull-left"  for="Name">Attachments</label>
                        </div>
                        <div class="col-sm-9">
                            <filefield ref="comms_log_file" name="comms-log-file" :isRepeatable="true" :documentActionUrl="sanction_outcome.commsLogsDocumentUrl" />
                        </div>
                    </div></div>

                </div>
            </div>
        </modal>
    </div>
</template>

<script>
import Vue from "vue";
import modal from '@vue-utils/bootstrap-modal.vue';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import filefield from '@/components/common/compliance_file.vue';
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");

export default {
    name: "SanctionOutcomeWorkflow",
    data: function() {
        return {
            isModalOpen: false,
            files: [
                    {
                        'file': null,
                        'name': ''
                    }
            ],
            workflowDetails: '',
        }
    },
    components: {
      modal,
      filefield,
    },
    props:{
        workflow_type: {
            type: String,
            default: '',
        },
    },
    computed: {
      ...mapGetters('sanctionOutcomeStore', {
          sanction_outcome: "sanction_outcome",
      }),
      modalTitle: function() {
          switch(this.workflow_type){
            case 'issue':
                  return "Issue";
                  break;
            case 'withdraw':
                  return "Withdraw";
                  break;
            case 'send_to_manager':
                  return "Send to Manager";
                  break;
            case 'endorse':
                  return "Endorse";
                  break;
            case 'decline':
                  return "Decline";
                  break;
            case 'return_to_officer':
                  return "Return to Officer";
                  break;
            case 'extend_due_date':
                  return "Extend Due Date";
                  break;
            case 'send_to_dot':
                  return "Send to Department of Transport";
                  break;
            case 'send_to_fines_enforcement':
                  return "Send to Fines Enforcement";
                  break;
            case 'escalate_for_withdrawal':
                  return "Escalate for Withdrawal";
                  break;
            default:
                  return "---";
          }
      },
    },
    methods: {
        ok: async function () {
            const response = await this.sendData();
            console.log(response);
            if (response === 'ok') {
                this.close();
            }
        },
        cancel: async function() {
            await this.$refs.comms_log_file.cancel();
            this.isModalOpen = false;
            this.close();
        },
        close: function () {
            let vm = this;
            this.isModalOpen = false;
            let file_length = vm.files.length;
            this.files = [];
            for (var i = 0; i < file_length;i++){
                vm.$nextTick(() => {
                    $('.file-row-'+i).remove();
                });
            }
            this.attachAnother();
        },
        sendData: async function () {
            let post_url = '/api/sanction_outcome/' + this.sanction_outcome.id + '/workflow_action/'
            let payload = new FormData();
            payload.append('details', this.workflowDetails);
            this.$refs.comms_log_file.commsLogId ? payload.append('comms_log_id', this.$refs.comms_log_file.commsLogId) : null;
            this.workflow_type ? payload.append('workflow_type', this.workflow_type) : null;

            console.log('payload');
            console.log(payload);

            try {
                let res = await Vue.http.post(post_url, payload);
                console.log(res);
                if (res.ok) {
                    return res
                }
            } catch(err) {
                    this.errorResponse = err.statusText;
            }
        },
        uploadFile(target,file_obj){
            let vm = this;
            let _file = null;
            var file_input = $('.'+target)[0];
  
            if (file_input.files && file_input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(file_input.files[0]); 
                reader.onload = function(e) {
                    _file = e.target.result;
                };
                _file = file_input.files[0];
            }
            file_obj.file = _file;
            file_obj.name = _file.name;
        },
        removeFile(index){
            let length = this.files.length;
            $('.file-row-'+index).remove();
            this.files.splice(index,1);
            this.$nextTick(() => {
                length == 1 ? this.attachAnother() : '';
            });
        },
        attachAnother(){
            this.files.push({
                'file': null,
                'name': ''
            })
        },
    },
}
</script>

<style>

</style>


