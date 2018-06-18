<template lang="html">
	<!-- <div>
		<ul>
			<div class="nav nav-tabs" >
	            <li><a data-toggle="tab" :href="'#'+tab_id">{{label}}</a></li>
		    </div>
		</ul> -->
	    
            <div class="tab-pane fade" :id="id">
                
	    	      <slot></slot>
            </div>
	    	
	    
	<!-- </div> -->
</template>
<script>
export default {
    name:"tab",
    props:["label","id"],
    data:function () {
        return {
            title:"Tab title",
            eventInitialised: false
        }
    },
    computed:{
        tab_id:function () {
            return "tab_"+this.Key
        }
    },
    updated:function () {
        // let vm = this;
        // vm.$nextTick(()=>{
        //     if (!vm.eventInitialised){
        //         $('.panelClicker[data-toggle="collapse"]').on('click',function () {
        //             var chev = $(this).children()[0];
        //             window.setTimeout(function () {
        //                 $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
        //             },100);
        //         });
        //         this.eventInitialised = true;
        //     }
        // });
    }
}
</script>