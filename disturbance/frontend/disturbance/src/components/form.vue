<style lang="css">
    .section{
        text-transform: capitalize;
    }
    #scrollspy-section li {
        list-style-type: none;
        font-size:1.2em;
        line-height: 2;
    }

    #scrollspy-section li>a{
        text-decoration: none;
    }
    .affix-top{
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
                type: Array,
                required:true
            },
            data:{
                type: Array,
                default:function () {
                    return null;
                }
            }
        },
        data:function () {
            return{
                values:null
            }
        },
        methods:{
            mapDataToApplication:function () {

                if (this.data) {
                    let fdata = {};
                    let jans = this.data;
                    for (var a in jans) {
                        var key = Object.keys(jans[a])[0];
                        if (jans[a][key] instanceof Array) {
                            fdata[key] = jans[a][key][0];
                        }
                        else{
                            fdata[key] = jans[a][key];
                        }

                    }
                    this.values = fdata
                }
            }
        },
        created:function () {
            this.mapDataToApplication();
        },
        mounted:function () {
            Renderer.sections.map(sec => {
                $('#scrollspy-section').append(`<li><a class='page-scroll section' href='#${sec.name}'>${sec.label}</a></li>`);
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
                    $('nav.affix').addClass('affix-top');
                }else{
                    $('nav.affix').removeClass('affix-top');
                }
            });

        },
        render(h) {
            let vm =this;
            return (
                <div>
                    <div id="scrollspy-heading" class="col-lg-12" >
                        <h3 style="padding-left:40px;">Proposal: <small>158325</small></h3>
                    </div>
                    <div class="col-md-3" >
                        <nav class="hidden-print hidden-sm hidden-xs affix">
                            <ul class="" id="scrollspy-section">

                            </ul>
                        </nav>
                    </div>
                    <div class="col-md-9">
                        {vm.proposal.map(d =>{
                            return Renderer.renderChildren(h,d,vm.values)
                        })}
                        { this.$slots.default }
                    </div>
                </div>
            )
        }
    }
</script>
