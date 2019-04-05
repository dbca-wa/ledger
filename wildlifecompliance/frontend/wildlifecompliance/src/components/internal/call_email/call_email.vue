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
                                    <!--

                                    <input type="text" :value="call_email.classification.name"
                                    
                                    @change="updateClassification">
                                    -->
                                    <input type="text" name="classification" v-model="call_email.classification.name">                                    
                                    
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
                                    <!--
                                    <input type="text" name="number" :value="call_email.number">

                                    -->
                                    <input type="text" name="number" v-model="call_email.number">                                    
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Caller</label>
                                    <input type="text" name="caller" v-model="call_email.caller">
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <div class="row">
                                    <label class="col-sm-4">Assigned To</label>
                                    <input type="text" name="assigned_to" v-model="call_email.assigned_to">
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <button @click.prevent="createCallEmail"
                                    class="btn btn-primary pull-right">Update</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

    <!--
     <Application form_width="inherit" :withSectionsSelector="false" v-if="isApplicationLoaded">
                                    <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token"/>
                                    <input type='hidden' name="schema" :value="JSON.stringify(application)" />
                                    <input type='hidden' name="application_id" :value="1" />
                                    <input type='hidden' id="selected_activity_tab_id" v-model="selected_activity_tab_id" />
                                    <div class="row" style="margin-bottom:50px;">
                                        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                                            <div class="navbar-inner">
                                                <div class="container">
                                                    <p class="pull-right" style="margin-top:5px;">
                                                        <button v-if="canReturnToConditions" class="btn btn-primary" @click.prevent="returnToOfficerConditions()">Return to Officer - Conditions</button>
                                                        <button v-if="canCompleteAssessment" class="btn btn-info" @click.prevent="toggleConditions()">Assess</button>
                                                        <button v-if="!applicationIsDraft && canRequestAmendment" class="btn btn-primary" @click.prevent="save()">Save Changes</button>
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </Application>
            -->
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <CallEmail form_width="inherit" :withSectionsSelector="false" >
                
                                    <input type='hidden' name="schema" :value="JSON.stringify(call_email)" />
                                    <div class="row" style="margin-bottom:50px;">
                                        <div class="navbar navbar-fixed-bottom" style="background-color: #f5f5f5 ">
                                            <div class="navbar-inner">
                                                <div class="container">
                                                    <p class="pull-right" style="margin-top:5px;">
                                                        <button class="btn btn-primary" @click.prevent="returnToOfficerConditions()">Return to Officer - Conditions</button>
                                                        <button class="btn btn-info" @click.prevent="toggleConditions()">Assess</button>
                                                        <button class="btn btn-primary" @click.prevent="save()">Save Changes</button>
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>


            </CallEmail>
                
            </div>   
    </div>
</template>
<script>
    import CallEmail from '../../../components/compliance_form.vue'
    import Vue from 'vue'
    import CommsLogs from '@common-utils/comms_logs.vue'
    import {
        api_endpoints,
        helpers
    }
    from '@/utils/hooks'
    import utils from '@/components/external/utils'
    //import { mapState, mapGetters, mapActions, mapMutations } from 'vuex'
    //import { mapFields } from 'vuex-map-fields'
    import { createNamespacedHelpers } from 'vuex'
    const { mapState, mapGetters, mapActions } = createNamespacedHelpers('callemailStore')
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
            CallEmail,
            CommsLogs
        },
        computed: {
            /*
            ...mapState({
                call_email: state.callemailStore 
            }
            ),
            */
            ...mapGetters([
                'call_email',

            ]),
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
            
            
            //call_email: this.$store.call_email
        },
        methods: {
            ...mapActions({
                load: 'loadCallEmail',
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
                let formData = new FormData(this.form);
                
                formData.append('additional_key_example', 'some_val') // example of additonal info sent to server
                console.log(this);
                this.$http.post('/api/call_email/', formData).then(
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

        }
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
            
            this.$nextTick( function() {
            this.form = document.forms.createForm;
            })
            
        },


    }
</script>

<style lang="css">
</style>