// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import './foundation-min.scss';
import 'foundation-datepicker/css/foundation-datepicker.css';

import Vue from 'vue';
import availability from './availability';

require('custom-event-polyfill');


var availabilityApp = function (target, parkstayUrl, siteId, useAdminApi) {

    Vue.config.productionTip = (process.env.NODE_ENV === 'production');

    if (!parkstayUrl) {
        parkstayUrl = process.env.PARKSTAY_URL || '';
    }
    siteId = siteId || 0;
    useAdminApi = useAdminApi || false;

    var options = {
        props: {parkstayUrl, siteId, useAdminApi}
    };

    /* eslint-disable no-new */
    return new Vue({
        render: function (h) {
            return h(availability, options);
        }
    }).$mount(target);
};

export default availabilityApp
