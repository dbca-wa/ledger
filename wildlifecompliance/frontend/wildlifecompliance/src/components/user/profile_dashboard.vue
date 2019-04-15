<template id="profile_dashboard">
<div class="container" id="profiles">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">My Profiles <small v-if="is_external">View profile details</small>
                        <a href="/profiles/create" class="pull-right btn btn-primary" style="color:#fff">Create Profile</a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div>Profiles let you link multiple email addresses with your account, allowing you to log in with any linked email address.</div><br/>
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="profile_datatable" :id="datatable_id" :dtOptions="profile_options" :dtHeaders="profile_headers"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'

export default {
    name: 'ProfileDashTable',
    props: {
        level:{
            type: String,
            required: true,
            validator:function(val) {
                let options = ['internal'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        url:{
            type: String,
            required: true
        }
    },
    data() {
        let vm = this;
        return {
            pBody: 'pBody' + vm._uid,
            datatable_id: 'profile-datatable-'+vm._uid,
            // Filters for Profiles 
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            profile_headers:["Profile Name","Email","Institution","Postal Address","Actions"],
            profile_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": api_endpoints.my_profiles,
                    "dataSrc": ''
                },
                columns: [
                    {data: "name"},
                    {data: "email"},
                    {data: "institution"},
                    {
                        mRender:function (data,type,full) {
                            return full.postal_address.line1 + " " + full.postal_address.line2 + " " + full.postal_address.line3 + " " + full.postal_address.locality + " " + full.postal_address.state + " " + full.postal_address.country + " " + full.postal_address.postcode;
                        }
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            links +=  `<a href='/profiles/${full.id}' class="editProfile">Edit</a><br/>`;
                            links +=  `<a data-name='${full.name}' data-email='${full.email}' data-id='${full.id}' class="delete_profile">Delete</a><br/>`;
                            return links;
                        },
                        orderable: false
                    },
                ],
                processing: true,
                initComplete: function () {
                    // Fix the table rendering columns
                    vm.$refs.profile_datatable.vmDataTable.columns.adjust().responsive.recalc();
                }
            }
        }
    },
    components:{
        datatable
    },
    watch:{
    },
    computed: {
        status: function(){
            //return this.is_external ? this.external_status : this.internal_status;
            return [];
        },
        is_external: function(){
            return this.level == 'external';
        }
    },
    methods: {
        deleteProfile: function(id,name,email){
            let vm = this;
            vm.$http.delete(api_endpoints.profiles + "/" + id + '/'
            ).then((response) => {
                swal(
                    'Delete Profile',
                    'Your profile, ' + name + ' (' + email + ') has been successfully deleted.',
                    'success'
                )
                vm.$refs.profile_datatable.vmDataTable.ajax.reload();
            }, (error) => {
                console.log(error);
                swal(
                    'Delete Profile',
                    'There was an error deleting the profile, ' + name + ' (' + email + ').',
                    'error'
                )
            });
        },
        eventListeners: function(){
            let vm = this;
            vm.$refs.profile_datatable.vmDataTable.on('click','.delete_profile',(e) => {
                e.preventDefault();
                let name = $(e.target).data('name');
                let email = $(e.target).data('email');
                let id = $(e.target).data('id');
                swal({
                    title: "Delete Profile",
                    text: 'Are you sure you want to delete this profile, ' + name + ' (' + email + ')?',
                    type: "error",
                    showCancelButton: true,
                    confirmButtonText: 'Delete',
                    focusCancel: true
                }).then((result) => {
                    if(result.value) {
                        vm.deleteProfile(id,name,email);
                    } else if (result.dismiss === swal.DismissReason.cancel) {
                        return;
                    }

                },(error) => {
                    console.log(error);
                });
            });
        }
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            this.eventListeners();
        });
    }
}
</script>
<style scoped>
</style>
