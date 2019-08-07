<template lang="html">
    <div>
      Online training: <input type="text" name="online_training"><br>
    </div>
</template>

<script>
    export default {
        props:{
            proposal:{
                type: Object,
                required:true
            }
        },
        data:function () {
            return{
                values:null
            }
        },
        methods:{
        }
    }
</script>

<style lang="css" scoped>
</style>

