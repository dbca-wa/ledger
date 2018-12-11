<template lang="html">

  
        <span v-if="help_text">
            <template v-if="!isForAssessor">
                <template v-if="!showingHelpText">
                    <a href="" @click.prevent="toggleHelpText"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a>
                </template>
                    <a v-else href="" @click.prevent="toggleHelpText"><i class="fa fa-question-circle" style="color:blue">&nbsp;</i></a>
            </template>

            <template v-else>
            <template v-if="assessorMode">
                <template v-if="!showingHelpText">
                    <a href="" @click.prevent="toggleHelpText"><i class="fa fa-question-circle" style="color:green">&nbsp;</i></a>
                </template>
                    <a v-else href="" @click.prevent="toggleHelpText"><i class="fa fa-question-circle" style="color:green">&nbsp;</i></a>
            </template>
            </template>
            <HelpTextDisplay v-show="showingHelpText" :help_text="help_text" />
        </span>
     
</template>

 



<script>
import HelpTextDisplay from './help_text_display.vue'
export default {
    props:["help_text","assessorMode","isForAssessor"],

components: { HelpTextDisplay },
data: function() {
  return{
    showingHelpText: false,
    pBody: 'pBody'
    }
  },

 methods:{
         toggleHelpText(){
            this.showingHelpText = ! this.showingHelpText;
        },
   }
}
</script>

<style lang="css">
</style>


