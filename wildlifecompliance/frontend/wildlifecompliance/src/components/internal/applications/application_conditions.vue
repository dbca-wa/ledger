<template id="application_conditions">

                    <div class="col-md-12">
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Inspection Report
                                    <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>
                            </div>
                            <div class="panel-body panel-collapse collapse in" :id="panelBody">
                                <form class="form-horizontal" action="index.html" method="post">
                                    <div class="col-sm-12">
                                        <div class="form-group">
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left">Inspection Date</label>
                                                </div>
                                                <div class="col-sm-9">
                                                    <div class="input-group date" style="width: 70%;">
                                                       <input class="pull-left" placeholder="DD/MM/YYYY"/> 
                                                       <span class="input-group-addon">
                                                            <span class="glyphicon glyphicon-calendar"></span>
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-sm-3">
                                                    <label class="control-label pull-left">Inspection Report</label>
                                                </div>
                                                <div class="col-sm-9">
                                                       <a href="">Attach File</a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                </form>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h3 class="panel-title">Proposed Conditions
                                    <a class="panelClicker" :href="'#'+panelBody" data-toggle="collapse"  data-parent="#userInfo" expanded="false" :aria-controls="panelBody">
                                        <span class="glyphicon glyphicon-chevron-down pull-right "></span>
                                    </a>
                                </h3>
                            </div>
                            <div class="panel-body panel-collapse collapse in" :id="panelBody">
                                <form class="form-horizontal" action="index.html" method="post">
                                    <div class="col-sm-12">
                                        <button @click.prevent="addCondition()" style="margin-bottom:10px;" class="btn btn-primary pull-right">Add Condition</button>
                                    </div>
                                    <datatable ref="conditions_datatable" :id="'conditions-datatable-'+_uid" :dtOptions="condition_options" :dtHeaders="condition_headers"/>
                                </form>
                            </div>
                        </div>
                    </div>
                    <ConditionDetail ref="condition_detail" :application_id="application.id" :conditions="conditions" :licence_activity_tab="licence_activity_tab"/>
                </div>

            
