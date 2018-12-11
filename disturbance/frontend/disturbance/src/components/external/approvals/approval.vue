<template>
<div class="container" id="externalApproval">
    <div class="row">
        <h3>Approval {{ approval.lodgement_number }}</h3>
      
        
        <div class="col-sm-12">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">Holder
                            <a class="panelClicker" :href="'#'+pBody" data-toggle="collapse" expanded="false"  data-parent="#userInfo" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                        </h3> 
                    </div>
                    <div class="panel-body panel-collapse" :id="pBody">
                        <div class="row">
                            <div class="col-sm-12">
                                <form class="form-horizontal" name="approval_form">
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">Organisation</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="name" placeholder="" v-model="org.name">
                                        </div>
                                    </div>   
                                    <div class="form-group">
                                        <label for="" class="col-sm-3 control-label">ABN</label>
                                        <div class="col-sm-6">
                                            <input type="text" disabled class="form-control" name="abn" placeholder="" v-model="org.abn">
                                        </div>
                                    </div>                                      
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
               
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Address Details 
                        <a class="panelClicker" :href="'#'+adBody" data-toggle="collapse" expanded="true"  data-parent="#userInfo" :aria-controls="adBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div v-if="loading.length == 0" class="panel-body collapse" :id="adBody">
                      <form class="form-horizontal" action="index.html" method="post">
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Street</label>
                            <div class="col-sm-6">
                                <input type="text" disabled class="form-control" name="street" placeholder="" v-model="org.address.line1">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                            <div class="col-sm-6">
                                <input type="text" disabled class="form-control" name="surburb" placeholder="" v-model="org.address.locality">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">State</label>
                            <div class="col-sm-3">
                                <input type="text" disabled class="form-control" name="country" placeholder="" v-model="org.address.state">
                            </div>
                            <label for="" class="col-sm-1 control-label">Postcode</label>
                            <div class="col-sm-2">
                                <input type="text" disabled class="form-control" name="postcode" placeholder="" v-model="org.address.postcode">
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Country</label>
                            <div class="col-sm-4">
                                <input type="text" disabled class="form-control" name="country" v-model="org.address.country">
                                </input>
                            </div>
                          </div>
                       </form>
                  </div>
                </div>
           
            </div>

            <div class="row">
                
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <h3 class="panel-title">Approval Details 
                        <a class="panelClicker" :href="'#'+oBody" data-toggle="collapse" expanded="true"  data-parent="#userInfo" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                        </a>
                    </h3>
                  </div>
                  <div v-if="loading.length == 0" class="panel-body collapse" :id="oBody">
                      <form class="form-horizontal" action="index.html" method="post">
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Issue Date</label>
                            <div class="col-sm-6">
                                <label for="" class="control-label pull-left">{{approval.issue_date | formatDate}}</label>
                            </div>
                        <!---    <div class="col-sm-6">
                                <p>{{approval.issue_date | formatDate}}</p>
                            </div> -->
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Start Date</label>
                            <div class="col-sm-6">
                                <label for="" class="control-label pull-left">{{approval.start_date | formatDate}}</label>
                            </div>
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label">Expiry Date</label>
                            <div class="col-sm-3">
                                <label for="" class="control-label pull-left">{{approval.expiry_date | formatDate}}</label>
                            </div>
                            
                          </div>
                          <div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Document</label>
                            <div class="col-sm-4">
                                <p><a target="_blank" :href="approval.licence_document" class="control-label pull-left">Approval.pdf</a></p>
                            </div>
                          </div>
                       </form>
                  </div>
                </div>         
            </div>
        </div>
    </div>
</div>
</template>
<script>
import $ from 'jquery'
import Vue from 'vue'
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
export default {
  name: 'Approval',
  data() {
    let vm = this;
    return {
        loading: [],
        approval: {
            applicant_id: null
            
        },
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        adBody: 'adBody'+vm._uid,
        pBody: 'pBody'+vm._uid,
        cBody: 'cBody'+vm._uid,
        oBody: 'oBody'+vm._uid,
        org: {
            address: {}
        },
        
        // Filters
        
    }
  },
  watch: {},
  filters: {
    formatDate: function(data){
        return moment(data).format('DD/MM/YYYY');
    }
  },
  beforeRouteEnter: function(to, from, next){
    Vue.http.get(helpers.add_endpoint_json(api_endpoints.approvals,to.params.approval_id)).then((response) => {
        next(vm => {
            vm.approval = response.body;
            vm.approval.applicant_id = response.body.applicant_id;
            vm.fetchOrganisation(vm.approval.applicant_id)

        })
    },(error) => {
        console.log(error);
    }) 
  },
  components: {
    datatable,
    CommsLogs
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    
  },
  methods: {
    commaToNewline(s){
        return s.replace(/[,;]/g, '\n');
    },
    fetchOrganisation(applicant_id){
        let vm=this;
        Vue.http.get(helpers.add_endpoint_json(api_endpoints.organisations,applicant_id)).then((response) => {
        
            vm.org = response.body;
            vm.org.address = response.body.address;         
    },(error) => {
        console.log(error);
    })

    },
  
  
  },
  mounted: function () {
    let vm = this;
  }
}
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}
</style>
