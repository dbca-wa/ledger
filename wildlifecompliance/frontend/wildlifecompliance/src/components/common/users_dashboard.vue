<template id="user_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">People <small v-if="is_external">View people details</small>
                        <a :href="'#'+pBody" data-toggle="collapse"  data-parent="#peopleInfo" expanded="true" :aria-controls="pBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="pBody">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label for="">Character Flagged</label>
                                <select class="form-control" v-model="filterCharacterFlagged">
                                    <option value="All">All</option>
                                    <option v-for="c in character_flagged_options" :value="c">{{c}}</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <label for="">Date of Birth</label>
                            <div class="input-group date" ref="filterDateOfBirthPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterDateOfBirth">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
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
            filterCharacterFlagged: 'All',
            character_flagged_options: ['True','False'],
            filterDateOfBirth: '',
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
                lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                order: [
                    [4, 'asc']
                ],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.url,
                    "data": 'data',
                    // adding extra GET params for Custom filtering
                    "data": function (d) {
                        d.character_flagged = vm.filterCharacterFlagged;
                        d.dob = vm.filterDateOfBirth != '' && vm.filterDateOfBirth != null ? moment(vm.filterDateOfBirth, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                    }
                },
                columns: [
                    {data: "title"},
                    {data: "first_name"},
                    {data: "last_name"},
                    {
                        data: "dob",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format(vm.dateFormat): '';
                        },
                        searchable: false
                    },
                    {data: "email"},
                    {data: "phone_number"},
                    {data: "mobile_number"},
                    {data: "fax_number"},
                    {
                        data: "character_flagged",
                        orderable: false,
                        searchable: false,
                        className: "capitalise"
                    },
                    {data: "character_comments"},
                    {
                        data:"id",
                        mRender:function(data, type, full){
                            let links = ''
                            links += "<a href='/internal/users/\__ID__\'> Edit</a><br/>";
                            links +=  `<a href='#${full.id}' apply-on-behalf-of='${full.id}'>New Application</a>`;

                            return links.replace(/__ID__/g, data);
                        },
                        orderable: false,
                        searchable: false
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
        filterDateOfBirth: function(){
            this.$refs.user_datatable.vmDataTable.draw();
        },
        filterCharacterFlagged: function(){
            this.$refs.user_datatable.vmDataTable.draw();
        },
    },
    computed: {
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
            // Initialise Date of Birth Filter
            $(vm.$refs.filterDateOfBirthPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.filterDateOfBirthPicker).on('dp.change', function(e){
                if ($(vm.$refs.filterDateOfBirthPicker).data('DateTimePicker').date()) {
                    vm.filterDateOfBirth =  e.date.format('DD/MM/YYYY');
                }
                else if ($(vm.$refs.filterDateOfBirthPicker).data('date') === "") {
                    vm.filterDateOfBirth = "";
                }
             });
            // Apply on behalf of listener
            vm.$refs.user_datatable.vmDataTable.on('click', 'a[apply-on-behalf-of]', function(e) {
                e.preventDefault();
                var id = parseInt($(this).attr('apply-on-behalf-of'));
                vm.applyOnBehalfOf(id);
            });
        },
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
