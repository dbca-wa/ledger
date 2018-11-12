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
            // Initialise by setting all first tabs.
            $('#tabs-section li:first-child a').click();
            $('#tabs-main li:first-child a').click();

            if (this.withSectionsSelector){
                var _tabid = 0;
                var _settab = '';
                var _mnu1 = '';
                var _mnu2 = '';
                Renderer.sections.map((sec,i) => {

                   if (sec.name.indexOf('Section1')>-1) {
                      if (sec.name.indexOf('Section1_0')===-1) {
                        _mnu1 = _mnu1 + _mnu2 + '</ul></li>';
                        _mnu2 = '';
                      }
                      _mnu1 = _mnu1 + `<li class='dropdown-submenu'><a class='section-menu' href='#section-submenu' data-toggle='collapse' aria-expanded='false'>` + tabs[parseInt(sec.name.split('_')[1])].name + `<span class='caret'></span></a><ul class='dropdown-menu' id='section-submenu' >` +_mnu2;
                   };
                   _mnu2 = _mnu2 + `<li><a class='page-scroll section' href='#${sec.name}'>${sec.label}</a></li>`;
                });
                _mnu1 = _mnu1 + _mnu2 + '</ul></li>';
                $('#scrollspy-section').append(_mnu1);

                $('a.page-scroll').bind('click', function(event) {
                   var $anchor = $(this);
                   _tabid = parseInt(($anchor.attr('href')).split('_')[1]);
                   _settab = '#tabs-section li:nth-child(' + ++_tabid + ') a';
                   $(_settab).click();
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
            Renderer.tabs_list = [];
            Renderer.store_status_data(vm.application.readonly,vm.application.assessor_data,vm.application.comment_data,vm.application.current_assessor,vm.application.assessor_mode,vm.application.can_user_edit,vm.application.documents_url,vm.application.id);
            if (vm.withSectionsSelector){
                return (
                    <div>
                        <div id="scrollspy-heading" class="col-lg-12" >
                            <h3>Application {vm.application.id}: {vm.application.licence_type_short_name}</h3>
                        </div>
                        <div class="col-md-3" >
                          <div class="panel panel-default fixed">
                            <div class="panel-heading">
                               <div class="dropdown">
                                  <ul class="list-unstyled">
                                    <li ><a href="#" class="dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true"><h5>Sections<span class="caret"></span></h5></a>
                                      <ul class="dropdown-menu" id="scrollspy-section" >
                                      </ul>
                                    </li>
                                  </ul>
                                </div>
                            </div>
                            <div class="panel-body" style="padding:0">
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
    $(document).ready(function(){
      $('.dropdown-submenu a.section-menu').on("click", function(e){
        $(this).next('ul').toggle();
        e.stopPropagation();
        e.preventDefault();
      });
    });
</script>
