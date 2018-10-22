<template lang="html">
    <div>
      First name: <input type="text" name="first_name"><br>
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

