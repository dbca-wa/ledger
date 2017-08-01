<template id="comms_logs">
    <div class="row">
        <div class="panel panel-default">
            <div class="panel-heading">
                Logs
            </div>
            <div class="panel-body panel-collapse">
                <div class="row">
                    <div class="col-sm-12">
                        <strong>Communications</strong><br/>
                        <div class="row">
                            <div class="col-sm-5">
                                <a ref="showCommsBtn" class="actionBtn">Show</a>
                            </div>
                            <div class="col-sm-1">
                                <span>|</span>
                            </div> 
                            <div class="col-sm-5">
                                <a ref="addCommsBtn" class="actionBtn pull-right">Add Entry</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-sm-12 top-buffer-s">
                        <strong>Actions</strong><br/>
                        <a tabindex="2" ref="showActionBtn" class="actionBtn">Show</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
require("select2/dist/css/select2.min.css");
require("select2-bootstrap-theme/dist/select2-bootstrap.min.css");
import {
    api_endpoints,
    helpers
}from '@/utils/hooks'
export default {
    name: 'CommsLogSection',
    props: {
        comms_url:{
            type: String,
            required: true
        },
        logs_url:{
            type: String,
            required: true
        },
        comms_add_url:{
            type: String,
            required: true
        }
    },
    data() {
        let vm = this;
        return {
            dateFormat: 'DD/MM/YYYY',
            actionsTable: null,
            popoversInitialised: false,
            actionsDtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[2, 'desc']],
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing:true,
                ajax: {
                    "url": vm.logs_url, 
                    "dataSrc": '',
                },
                order: [],
                columns:[
                    {
                        data:"who",
                        orderable: false
                    },
                    {
                        data:"what",
                        orderable: false
                    },
                    {
                        data:"when",
                        orderable: false,
                        mRender:function(data,type,full){
                            return moment(data).format(vm.dateFormat)
                        }
                    },
                ]
            },
            commsDtOptions:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                deferRender: true, 
                autowidth: true,
                order: [[0, 'desc']],
                processing:true,
                ajax: {
                    "url": vm.comms_url, 
                    "dataSrc": '',
                },
                columns:[
                    {
                        title: 'Date',
                        data: 'created',
                        render: function (date) {
                            return moment(date).format(vm.DATE_TIME_FORMAT);
                        }
                    },
                    {
                        title: 'Type',
                        data: 'type'
                    },
                    {
                        title: 'Reference',
                        data: 'reference'
                    },
                    {
                        title: 'To',
                        data: 'to',
                        render: vm.commaToNewline
                    },
                    {
                        title: 'CC',
                        data: 'cc',
                        render: vm.commaToNewline
                    },
                    {
                        title: 'From',
                        data: 'fromm',
                        render: vm.commaToNewline
                    },
                    {
                        title: 'Subject/Desc.',
                        data: 'subject'
                    },
                    {
                        title: 'Text',
                        data: 'text',
                        'render': function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 100,
                                    omission: ellipsis,
                                    separator: ' '
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template('<a href="#" ' +
                                    'role="button" ' +
                                    'data-toggle="popover" ' +
                                    'data-trigger="click" ' +
                                    'data-placement="top auto"' +
                                    'data-html="true" ' +
                                    'data-content="<%= text %>" ' +
                                    '>more</a>');
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value
                                });
                            }

                            return result;
                        },
                        'createdCell': function (cell) {
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            $(cell).popover();
                        }
                    },
                    {
                        title: 'Documents',
                        data: 'documents',
                        'render': function (values) {
                            var result = '';
                            _.forEach(values, function (value) {
                                // We expect an array [docName, url]
                                // if it's a string it is the url
                                var docName = '',
                                    url = '';
                                if (_.isArray(value) && value.length > 1){
                                    docName = value[0];
                                    url = value[1];
                                }
                                if (typeof s === 'string'){
                                    url = value;
                                    // display the first  chars of the filename
                                    docName = _.last(value.split('/'));
                                    docName = _.truncate(docName, {
                                        length: 18,
                                        omission: '...',
                                        separator: ' '
                                    });
                                }
                                result += '<a href="' + url + '" target="_blank"><p>' + docName+ '</p></a><br>';
                            });
                            return result;
                        }
                    }
                ]
            },
            commsTable : null,
            
        }
    },
    components:{
    },
    watch:{
    },
    computed: {
    },
    methods:{
        initialisePopovers: function(){
            if (!this.popoversInitialised){
                helpers.initialiseActionLogs(this._uid,this.$refs.showActionBtn,this.actionsDtOptions,this.actionsTable);
                helpers.initialiseCommLogs('-internal-proposal-'+this._uid,this.$refs.showCommsBtn,this.commsDtOptions,this.commsTable);
                this.popoversInitialised = true;
            }
        },
    },
    mounted: function(){
        let vm = this;
        this.$nextTick(() => {
            vm.initialisePopovers();
        });
    }
}
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
</style>
