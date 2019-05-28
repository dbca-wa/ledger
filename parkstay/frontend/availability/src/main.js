// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import './foundation-min.scss';
import 'foundation-datepicker/css/foundation-datepicker.css';

import Vue from 'vue';
import availability from './availability';
Vue.config.productionTip = (process.env.NODE_ENV === 'production');

require('custom-event-polyfill');


var availabilityApp = function (target, args) {
    var options = {
        props: {
            parkstayUrl: args.parkstayUrl || '',
            siteId: args.siteId || 0,
            useAdminApi: args.useAdminApi || false,
        }
    };

    /* eslint-disable no-new */
    return new Vue({
        render: function (h) {
            return h(availability, options);
        }
    }).$mount(target);
};

export default availabilityApp
