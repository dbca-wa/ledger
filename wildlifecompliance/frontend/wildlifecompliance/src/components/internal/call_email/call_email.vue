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
                        <!--
                        <form method="post" name="newCallEmail" enctype="multipart/form-data">
                        <form :action="call_email_form_url" method="post" name="newCallEmail" enctype="multipart/form-data">       
                        -->
                        <form method="post" name="newCallEmail">
                            <input type="hidden" name="create_type" value="call_email"/>
                            <input type="hidden" name="status" value="draft"/>
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Classification</label>
                                    <input type="text" name="classification" v-model="call_email.classification.name" value="Complaint">
                                </div>
                            </div>
        
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Number</label>
                                    <input type="text" name="number" v-model="call_email.number" value="CM67">
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Caller</label>
                                    <input type="text" name="caller" v-model="call_email.caller" value="Shayne">
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Assigned To</label>
                                    <input type="text" name="assigned_to" v-model="call_email.assigned_to" value="Brendan">
                                </div>
                            
                            </div>

        
                        </form>   
                        
                    </div>
                </div>
            </div>
        </div>
        <form method="post" name="callEmailUpdate">
            <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
            <input type='hidden' name="schema" :value="JSON.stringify(call_email)" />
            <!--
            <input type='hidden' name="application_id" :value="1" />
            -->
            <div>
                <div v-for="dict in call_email.report_type.schema">
                <div v-for="(item, index) in dict.children[0].children">
                    <renderer-block
                        :component="item" 
                        :value="call_email.data"
                        v-bind:key="`q_${index}`"
                        />
                </div>
                </div>
            </div>
                <div class="col-sm-12">
                    <button @click.prevent="createCallEmail"
                        class="btn btn-primary pull-right">Save</button>
                </div>
        </form>
    </div>
</template>
<script>
    //import CallEmail from '../../../components/compliance_form.vue'
    import Vue from 'vue'
    import CommsLogs from '@common-utils/comms_logs.vue'
    import {
        api_endpoints,
        helpers
    }
    from '@/utils/hooks'
    import utils from '@/components/external/utils'
    import { mapState, mapGetters, mapActions, mapMutations } from 'vuex'
    //import { mapFields } from 'vuex-map-fields'
    //import { createNamespacedHelpers } from 'vuex'
    //const { mapState, mapGetters, mapActions } = createNamespacedHelpers('callemailStore')
    export default {
        name: 'ViewCallEmail',
        data: function () {
            let vm = this;
            console.log(this);
            return {
                        pBody: 'pBody' + vm._uid,
                        //form: null,
                        loading: [],
                        comms_url: 'www.google.com',
                        comms_add_url: 'www.google.com',
                        logs_url: 'www.google.com',
                        rend_text_area: {
                        id: '1',
                        label: 'label',
                        status: 'status',
                        type: 'text_area'
                        },
                        nothing: null,
                        renderer_form: {},
                        new_form: {},
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
            }
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
                call_email: 'callemailStore/call_email',

            }),
            csrf_token: function() {
                return helpers.getCookie('csrftoken')
            },
            /*
            ...mapFields({
                callemail_classification_name: "call_email.classification['name']",
                callemail_number: 'call_email.number',
                callemail_caller: 'call_email.caller',
                callemail_assigned_to: 'call_email.assigned_to',

            }),
            */
            isLoading: function () {
                return this.loading.length > 0
            },
            call_email_form_url: function() {
                return (this.call_email) ? `/api/call_email/${this.call_email.id}/update_call.json` : '';
            },
            /*
            renderer_form: function() {
                this.form = document.forms.callEmailUpdate;
            },
            */
            
            //call_email: this.$store.call_email
        },
        methods: {
            ...mapActions({
                load: 'callemailStore/loadCallEmail',
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
            createCallEmail: function (e) {
                this.renderer_form = document.forms.callEmailUpdate;
                this.new_form = document.forms.newCallEmail;
                let formData = new FormData(this.renderer_form);
                
                //formData.append('additional_key_example', 'some_val') // example of additonal info sent to server
                console.log(formData);
                this.$http.post(helpers.add_endpoint_join(
                    api_endpoints.call_email,
                    this.call_email.id+'/update_renderer_form/'), formData)
                .then(
                    res => {
                    swal(
                        'Saved',
                        'Your Call/Email has been saved',
                        'success'
                    );
                    }, err => {});
                /*
                this.$router.push({
                    name: 'internal-call-email-dash'
                });
                */    
            },
            
        },
        /*
        watch: {
            renderer_form: function() {
                this.renderer_form = document.forms.callEmailUpdate;
            }

        },
        */
        beforeRouteEnter: function (to, from, next) {
            console.log("before route enter");
            let initialisers = [
            ]
            next(vm => {
                console.log("before route enter - next");
                vm.load({call_email_id: to.params.call_email_id});
                Promise.all(initialisers).then(data => {
                })
            })
        },
        
        mounted: function () {
            //this.form = document.forms.createForm;
            //this.form = document.forms.createForm;
            //this.form = document.forms.newCallEmail;
            //this.renderer_form = document.forms.newCallEmail;
            //this.renderer_form = document.forms.callEmailUpdate;
            this.$nextTick( function() {
            this.renderer_form = document.forms.callEmailUpdate;
            this.new_form = document.forms.newCallEmail;
            //this.form = document.forms.new_call_email;
            //this.form = document.forms.createForm;
            })
            
        },
        
        /*
        mounted: function () {
            let vm = this;
            vm.form = document.forms.createForm;
        },
        */


    }
</script>

<style lang="css">
</style>