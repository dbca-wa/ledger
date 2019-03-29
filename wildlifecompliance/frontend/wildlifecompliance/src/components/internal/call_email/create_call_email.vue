<template lang="html">
    <div class="container">
        <div class="row">
            <div class="col-sm-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <h3 class="panel-title">New Call / Email
                            <a :href="'#'+pBody" data-toggle="collapse" data-parent="#userInfo" expanded="true"
                                :aria-controls="pBody">
                                <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                            </a>
                        </h3>
                    </div>
                    <div class="panel-body collapse in" :id="pBody">
                        <form class="form-horizontal" name="createForm" method="post">
                            <input type="hidden" name="create_type" value="call_email"/>
                            <input type="hidden" name="status" value="draft"/>
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Classification</label>
                                    <input type="text" name="classification" v-model="classification" value="Complaint">
                                </div>
                            </div>
                            <!--
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Lodgment Date</label>
                                    <input type="date" name="lodgement_date" v-model="lodgement_date">
                                </div>
                            </div>
                            -->
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Number</label>
                                    <input type="text" name="number" v-model="number" value="CM67">
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Caller</label>
                                    <input type="text" name="caller" v-model="caller" value="Shayne">
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Assigned To</label>
                                    <input type="text" name="assigned_to" v-model="assigned_to" value="Brendan">
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <button v-if="!savingCallEmail" @click.prevent="createCallEmail"
                                    class="btn btn-primary pull-right">BB
                                    Save</button>
                                <button v-if="!savingCallEmail" @click.prevent="save_exit"
                                    class="btn btn-primary pull-right">Save and
                                    Return</button>
                                <button v-if="!savingCallEmail" @click.prevent="save_wo_confirm"
                                    class="btn btn-primary pull-right">Save
                                    and Continue</button>
                                <button v-else disabled class="pull-right btn btn-primary"><i
                                        class="fa fa-spin fa-spinner"></i>&nbsp;Saving</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
    import Application from '../../form.vue'
    import Vue from 'vue'
    import {
        api_endpoints,
        helpers
    }
    from '@/utils/hooks'
    //import utils from './utils'
    import utils from '@/components/external/utils'
    export default {
        data: function () {
            let vm = this;

            return {
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
            }
        },
        components: {
            Application
        },
        computed: {
            isLoading: function () {
                return this.loading.length > 0
            },
            call_email_form_url: function () {
                //return (this.call_email_id) ? `/api/call_email/${this.call_email_id}/draft.json` : '';
                //return (this.callEmailId) ? `/api/call_email/${this.callEmailIid}/call_email_save.json` : '';
                //return (`/api/call_email/${this.callEmailId}/call_email_save.json`);
                
                //return (`/api/call_email.json`);
            },
        },
        ajax: {
                "url": helpers.add_endpoint_json(api_endpoints.call_email, 'datatable_list'),
                "dataSrc": '',
        },
        created() {
            console.log(this.$route.params.id);
            console.log(this.callEmailId);
            this.callEmailId = this.$route.params.id;
        },
        methods: {
            save_wo_confirm: function (e) {
                let vm = this;
                let formData = new FormData(vm.form);
                this.savingCallEmail = true;
                vm.$http.post(vm.call_email_form_url, formData).then(res => {
                    this.savingCallEmail = false;
                }, (error) => {});
            },
            createCallEmail: function (e) {
                let vm = this;
                let formData = new FormData(vm.form);
                vm.callEmailId = 66;
                formData.append('additional_key_example', 'some_val') // example of additonal info sent to server
                //console.log(formData);
                //console.log(api_endpoints.call_email);
                //console.log(vm.data.classification);
                vm.$http.post('/api/call_email/', formData).then(
                    res => {
                    swal(
                        'Saved',
                        'Your Call/Email has been saved',
                        'success'
                    );
                    }, err => {});
            },
            save_exit: function (e) {
                let vm = this;
                vm.savingCallEmail = true;
                vm.save(e);
                // redirect back to dashboard
                vm.$router.push({
                    //name: 'external-proposals-dash'
                    name: 'internal-call_emails-dash' // defined in ../src/components/internal/routes/index.js
                });
            },
            /*
            save: function() {
                let vm = this;
                swal({
                    title: "Save Call / Email",
                    text: "Are you sure you want to create a Call/Email",
                    type: "question",
                    showCancelButton: true,
                    confirmButtonText: 'Accept'
                }).then(() => {
                    vm.saveCallEmail();
                },(error) => {
                });
            },
            save_exit:function () {
                let vm = this;
                vm.savingCallEmail = true;
                let formData = new FormData(vm.form);
                formData.append('additional_key_example', 'some_key')
                vm.$http.post(vm.call_email_form_url,formData).then(res=>{
                    vm.proposal = res.body;
                    vm.$router.push({
                        name:"draft_call_email", // defined in ../src/components/internal/routes/index.js
                        params:{call_email_id:vm.call_email.id}
                    });
                    vm.savingCallEmail = false;
                },
                err => {
                    console.log(err);
                });
            },
            submit: function() {
                let vm = this;
                 vm.$router.push({
                              name:"apply_application_organisation",
                              params:{licence_select:vm.licence_select}
                          });
                 console.log(vm.licence_select);
            },
            createApplication:function () {
                let vm = this;
                vm.$http.post('/api/application.json',{
                    behalf_of: vm.behalf_of
                }).then(res => {
                      vm.application = res.body;
                      
                  },
                  err => {
                    console.log(err);
                  });
            },
            createCallEmail:function () {
                let vm = this;
                //vm.$http.post('/api/application.json',{
                    //behalf_of: vm.behalf_of
                vm.form = document.forms.createForm;
                let formData = new FormData(vm.form);
                vm.$http.post('/api/call_emails.json',formData).then(res=>{
                  swal(
                    'Created',
                    'Your Call/Email has been created',
                    'success'
                  )
                },err=>{
                });
            }
            */
        },
        beforeRouteEnter: function (to, from, next) {
            console.log("before route enter");
            let initialisers = [
                //utils.fetchProfile(),
                //utils.fetchApplication(to.params.application_id)
            ]
            next(vm => {
                console.log("before route enter - next");
                Promise.all(initialisers).then(data => {
                    vm.profile = data[0];
                    //vm.application = data[1];
                })
            })
        },

        mounted: function () {
            let vm = this;
            vm.form = document.forms.createForm;
        },


    }
</script>

<style lang="css">
</style>