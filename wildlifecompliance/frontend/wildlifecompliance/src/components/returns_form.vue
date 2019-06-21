<template lang="html">
    <div>
        <ReturnsRendererForm
            :form_width="form_width"
        />
        <slot></slot>
    </div>
</template>

<script>
    import Vue from 'vue'
    import {
  api_endpoints,
  helpers
}
from '@/utils/hooks'
    import bs from 'bootstrap'
    import '@/scss/forms/form.scss';
    import ReturnsRendererForm from '@/components/common/returns_renderer.vue';
    require('../../node_modules/bootstrap/dist/css/bootstrap.css');
    require('../../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css');
    require('../../node_modules/font-awesome/css/font-awesome.min.css');
    export default {
        components: {
            ReturnsRendererForm,
        },
        props:{
            form_width: {
                type: String,
                default: 'col-md-8'
            }
        },
    }
</script>
