<style lang="css" scoped>
    .section{
        text-transform: capitalize;
    }
    .list-group{
        margin-bottom: 0;
    }
    .fixed-top{
        position: fixed;
        top:56px;
    }
</style>

<script>
    import Vue from 'vue'
    import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
    import Renderer from '@/utils/renderer'
    import bs from 'bootstrap'
    require('../../node_modules/bootstrap/dist/css/bootstrap.css');
    require('../../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css')
    require('../../node_modules/font-awesome/css/font-awesome.min.css')
    const easing = require('easing');
    export default {
        props:{
            application:{
                type: Object,
                required:true
            },
            withSectionsSelector:{
                type: Boolean,
                default: true
            },
            form_width: {
                type: String,
                default: 'col-md-9'
            }
        },
        data:function () {
            return{
                values:null,
                amendment_request_id:[]
            }
        },
        methods:{
            mapDataToApplication:function () {
                if (this.application.data) {
                    this.values = this.application.data[0]
                }

            },

        },
        created:function () {
           
            this.mapDataToApplication();
        },
        mounted:function () {

            this.amendment_request_id=this.application.amendment_requests
            
            var tabs=Renderer.tabs_list
            // tabs.map(tsec => {
            //         $('#tabs-section').append(`<li><a data-toggle="tab" href='#${tsec.id}'>${tsec.label}</a></li>`);
            //     });
            // console.log(tabs)
            if(this.application.has_amendment){
                console.log("from inside if")

                tabs.map(tsec => {
                    if(this.amendment_request_id.indexOf(tsec.id) < 0){
                        // $('#tabs-section').append(`<li><a class="nav-link disabled" data-toggle="tab" href='#'>${tsec.label}</a></li>`);
                    }
                    else{
                        $('#tabs-section').append(`<li><a class="nav-link" data-toggle="tab" href='#${tsec.id}'>${tsec.label}</a></li>`);
                    }
                    
                });

            }
            else{
                tabs.map(tsec => {
                    $('#tabs-section').append(`<li><a onclick="vue.setSelectedTabId(this)" data-toggle="tab" href='#${tsec.id}'>${tsec.label}</a></li>`);
                });

            }
            
            if (this.withSectionsSelector){
                
                Renderer.sections.map(sec => {
                    $('#scrollspy-section').append(`<li class="list-group-item" ><a class='page-scroll section' href='#${sec.name}'>${sec.label}</a></li>`);
                });

                $('a.page-scroll').bind('click', function(event) {
                   var $anchor = $(this);
                   $('html, body').stop().animate({
                       scrollTop: ($($anchor.attr('href')).offset().top)
                   }, 1000, 'easeInOutExpo');
                   event.preventDefault();
               });
               $(window).scroll(function () {
                    var wScroll = $(this).scrollTop();
                    if (wScroll >= $('#scrollspy-heading').offset().top-56) {
                        var width = $('.fixed').width();
                        $('.fixed').addClass('fixed-top');
                        $('.fixed-top').width(width);
                    }else{
                        $('.fixed').removeClass('fixed-top');
                        $('.fixed').width('100%');
                    }
                });

            }

                
        },
        render(h) {
            let vm =this;
            Renderer.store_status_data(vm.application.readonly,vm.application.assessor_data,vm.application.comment_data,vm.application.current_assessor,vm.application.assessor_mode,vm.application.can_user_edit,vm.application.documents_url);
            if (vm.withSectionsSelector){
                return (
                    <div>
                        <div id="scrollspy-heading" class="col-lg-12" >
                            <h3>Application {vm.application.id}: {vm.application.licence_type_short_name}</h3>
                        </div>
                        <div class="col-md-3" >
                            <div class="panel panel-default fixed">
                              <div class="panel-heading">
                                <h5>Sections</h5>
                              </div>
                              <div class="panel-body" style="padding:0">
                                  <ul class="list-group" id="scrollspy-section" style="margin-bottom:0">

                                  </ul>
                              </div>
                            </div>
                        </div>
                        <div class="col-md-9">
                            <ul class="nav nav-tabs" id="tabs-section">

                            </ul>
                            <div class="tab-content">
                                {vm.application.schema.map(d =>{
                                    return Renderer.renderChildren(h,d,vm.values,vm.application.assessor_data,vm.application.readonly,vm.application.assessor_mode,vm.application.assessor)
                                })}
                                { this.$slots.default }
                            </div>
                        </div>
                    </div>
                )
            }
            else{
                if (vm.form_width == 'inherit'){
                    return (
                        <div>
                            <ul class="nav nav-tabs" id="tabs-section">

                            </ul>
                            <div class="tab-content">
                                {vm.application.schema.map(d =>{
                                    return Renderer.renderChildren(h,d,vm.values,vm.application.assessor_data,vm.application.readonly,vm.application.assessor_mode,vm.application.assessor)
                                })}
                                { this.$slots.default }
                            </div>
                        
                        </div>
                    )
                }
                else {
                    return (
                        <div class={vm.form_width}>
                            <ul class="nav nav-tabs">
                              <li class="nav-item">
                                <a class="nav-link active" href="#">Active</a>
                              </li>
                            </ul>
                                {vm.application.schema.map(d =>{
                                    return Renderer.renderChildren(h,d,vm.values,vm.application.assessor_data,vm.application.readonly,vm.application.assessor_mode,vm.application.assessor)
                                })}
                                { this.$slots.default }
                        </div>
                    )
                }

            }
        }
    }
</script>
