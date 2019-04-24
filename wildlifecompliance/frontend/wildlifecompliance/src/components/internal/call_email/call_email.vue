<template lang="html">
    <div class="container">
          <div v-for="item in call_email.schema">
            <compliance-renderer-block
              :component="item" 
              />
          </div>
          <div class="col-sm-12">
            <button @click.prevent="save"
              class="btn btn-primary pull-right">Save</button>
          </div>
            
    </div>
</template>
<script>
import Vue from "vue";
import CommsLogs from "@common-utils/comms_logs.vue";
import { api_endpoints, helpers } from "@/utils/hooks";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
export default {
  name: "ViewCallEmail",
  data: function() {
    //let vm = this;
    console.log(this);
    return {
      pBody: "pBody" + this._uid,
      loading: [],
      renderer_form: null,
    };
  },

  components: {
    CommsLogs
  },
  computed: {
    ...mapGetters({
      call_email: "callemailStore/call_email",
      call_id: "callemailStore/call_id"
    }),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    isLoading: function() {
      return this.loading.length > 0;
    },
    call_email_form_url: function() {
      return this.call_email
        ? `/api/call_email/${this.call_email.id}/form_data.json`
        : "";
    }
  },
  methods: {
    ...mapActions({
      loadCallEmail: "callemailStore/loadCallEmail",
      saveFormData: "saveFormData"
    }),

    createCallEmail: function(e) {
      let formData = new FormData(this.renderer_form);
      this.$http
        .post(
          helpers.add_endpoint_join(
            api_endpoints.call_email,
            this.call_email.id + "/update_renderer_form/"
          ),
          formData
        )
        .then(
          res => {
            swal("Saved", "Your Call/Email has been saved", "success");
          },
          err => {}
        );
      /*
                this.$router.push({
                    name: 'internal-call-email-dash'
                });
                */
    },
    save: function(e) {
      this.isProcessing = true;
      console.log(this.call_email_form_url);
      this.saveFormData({ url: this.call_email_form_url }).then(
        res => {
          swal("Saved", "The record has been saved", "success").then(result => {
            this.isProcessing = false;
          });
        },
        err => {
          swal("Error", "There was an error saving the record", "error").then(
            result => {
              this.isProcessing = false;
            }
          );
        }
      );
    }
  },
  beforeRouteEnter: function(to, from, next) {
    console.log("before route enter");
    let initialisers = [];
    next(vm => {
      console.log("before route enter - next");
      vm.loadCallEmail({ call_email_id: to.params.call_email_id });
    });
  },

  mounted: function() {
    this.renderer_form = document.forms.callEmailUpdate;
    this.$nextTick(function() {
      this.renderer_form = document.forms.callEmailUpdate;
    });
  }
};
</script>

<style lang="css">
</style>