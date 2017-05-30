<template lang="html">
    <Renderer :application="app" />
</template>

<script>
import Renderer from "@/Form.vue"
export default {
    components: {
        Renderer
    },
    data:function () {
        return {
            app:require('@/assets/data')
        }
    }
}
</script>

<style lang="css">
</style>
