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
    import Renderer from '@/utils/renderer'
    import bs from 'bootstrap'
    require('../../node_modules/bootstrap/dist/css/bootstrap.css');
    require('../../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css')
    require('../../node_modules/font-awesome/css/font-awesome.min.css')
    const easing = require('easing');
    export default {
        props:{
            proposal:{
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
                values:null
                //[{'RegionActivitySection': [{'Activity': 'PublicUtilities 1','Region': ['Kimberley (Region) 1'], 'Tenure':'My Tenure 1'}]}]
                //'RegionActivitySection': [{'Activity': 'PublicUtilities 1','Region': ['Kimberley (Region) 1'], 'Tenure':'My Tenure 1'}]
            }
        },
        methods:{
            mapDataToApplication:function () {
                if (this.proposal.data) {
                    this.values = this.proposal.data[0]
                }
            }
        },
        created:function () {
            this.mapDataToApplication();
        },
        mounted:function () {
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
            //Renderer.sections = [];
            Renderer.store_status_data(vm.proposal.readonly,vm.proposal.assessor_data,vm.proposal.comment_data,vm.proposal.current_assessor,vm.proposal.assessor_mode,vm.proposal.can_user_edit,vm.proposal.documents_url, vm.proposal.id, vm.proposal.application_type);
            if (vm.withSectionsSelector){
                return (
                    <div>
                        <div id="scrollspy-heading" class="col-lg-12" >
                            <h3>Application: <small>{vm.proposal.lodgement_number}</small></h3>
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
                            {vm.proposal.schema.map(d =>{
                                return Renderer.renderChildren(h,d,vm.values,vm.proposal.assessor_data,vm.proposal.readonly,vm.proposal.assessor_mode,vm.proposal.assessor)
                            })}
                            { this.$slots.default }
                        </div>
                    </div>
                )
            }
            else{
                if (vm.form_width == 'inherit'){
                    return (
                        <div>
                            {vm.proposal.schema.map(d =>{
                                return Renderer.renderChildren(h,d,vm.values,vm.proposal.assessor_data,vm.proposal.readonly,vm.proposal.assessor_mode,vm.proposal.assessor)
                            })}
                            { this.$slots.default }
                        </div>
                    )
                }
                else {
                    return (
                        <div class={vm.form_width}>
                            {vm.proposal.schema.map(d =>{
                                return Renderer.renderChildren(h,d,vm.values,vm.proposal.assessor_data,vm.proposal.readonly,vm.proposal.assessor_mode,vm.proposal.assessor)
                            })}
                            { this.$slots.default }
                        </div>
                    )
                }
            }
        }
    }
</script>
