<script>
    import Renderer from '@/utils/renderer'
    import bs from 'bootstrap'
    require('../../node_modules/bootstrap/dist/css/bootstrap.css');
    require('../../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css')
    require('../../node_modules/font-awesome/css/font-awesome.min.css')
    export default {
        props:{
            application:{
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
                        fdata[key] = jans[a][key][0];
                    }
                    this.values = fdata
                }
            }
        },
        mounted:function () {
            this.mapDataToApplication();
        },
        render(h) {
            let vm =this;
            return (
                <div>
                    {vm.application.map(d =>{
                        return Renderer.renderChildren(h,d,vm.values)
                    })}
                </div>
            )
        }
    }
</script>
