<template>
  <form method="POST" name="enter_return_question" enctype="multipart/form-data">
  <div class="container" id="externalReturnQuestion">

    <Returns v-if="isReturnsLoaded">
    <div class="row">

      <!-- div class="col-md-1" div -->
      <div class="col-md-8">
        <div class="row">
          <template>


                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Return
                      <a class="panelClicker" href="#" data-toggle="collapse"  data-parent="#userInfo" expanded="true" aria-controls="pdBody">
                         <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                      </a>
                    </h3>
                  </div>
                  <div class="panel-body panel-collapse in" id="pdBody">
                    <div class="col-sm-16">
                      <div>
                        <div v-for="(item,index) in returns.table">
                          <renderer-block v-for="(question,key) in item.headers"
                              :component="question"
                              v-bind:key="`q_${key}`"
                          />
                        </div>
                      </div>
                      <!-- End of Question Return -->
                    </div>
                  </div>
                </div>

            <input type='hidden' name="table_name" :value="returns.table[0].name" />
          </template>
          <!-- End template for Return Tab -->
          <div class="row" style="margin-bottom:50px;">
            <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
              <div class="navbar-inner">
                <div class="container">
                  <p class="pull-right" style="margin-top:5px;">
                    <button class="btn btn-primary" name="save_exit">Save and Exit</button>
                    <button class="btn btn-primary" @click.prevent="save()" name="save_continue">Save and Continue</button>
                    <button class="btn btn-primary" name="draft">Submit</button>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </Returns>
  </div>
  </form>
</template>

<script>
import Returns from '../../returns_form.vue'
import { mapActions, mapGetters } from 'vuex'
import $ from 'jquery'
import Vue from 'vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'externalReturnQuestion',
  data() {
    let vm = this;
    return {}
  },
  components: {
    Returns,
  },
  computed: {
    ...mapGetters([
        'isReturnsLoaded',
        'returns',
    ]),
  },
  methods: {
    ...mapActions({
      load: 'loadReturns',
    }),
    ...mapActions([
        'setReturns',
    ]),
    save: function(e) {
      console.log('Save function')
      this.form=document.forms.enter_return_question;
      let data = new FormData(this.form);
      this.$http.post(helpers.add_endpoint_json(api_endpoints.returns,this.returns.id+'/save'),data,{
                       emulateJSON:true,
                    }).then((response)=>{
                       this.returns = response.body;
                       swal('Save',
                            'Returns Saved',
                            'success'
                       );
                    },(error)=>{
                        console.log(error);
                    });
    },
  },
  beforeRouteEnter: function(to, from, next) {
     next(vm => {
       vm.load({ url: `/api/returns/${to.params.return_id}.json` })
     });
  },
}
</script>
