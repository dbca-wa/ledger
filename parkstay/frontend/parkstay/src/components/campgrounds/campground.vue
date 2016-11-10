<template lang="html">

   <div class="panel-group" id="applications-accordion" role="tablist" aria-multiselectable="true">
      <div class="panel panel-default" id="applications">
        <div class="panel-heading" role="tab" id="applications-heading">
            <h4 class="panel-title">
                <a role="button" data-toggle="collapse" href="#applications-collapse"
                   aria-expanded="false" aria-controls="applications-collapse">
                    <h3>{{title}}</h3>
                </a>
            </h4>
        </div>
        <div id="applications-collapse" class="panel-collapse collapse in" role="tabpanel"
             aria-labelledby="applications-heading">
            <div class="panel-body">
               <div class="col-lg-12">
                  <div class="row">
                     <campgroundAttr @create="create" >
                        <h1 slot="cg_name">My Slot</h1>
                     </campgroundAttr>
                  </div>
                  <div class="row">
                     <div class="well">
                        <h1>Price History</h1>
                     </div>
                  </div>
                  <div class="row">
                     <div class="well">
                        <datatable :dtHeaders ="ch_headers" :dtOptions="ch_options" id="cg_table"></datatable>
                     </div>
                  </div>
               </div>
            </div>
         </div>
      </div>
      <div class="panel panel-default" id="applications">
        <div class="panel-heading" role="tab" id="applications-heading">
            <h4 class="panel-title">
                <a role="button" data-toggle="collapse" href="#campsites"
                   aria-expanded="false" aria-controls="collapseOne">
                    <h3>Campsites</h3>
                </a>
            </h4>
        </div>
        <div class="panel-collapse collapse in" role="tabpanel"
             aria-labelledby="applications-heading" id="campsites">
            <div class="panel-body">
               <div class="col-lg-12">
                  <div class="row">
                     <div class="well">
                        <datatable :dtHeaders ="cs_headers" :dtOptions="cs_options" id="cs_table"></datatable>
                     </div>
                  </div>
               </div>
            </div>
        </div>
    </div>
   </div>

</template>

<script>
import datatable from '../utils/datatable.vue'
import campgroundAttr from './campground-attr.vue'
import {
    $,
    Moment,
    api_endpoints
} from '../../hooks.js'

export default {
    name: 'campground',
    components: {
        datatable,
        campgroundAttr
    },
    data: function() {
        return {
            ch_options: {
                responsive: true,
                processing: true,
                deferRender: true,
                ajax: {
                    url: api_endpoints.status_history(this.$route.params.id),
                    dataSrc: ''
                },
                columns: [{
                    data: 'range_start',
                    mRender: function(data, type, full) {
                        return Moment(data).format('MMMM Do, YYYY');
                    }

                }, {
                    data: 'range_end',
                    mRender: function(data, type, full) {
                        if (data){
                            return Moment(data).add(1, 'day').format('MMMM Do, YYYY');
                        } else {
                            return '';
                        }
                    }

                }, {
                    data: 'status'
                }, {
                    data: 'editable',
                    mRender: function(data, type, full) {
                        if (data) {
                            var id = full.id;
                            var column = "<td ><a href='#' class='editRange' data-range=\"__ID__\" >Edit</a><br/><a href='#' class='deleteRange' data-range=\"__ID__\" >Delete</a></td>";
                            return column.replace(/__ID__/g, id);
                        } else {
                            return ""
                        }
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            },
            ch_headers: ['Closure Start', 'Reopen', 'Closure Reason', 'Action'],
            title: 'Campground',
            cs_options:{
                responsive: true,
                processing: true,
                deferRender: true,
                ajax: {
                    url: api_endpoints.campgroundCampsites(this.$route.params.id),
                    dataSrc: ''
                },
                columns: [{
                    data: 'name'
                }, {
                    data: 'type'
                }, {
                    data: 'status',
                    mRender: function(data, type, full) {
                         return data ? 'Open' : 'Closed'
                    }
                },{
                    data: 'price'
                }, {
                   "mRender": function(data, type, full) {
                        var id = full.id;
                        if (full.status){
                            var column = "<td ><a href='#' class='detailRoute' data-campsite=\"__ID__\" >Edit Campsite Details</a><br/><a href='#' class='statusCS' data-status='close' data-campsite=\"__ID__\" >(Temporarily) Close Campsite </a></td>";
                        } else {
                            var column = "<td ><a href='#' class='detailRoute' data-campsite=\"__ID__\" >Edit Campsite Details</a><br/><a href='#' class='statusCS' data-status='open' data-campsite=\"__ID__\" >Open Campsite </a></td>";
                        }

                        return column.replace(/__ID__/g, id);
                    }
                }],
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
            }
            ,
            cs_headers: ['Campsite Id', 'Type', 'Status', 'Price','Action'],
        }
    },
    methods: {
        create: function() {
            console.log('create in Campground');
            alert('Create was clicked')
        },
    }
}
</script>

<style lang="css">
.well{
   background-color: #fff;
}
.btn{
   margin-bottom: 10px;
}
</style>
