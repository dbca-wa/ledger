<template id="vehicle_table">
    <div class="row">
        <div class="col-sm-12"> 
            <div class="row" >
                <div class="col-md-3" v-if="!proposal.readonly">
                            <!-- <button style="margin-top:25px;" class="btn btn-primary pull-right">New Application</button> -->
                            <input type="button" style="margin-top:25px;" @click.prevent="newVehicle" class="btn btn-primary" value="Add new vehicle" />
                </div>
            </div>

            <div class="row">
                <div class="col-lg-12" style="margin-top:25px;">
                    <datatable ref="vehicle_datatable" :id="datatable_id" :dtOptions="vehicle_options" :dtHeaders="vehicle_headers"/>
                </div>
            </div>
        </div>
        <editVehicle ref="edit_vehicle" :vehicle_id="vehicle_id" :access_types="access_types" @refreshFromResponse="refreshFromResponse"></editVehicle>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import editVehicle from './edit_vehicle.vue'
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'VehicleTableDash',
    props: {
        // level:{
        //     type: String,
        //     required: true,
        //     validator:function(val) {
        //         let options = ['internal','referral','external'];
        //         return options.indexOf(val) != -1 ? true: false;
        //     }
        // },
        proposal:{
                type: Object,
                required:true
        },
        url:{
            type: String,
            required: true
        },
        access_types:{
            type: Array,
            required: true
        }
    },
    data() {
        let vm = this;
        return {
            new_vehicle:{
                access_type: null,
                capacity:'',
                rego:'',
                rego_expiry:null,
                license:'',
                proposal: vm.proposal.id
            },
            pBody: 'pBody' + vm._uid,
            datatable_id: 'vehicle-datatable-'+vm._uid,
            // Filters for Vehicles
            external_status:[
                'Due',
                'Future',
                'Under Review',
                'Approved',
            ],
            internal_status:[
                'Due',
                'Future',
                'With Assessor',
                'Approved',
            ],
            vehicle_headers:["Number", "Vehicle Type","Seating capacity","Registration no.","Registration Expiry","Transport license no.","Action"],
            vehicle_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                //serverSide: true,
                //lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                ajax: {
                    "url": vm.url,
                    "dataSrc": '',

                    // adding extra GET params for Custom filtering
                    // "data": function ( d ) {
                    //     //d.regions = vm.filterVehicleRegion.join();
                    //     d.date_from = vm.filterComplianceDueFrom != '' && vm.filterComplianceDueFrom != null ? moment(vm.filterComplianceDueFrom, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                    //     d.date_to = vm.filterComplianceDueTo != '' && vm.filterComplianceDueTo != null ? moment(vm.filterComplianceDueTo, 'DD/MM/YYYY').format('YYYY-MM-DD'): '';
                    // }

                },
                dom: 'lBfrtip',
                buttons:[
                'excel', 'csv', ],
                columns: [
                    {
                        data: "id",
                        mRender:function (data,type,full) {
                            //return `C${data}`;
                            return full.id;
                        },
                        //name: "id, lodgement_number",
                    },
                    {
                        data: "access_type",
                        mRender:function (data,type,full) {
                            //return `C${data}`;
                            return data.name;
                        },
                        //name: "vehicle__region__name" // will be use like: Approval.objects.filter(vehicle__region__name='Kimberley')
                    },
                    {
                        data: "capacity",

                        //name: "vehicle__activity",
                    },
                    {
                        data: "rego",
                        //name: "vehicle__title",
                    },
                    {
                        data: "rego_expiry",
                        // mRender:function (data,type,full) {
                        //     return `A${data}`;
                        // },
                        // name: "approval__lodgement_number"
                    },
                    {
                        data: "license",
                        //name: "vehicle__applicant__organisation__name"
                    },
                    {
                        data: '',
                        mRender:function (data,type,full) {
                            let links = '';
                            if(!vm.proposal.readonly){
                            links +=  `<a href='#${full.id}' data-edit-vehicle='${full.id}'>Edit Vehicle</a><br/>`;
                            links +=  `<a href='#${full.id}' data-discard-vehicle='${full.id}'>Discard</a><br/>`;
                        }
                        //     if (!vm.is_external){
                        //         if (full.can_user_view) {
                        //             links +=  `<a href='/internal/compliance/${full.id}'>Process</a><br/>`;
                                    
                        //         }
                        //         else {
                        //             links +=  `<a href='/internal/compliance/${full.id}'>View</a><br/>`;
                        //         }
                        //     }
                        //     else{
                        //         if (full.can_user_view) {
                        //             links +=  `<a href='/external/compliance/${full.id}'>View</a><br/>`;
                                    
                        //         }
                        //         else {
                        //             links +=  `<a href='/external/compliance/${full.id}'>Submit</a><br/>`;
                        //         }
                        //     }
                            return links;
                        },
                        // name: ''  
                    },
                    // {data: "reference", visible: false},
                    // {data: "customer_status", visible: false},
                    // {data: "can_user_view", visible: false},

                ],
                processing: true,
                /*
                initComplete: function () {
                    // Grab Regions from the data in the table
                    var regionColumn = vm.$refs.vehicle_datatable.vmDataTable.columns(1);
                    regionColumn.data().unique().sort().each( function ( d, j ) {
                        let regionTitles = [];
                        $.each(d,(index,a) => {
                            // Split region string to array
                            if (a != null){
                                $.each(a.split(','),(i,r) => {
                                    r != null && regionTitles.indexOf(r) < 0 ? regionTitles.push(r): '';
                                });
                            }
                        })
                        vm.vehicle_regions = regionTitles;
                    });
                    // Grab Activity from the data in the table
                    var titleColumn = vm.$refs.vehicle_datatable.vmDataTable.columns(2);
                    titleColumn.data().unique().sort().each( function ( d, j ) {
                        let activityTitles = [];
                        $.each(d,(index,a) => {
                            a != null && activityTitles.indexOf(a) < 0 ? activityTitles.push(a): '';
                        })
                        vm.vehicle_activityTitles = activityTitles;
                    });

                    // Grab Status from the data in the table
                    var statusColumn = vm.$refs.vehicle_datatable.vmDataTable.columns(6);
                    statusColumn.data().unique().sort().each( function ( d, j ) {
                        let statusTitles = [];
                        $.each(d,(index,a) => {
                            a != null && statusTitles.indexOf(a) < 0 ? statusTitles.push(a): '';
                        })
                        vm.status = statusTitles;
                    });
                }
                */
            }
        }
    },
    components:{
        datatable,
        editVehicle
    },
    watch:{
    },
    computed: {
       /* status: function(){
            return this.is_external ? this.external_status : this.internal_status;
            //return [];
        }, */
        is_external: function(){
            return this.level == 'external';
        },
    },
    methods:{
        fetchFilterLists: function(){
            let vm = this;

            // vm.$http.get(api_endpoints.filter_list_compliances).then((response) => {
            //     vm.vehicle_regions = response.body.regions;
            //     vm.vehicle_activityTitles = response.body.activities;
            //     vm.status = vm.level == 'external' ? vm.external_status: vm.internal_status;
            // },(error) => {
            //     console.log(error);
            // })
            //console.log(vm.regions);
        },
        newVehicle: function(){
            let vm=this;
            this.$refs.edit_vehicle.vehicle_id = null;
            //this.$refs.edit_vehicle.fetchVehicle(id);
            var new_vehicle_another={
                access_type: null,
                capacity:'',
                rego:'',
                rego_expiry:null,
                license:'',
                proposal: vm.proposal.id
            }
            //this.$refs.edit_vehicle.vehicle=this.new_vehicle;
            this.$refs.edit_vehicle.vehicle=new_vehicle_another;
            this.$refs.edit_vehicle.vehicle_action='add'
            this.$refs.edit_vehicle.isModalOpen = true;
        },
        editVehicle: function(id){
            this.$refs.edit_vehicle.vehicle_id = id;
            this.$refs.edit_vehicle.fetchVehicle(id);
            this.$refs.edit_vehicle.isModalOpen = true;
        },
        discardVehicle:function (vehicle_id) {
            let vm = this;
            swal({
                title: "Discard Vehicle",
                text: "Are you sure you want to discard this vehicle?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Discard Vehicle',
                confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.delete(api_endpoints.discard_vehicle(vehicle_id))
                .then((response) => {
                    swal(
                        'Discarded',
                        'Your vehicle has been discarded',
                        'success'
                    )
                    vm.$refs.vehicle_datatable.vmDataTable.ajax.reload();
                }, (error) => {
                    console.log(error);
                });
            },(error) => {

            });
        },
        addEventListeners: function(){
            let vm = this;
            vm.$refs.vehicle_datatable.vmDataTable.on('click', 'a[data-edit-vehicle]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-edit-vehicle');
                vm.editVehicle(id);
            });
            // External Discard listener
            vm.$refs.vehicle_datatable.vmDataTable.on('click', 'a[data-discard-vehicle]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-discard-vehicle');
                vm.discardVehicle(id);
            });
        },
        refreshFromResponse: function(){
            this.$refs.vehicle_datatable.vmDataTable.ajax.reload();
        },
        initialiseSearch:function(){
            
        }, 
    },
    mounted: function(){
        let vm = this;
        vm.fetchFilterLists();
        this.$nextTick(() => {
            vm.addEventListeners();
            vm.initialiseSearch();
        });
        if(vm.is_external){
            var column = vm.$refs.vehicle_datatable.vmDataTable.columns(8); //Hide 'Assigned To column for external'
            column.visible(false);
        }
        
    }
}
</script>
<style scoped>
</style>
