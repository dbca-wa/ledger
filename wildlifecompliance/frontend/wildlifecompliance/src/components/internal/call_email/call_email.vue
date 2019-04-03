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
                                    <input type="text" name="classification" v-model="call_email.classification.name" value="Complaint">
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
                            <div class="col-sm-12">
                                <button @click.prevent="createCallEmail"
                                    class="btn btn-primary pull-right">Update</button>
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
    import utils from '@/components/external/utils'
    import { mapState, mapGetters, mapActions } from 'vuex'
    //import { createNamespacedHelpers } from 'vuex'
    //const { mapState, mapGetters, mapActions } = createNamespacedHelpers('callemailStore')
    export default {
        data: function () {
            let vm = this;
            console.log(this);
            return {
                        pBody: 'pBody' + vm._uid,
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
        },
        computed:
            {
            
            ...mapGetters({
                call_email: 'getCallEmail',

            }),
        },
        methods: {
            ...mapActions({
                load: 'loadCallEmail',
            }),
            createCallEmail: function (e) {
                let vm = this;
                let formData = new FormData(vm.form);
                formData.append('additional_key_example', 'some_val') // example of additonal info sent to server
                vm.$http.post('/api/call_email/', formData).then(
                    res => {
                    swal(
                        'Saved',
                        'Your Call/Email has been saved',
                        'success'
                    );
                    }, err => {});
                vm.$router.push({
                    name: 'internal-call_emails-dash'
                });
            },
        },
        
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
            let vm = this;
            vm.form = document.forms.createForm;
        },


    }
</script>

<style lang="css">
</style>