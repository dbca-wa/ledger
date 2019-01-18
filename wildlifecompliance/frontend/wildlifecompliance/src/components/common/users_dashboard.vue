<template id="user_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">People <small v-if="is_external">View people details</small>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="user_datatable" :id="datatable_id" :dtOptions="user_options" :dtHeaders="user_headers"/>
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
    name: 'UserDashTable',
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
            datatable_id: 'user-datatable-'+vm._uid,
            // Filters for Users 
            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },
            user_headers:["Title","Given Name(s)","Last Name","Date of Birth","Email","Phone","Mobile","Fax","Character Flagged","Character Comments","Action"],
            user_options:{
                serverSide: true,
                searchDelay: 1000,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.url,
                },
                columns: [
                    {data: "title"},
                    {data: "first_name"},
                    {data: "last_name"},
                    {
                        data: "dob",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        }
                    },
                    {data: "email"},
                    {data: "phone_number"},
                    {data: "mobile_number"},
                    {data: "fax_number"},
                    {data: "character_flagged"},
                    {data: "character_comments"},
                    {
                        data:"id",
                        mRender:function(data, type, full){
                            let links = ''
                            links += "<a href='/internal/users/\__ID__\'> Edit</a><br/>";
                            links +=  `<a href='#${full.id}' apply-on-behalf-of='${full.id}'>New Application</a>`;

                            return links.replace(/__ID__/g, data);
                        }
                    },
                ],
                processing: true,
                initComplete: function () {
                    // Fix the table rendering columns
                    vm.$refs.user_datatable.vmDataTable.columns.adjust().responsive.recalc();
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
        
    },
    methods: {
        applyOnBehalfOf:function (user_id) {
            let vm = this;
            console.log('from user list - apply on behalf of: ',user_id);
             vm.$router.push({
                  name:"apply_application_licence",
                  params:{
                    proxy_select: user_id
                  }
              });
        },
        addEventListeners: function(){
            let vm = this;
            // Apply on behalf of listener
            vm.$refs.user_datatable.vmDataTable.on('click', 'a[apply-on-behalf-of]', function(e) {
                e.preventDefault();
                var id = parseInt($(this).attr('apply-on-behalf-of'));
                vm.applyOnBehalfOf(id);
            });
        }
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.addEventListeners();
        });
    }
}
</script>
<style scoped>
</style>
