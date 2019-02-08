
<script>
    export default {
        props:["data_children","renderer","name","data","readonly"],
        mounted(){

        },
        render(h) {
            let vm =this;
            try {
                //var conditions = vm.conditions;
                var value = null;
                //var data_children = JSON.parse( vm.data_children );
                var data_children = vm.data_children;
                if (data_children) {
                    var values = Object.keys(data_children);
                    if (!values) {
                        return (
                            <div> no data_children </div>
                        )
                    }else{
                        /*
                        return (
                            <div>
                                {values.map(val =>{
                                    {return conditions[val].map(c=>{
                                        {return (<div id={'cons_'+vm.name+'_'+val} class="hidden">
                                            {vm.renderer.renderChildren(h,c,vm.data,vm.readonly)}
                                        </div>)}
                                    })}
                                })}
                            </div>
                        )
                        */

                        return (
                            <div>
                                {data_children[0].children.map(c=>{
                                    return (
                                        <div>
                                            {vm.renderer.renderChildren(h,c,value)}
                                        </div>
                                    )
                                })}
                            </div>
                        )

                    }
                }
            } catch (e) {
                console.log(e);
            }
        }

    }
</script>
