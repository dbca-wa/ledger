<template id="organisation_dashboard">
    <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h3 class="panel-title">Organisations
                        <a :href="'#'+oBody" data-toggle="collapse"  data-parent="#userInfo" expanded="true" :aria-controls="oBody">
                            <span class="glyphicon glyphicon-chevron-up pull-right "></span>
                        </a>
                    </h3>
                </div>
                <div class="panel-body collapse in" :id="oBody">
                    <div class="row">
                        <div class="col-lg-12">
                            <datatable ref="organisation_datatable" :id="datatable_id" :dtOptions="organisation_options" :dtHeaders="organisation_headers"/>
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
    name: 'OrganisationDashTable',
    data() {
        let vm = this;
        return {
            oBody: 'oBody' + vm._uid,
            datatable_id: 'organisation-datatable-'+vm._uid,
            organisation_headers: ["Name", "ABN", "Address", "Action"],
            organisation_options:{
                serverSide: true,
                searchDelay: 1000,
                lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                order: [
                    [0, 'asc']
                ],
                tableID: 'organisation-datatable-'+vm._uid,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_join(api_endpoints.organisations_paginated,'datatable_list/?format=datatables'),
                    "dataSrc": "data",
                },
                columns: [
                    {
                        data: "name",
                        name: "organisation__name"
                    },
                    {
                        data: "abn",
                        name: "organisation__abn"
                    },
                    {
                        data: "address_string",
                        mRender:function (data,type,full) {
                            if (data) {
                                return data;
                            }
                            return ''
                        },
                        orderable: false,
                        searchable: false // handled by filter_queryset override method - class OrganisationFilterBackend
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            links +=  `<a href='/internal/organisations/${full.id}'>View</a><br/>`;
                            return links;
                        },
                        orderable: false,
                        searchable: false
                    }
                ],
                processing: true,
                initComplete: function () {
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
    },
    methods:{
    },
    mounted: function(){
        let vm = this;
        $( 'a[data-toggle="collapse"]' ).on( 'click', function () {
            var chev = $( this ).children()[ 0 ];
            window.setTimeout( function () {
                $( chev ).toggleClass( "glyphicon-chevron-down glyphicon-chevron-up" );
            }, 100 );
        });
    }
}
</script>
<style scoped>
</style>