</template>
<script>
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks'
import datatable from '@vue-utils/datatable.vue'
import ConditionDetail from './application_add_condition.vue'
export default {
    name: 'InternalApplicationConditions',
    props: {
        application: Object,
        licence_activity_tab:Number
    },
    data: function() {
        let vm = this;
        return {
            panelBody: "application-conditions-"+vm._uid,
            conditions: [],
            condition_headers:["Condition","Due Date","Recurrence","Action","Order"],
            condition_options:{
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": helpers.add_endpoint_join(api_endpoints.applications,vm.application.id+'/conditions/?licence_activity='+vm.licence_activity_tab),
                    "dataSrc": ''
                },
                order: [],
                columns: [
                    {
                        data: "condition",
                        orderable: false
                    },
                    {
                        data: "due_date",
                        mRender:function (data,type,full) {
                            return data != '' && data != null ? moment(data).format('DD/MM/YYYY'): '';
                        },
                        orderable: false
                    },
                    {
                        data: "recurrence",
                        mRender:function (data,type,full) {
                            if (full.recurrence){
                                switch(full.recurrence_pattern){
                                    case 1:
                                        return `Once per ${full.recurrence_schedule} week(s)`;
                                    case 2:
                                        return `Once per ${full.recurrence_schedule} month(s)`;
                                    case 3:
                                        return `Once per ${full.recurrence_schedule} year(s)`;
                                    default:
                                        return '';
                                }
                            }
                            return '';
                        },
                        orderable: false
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = `<a href='#' class="editCondition" data-id="${full.id}">Edit</a><br/>`;
                            links +=  `<a href='#' class="deleteCondition" data-id="${full.id}">Delete</a><br/>`;
                            return links;
                        },
                        orderable: false
                    },
                    {
                        mRender:function (data,type,full) {
                            let links = '';
                            // TODO check permission to change the order
                            links +=  `<a class="dtMoveUp" data-id="${full.id}" href='#'><i class="fa fa-angle-up"></i></a><br/>`;
                            links +=  `<a class="dtMoveDown" data-id="${full.id}" href='#'><i class="fa fa-angle-down"></i></a><br/>`;
                            return links;
                        },
                        orderable: false
                    }
                ],
                processing: true,
                drawCallback: function (settings) {
                    $(vm.$refs.conditions_datatable.table).find('tr:last .dtMoveDown').remove();
                    $(vm.$refs.conditions_datatable.table).children('tbody').find('tr:first .dtMoveUp').remove();
                    // Remove previous binding before adding it
                    $('.dtMoveUp').unbind('click');
                    $('.dtMoveDown').unbind('click');
                    // Bind clicks to functions
                    $('.dtMoveUp').click(vm.moveUp);
                    $('.dtMoveDown').click(vm.moveDown);
                }
            }
        }
    },
    watch:{
    },
    components:{
        datatable,
        ConditionDetail
    },
    computed:{
    },
    methods:{
        addCondition(){
            this.$refs.condition_detail.licence_activity=this.licence_activity_tab;
            this.$refs.condition_detail.isModalOpen = true;
        },
        removeCondition(_id){
            let vm = this;
            swal({
                title: "Remove Condition",
                text: "Are you sure you want to remove this condition?",
                type: "warning",
                showCancelButton: true,
                confirmButtonText: 'Remove Condition',
                confirmButtonColor:'#d9534f'
            }).then((result) => {
                if (result.value) {
                    vm.$http.delete(helpers.add_endpoint_json(api_endpoints.application_conditions,_id))
                    .then((response) => {
                        vm.$refs.conditions_datatable.vmDataTable.ajax.reload();
                    }, (error) => {
                        console.log(error);
                    });
                }
            },(error) => {
            });
        },
        fetchConditions(){
            let vm = this;
            
            vm.$http.get(api_endpoints.application_standard_conditions).then((response) => {
                vm.conditions = response.body
            },(error) => {
                console.log(error);
            })
        },
        editCondition(_id){
            let vm = this;
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.application_conditions,_id)).then((response) => {
                this.$refs.condition_detail.condition = response.body;
                this.$refs.condition_detail.condition.due_date =  response.body.due_date != null && response.body.due_date != undefined ? moment(response.body.due_date).format('DD/MM/YYYY'): '';
                response.body.standard ? $(this.$refs.condition_detail.$refs.standard_req).val(response.body.standard_condition).trigger('change'): '';
                this.addCondition();
            },(error) => {
                console.log(error);
            })
        },
        updatedConditions(){
            this.$refs.conditions_datatable.vmDataTable.ajax.reload();
        },
        eventListeners(){
            let vm = this;
            vm.$refs.conditions_datatable.vmDataTable.on('click', '.deleteCondition', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-id');
                vm.removeCondition(id);
            });
            vm.$refs.conditions_datatable.vmDataTable.on('click', '.editCondition', function(e) {
                e.preventDefault();
                var id = $(this).attr('data-id');
                vm.editCondition(id);
            });
        },
        sendDirection(req,direction){
            let movement = direction == 'down'? 'move_down': 'move_up';
            this.$http.get(helpers.add_endpoint_json(api_endpoints.application_conditions,req+'/'+movement)).then((response) => {
            },(error) => {
                console.log(error);
                
            })
        },
        moveUp(e) {
            // Move the row up
            let vm = this;
            e.preventDefault();
            var tr = $(e.target).parents('tr');
            vm.moveRow(tr, 'up');
            vm.sendDirection($(e.target).parent().data('id'),'up');
        },
        moveDown(e) {
            // Move the row down
            e.preventDefault();
            let vm = this;
            var tr = $(e.target).parents('tr');
            vm.moveRow(tr, 'down');
            vm.sendDirection($(e.target).parent().data('id'),'down');
        },
        moveRow(row, direction) {
            // Move up or down (depending...)
            var table = this.$refs.conditions_datatable.vmDataTable;
            var index = table.row(row).index();
            var order = -1;
            if (direction === 'down') {
              order = 1;
            }
            var data1 = table.row(index).data();
            data1.order += order;
            var data2 = table.row(index + order).data();
            data2.order += -order;
            table.row(index).data(data2);
            table.row(index + order).data(data1);
            table.page(0).draw(false);
        }
    },
    mounted: function(){
        let vm = this;
        this.fetchConditions();
        vm.$nextTick(() => {
            this.eventListeners();
        });
    }
}
</script>
<style scoped>
</style>