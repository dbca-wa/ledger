<template id="vessel_table">
    <div class="row">
        <div class="col-sm-12"> 
            <div class="row" >
                <div class="col-md-3" v-if="!proposal.readonly">
                            <input type="button" style="margin-top:25px;" @click.prevent="newVessel" class="btn btn-primary" value="Add new vessel"/>
                </div>
            </div>

            <div class="row">
                <div class="col-lg-12" style="margin-top:25px;">
                    <datatable ref="vessel_datatable" :id="datatable_id" :dtOptions="vessel_options" :dtHeaders="vessel_headers"/>
                </div>
            </div>
        </div>
        <editVessel ref="edit_vessel" :vessel_id="vessel_id" @refreshFromResponse="refreshFromResponse"></editVessel>
    </div>
</template>
<script>
import datatable from '@/utils/vue/datatable.vue'
import editVessel from './edit_vessel.vue'
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'VesselTableDash',
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
        }
    },
    data() {
        let vm = this;
        return {
            new_vessel:{
                nominated_vessel:'',
                spv_no:'',
                hire_rego:'',
                craft_no:null,
                size:'',
                proposal: vm.proposal.id
            },
            pBody: 'pBody' + vm._uid,
            datatable_id: 'vessel-datatable-'+vm._uid,
            // Filters for Vessels
            
            vessel_headers:["Nominated Vessel", "SPV no./ reg. no.","Hire and Drvie reg.","No.of craft","Vessel Size (m)","Action"],
            vessel_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                //serverSide: true,
                //lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
                ajax: {
                    "url": vm.url,
                    "dataSrc": '',
                },
                dom: 'lBfrtip',
                buttons:[
                'excel', 'csv', ],
                columns: [
                    {
                        data: "nominated_vessel",
                        mRender:function (data,type,full) {
                            //return `C${data}`;
                            return full.nominated_vessel;
                        },
                        //name: "id, lodgement_number",
                    },
                    {
                        data: "spv_no",   
                    },
                    {
                        data: "hire_rego",   
                    },
                    {
                        data: "craft_no",
                    },
                    {
                        data: "size",
                        // mRender:function (data,type,full) {
                        //     return `A${data}`;
                        // },
                        // name: "approval__lodgement_number"
                    },
                    {
                        data: '',
                        mRender:function (data,type,full) {
                            let links = '';
                            if(!vm.proposal.readonly){
                            links +=  `<a href='#${full.id}' data-edit-vessel='${full.id}'>Edit Vessel</a><br/>`;
                            links +=  `<a href='#${full.id}' data-discard-vessel='${full.id}'>Discard</a><br/>`;
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
                ],
                processing: true,
                
            }
        }
    },
    components:{
        datatable,
        editVessel
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
        },
        newVessel: function(){
            let vm=this;
            this.$refs.edit_vessel.vessel_id = null;
            //this.$refs.edit_vessel.fetchVessel(id);
            //this.$refs.edit_vessel.vessel=this.new_vessel;
            var new_vessel_another={
                nominated_vessel:'',
                spv_no:'',
                hire_rego:'',
                craft_no:null,
                size:'',
                proposal: vm.proposal.id
            }
            this.$refs.edit_vessel.vessel=new_vessel_another;
            this.$refs.edit_vessel.vessel_action='add'
            this.$refs.edit_vessel.isModalOpen = true;
        },
        editVessel: function(id){
            this.$refs.edit_vessel.vessel_id = id;
            this.$refs.edit_vessel.fetchVessel(id);
            this.$refs.edit_vessel.isModalOpen = true;
        },
        discardVessel:function (vessel_id) {
            let vm = this;
            swal({
                title: "Discard Vessel",
                text: "Are you sure you want to discard this vessel?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Discard Vessel',
                confirmButtonColor:'#d9534f'
            }).then(() => {
                vm.$http.delete(api_endpoints.discard_vessel(vessel_id))
                .then((response) => {
                    swal(
                        'Discarded',
                        'Your vessel has been discarded',
                        'success'
                    )
                    vm.$refs.vessel_datatable.vmDataTable.ajax.reload();
                }, (error) => {
                    console.log(error);
                });
            },(error) => {

            });
        },
        addEventListeners: function(){
            let vm = this;
            vm.$refs.vessel_datatable.vmDataTable.on('click', 'a[data-edit-vessel]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-edit-vessel');
                vm.editVessel(id);
            });
            // External Discard listener
            vm.$refs.vessel_datatable.vmDataTable.on('click', 'a[data-discard-vessel]', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-discard-vessel');
                vm.discardVessel(id);
            });
        },
        refreshFromResponse: function(){
            this.$refs.vessel_datatable.vmDataTable.ajax.reload();
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
            var column = vm.$refs.vessel_datatable.vmDataTable.columns(8); //Hide 'Assigned To column for external'
            column.visible(false);
        }
        
    }
}
</script>
<style scoped>
</style>
