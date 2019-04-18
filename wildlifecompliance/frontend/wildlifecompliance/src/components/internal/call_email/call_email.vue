<template lang="html">
    <div class="container">
        <form method="post" name="callEmailUpdate">
            <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
            <input type='hidden' name="schema" :value="JSON.stringify(call_email)" />
            <input type='hidden' name="call_email_id" :value="1" />
<!--
    v-bind:key="`SWS_Application${index}_0`"
    :instance='call_email.data[0]["Sandalwood - Supplying"][0]["SWS_applicationSection_0"][0]'
    <p>{{ call_email.data[0]["Sandalwood - Supplying"][0]["SWS_applicationSection_0"][0] }}</p>
<p>{{ `SWS_Application${index}_0` }}</p>
                    <p>{{ item }}</p>
                    v-bind:key="`${item.name}`"
                    <p>{{ call_email.data[0]["Sandalwood - Supplying"][0]["SWS_applicationSection_0"][0] }}</p>
                    Object.keys(call_email.data[0]["Sandalwood - Supplying"][0]["SWS_applicationSection_0"][0])
                    :json_data='call_email.data'
                    :instance='item.name'
                    v-bind:key="`compliance_renderer_block_${index}`"
-->
            
            <div>
                <div v-for="dict in call_email.schema">
                <div v-for="(item, index) in dict.children[0].children">
                    <compliance-renderer-block
                        :component="item" 
                        />
                    </div>
                </div>
            </div>
                <div class="col-sm-12">
                    <button @click.prevent="save"
                        class="btn btn-primary pull-right">Save</button>
                </div>
        </form>
        
    </div>
</template>
<script>
//import CallEmail from '../../../components/compliance_form.vue'
import Vue from "vue";
import CommsLogs from "@common-utils/comms_logs.vue";
import { api_endpoints, helpers } from "@/utils/hooks";
import utils from "@/components/external/utils";
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
//import { mapFields } from 'vuex-map-fields'
//import { createNamespacedHelpers } from 'vuex'
//const { mapState, mapGetters, mapActions } = createNamespacedHelpers('callemailStore')
export default {
  name: "ViewCallEmail",
  data: function() {
    let vm = this;
    console.log(this);
    return {
      pBody: "pBody" + vm._uid,
      //form: null,
      loading: [],
      comms_url: "www.google.com",
      comms_add_url: "www.google.com",
      logs_url: "www.google.com",
      rend_text_area: {
        id: "1",
        label: "label",
        status: "status",
        type: "text_area"
      },
      nothing: null,
      renderer_form: null,
      new_form: {},
      dummy_field_data: { SWS_Application1_0: "new new text" }
      //field_data: call_email.data[0]["Sandalwood - Supplying"][0]["SWS_applicationSection_0"][0][item.name]
      //data: function() {}
      /*
                        call_email: function() {
                        console.log("computed");
                        console.log(this.$store.state.call_email);
                        return this.$store.state.call_email
                        },
                        */
      /*
                        status: null,
                        classification: null,
                        lodgement_date: null,
                        number: null,
                        caller: null,
                        assigned_to: null,
                        callEmailId: null,
                        loading: [],
                        form: null,
                        pBody: 'pBody' + vm._uid,
                        callEmailDetails: 'bb_test_details',
                        //myNewVar: 'new_var',
                        savingCallEmail: null,
                        type: 'call_email'
                        */
    };
  },

  components: {
    //CallEmail,
    CommsLogs
  },
  computed: {
    /*
            ...mapState({
                call_email: state.callemailStore 
            }
            ),
            */
    ...mapGetters({
      call_email: "callemailStore/call_email",
      //call_id: "callemailStore/call_id",
      selected_tab_id: "complianceUserStore/selected_tab_id",
      selected_tab_name: "complianceUserStore/selected_tab_name"

      //stored_renderer_data: "callemailStore/stored_renderer_data"
    }),
    csrf_token: function() {
      return helpers.getCookie("csrftoken");
    },
    /*
            ...mapFields({
                callemail_classification_name: "call_email.classification['name']",
                callemail_number: 'call_email.number',
                callemail_caller: 'call_email.caller',
                callemail_assigned_to: 'call_email.assigned_to',

            }),
            */
    isLoading: function() {
      return this.loading.length > 0;
    },
    call_email_form_url: function() {
      return this.call_email
        ? `/api/call_email/${this.call_email.id}/form_data.json`
        : "";
    }
    /*
            setValue: function () {
                this.call_email.stored_data = 
                { "SWS_Application1_0": 
                { "value": this.call_email.data[0]["Sandalwood - Supplying"][0]["SWS_applicationSection_0"][0]["SWS_Application1_0"],  "schema_name": "SWS_Application1_0", 
                "component_type": "text" 
                }, 
                "SWS_Application2_0": 
                { "value": this.call_email.data[0]["Sandalwood - Supplying"][0]["SWS_applicationSection_0"][0]["SWS_Application2_0"],
                    "schema_name": "SWS_Application2_0", "component_type": "text" }, 
                    
                }
                //this.call_email.data[0]["Sandalwood - Supplying"][0]["SWS_applicationSection_0"][0];
            },
            */
    /*
            renderer_form: function() {
                this.form = document.forms.callEmailUpdate;
            },
            */

    //call_email: this.$store.call_email
  },
  methods: {
    ...mapActions({
      load: "callemailStore/loadCallEmail",
      saveFormData: "complianceRendererStore/saveFormData"
    }),
    /*
            ...mapMutations([
                'updateCallEmail',
                'updateClassification',
                'updateNumber',
                'updateCaller',
                'updateAssignedTo',
            ]),
            
            updateClassification (e) {
                this.$store.commit('updateClassification', e.target.value)
                console.log("classification")
                console.log(this.call_email.classification)
            },
            */
    createCallEmail: function(e) {
      //this.renderer_form = document.forms.callEmailUpdate;
      //this.new_form = document.forms.newCallEmail;

      let formData = new FormData(this.renderer_form);

      //formData.append('additional_key_example', 'some_val') // example of additonal info sent to server
      console.log(formData);
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
  /*
        watch: {
            renderer_form: function() {
                this.renderer_form = document.forms.callEmailUpdate;
            }

        },
        */
  beforeRouteEnter: function(to, from, next) {
    console.log("before route enter");
    let initialisers = [];
    next(vm => {
      console.log("before route enter - next");
      vm.load({ call_email_id: to.params.call_email_id });
      //Promise.all(initialisers).then(data => {
      //})
    });
  },

  mounted: function() {
    this.renderer_form = document.forms.callEmailUpdate;
    this.$nextTick(function() {
      //this.form = document.forms.callEmailUpdate;
      this.renderer_form = document.forms.callEmailUpdate;
      //this.new_form = document.forms.newCallEmail;
    });
  }

  /*
        mounted: function () {
            let vm = this;
            vm.form = document.forms.createForm;
        },
        */
};
</script>

<style lang="css">
</style>