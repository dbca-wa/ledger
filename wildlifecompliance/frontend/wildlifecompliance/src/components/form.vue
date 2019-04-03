<template lang="html">
    <div>
        <RendererForm
            :withSectionsSelector="withSectionsSelector"
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
    import { splitText } from "@/utils/helpers.js";
    import { mapGetters } from 'vuex'
    import '@/scss/forms/form.scss';
    import AmendmentRequestDetails from '@/components/forms/amendment_request_details.vue';
    import RendererForm from '@/components/common/renderer.vue';
    require('../../node_modules/bootstrap/dist/css/bootstrap.css');
    require('../../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css');
    require('../../node_modules/font-awesome/css/font-awesome.min.css');
    const easing = require('easing');
    export default {
        components: {
            RendererForm,
        },
        props:{
            withSectionsSelector:{
                type: Boolean,
                default: true
            },
            form_width: {
                type: String,
                default: 'col-md-9'
            }
        },
        data: function () {
        },
    }
</script>
