<template id="profile_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Profiles <small v-if="is_external">View profile details</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#profileInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="profile_datatable" :id="datatable_id" :dtOptions="profile_options" :dtHeaders="profile_headers"/>
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
                let options = ['internal','referral'];
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
            profile_headers:["Profile Name","Email","Institution","Postal Address","Action"],
            profile_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": api_endpoints.profiles,
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
                    {data: "name"},
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
        },
        is_referral: function(){
            return this.level == 'referral';
        }
    },
    methods: {
    },
    mounted: function(){
        let vm = this;
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        });
        this.$nextTick(() => {
            vm.addEventListeners();
            vm.initialiseSearch();
        });
    }
}
</script>
<style scoped>
</style>
