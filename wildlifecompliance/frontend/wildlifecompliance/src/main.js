// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import resource from 'vue-resource'
import App from './App'
import router from './router'
import bs from 'bootstrap'
import helpers from '@/utils/helpers'
import hooks from './packages'
import api_endpoints from './api'
require( '../node_modules/bootstrap/dist/css/bootstrap.css' );
//require('../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css')
require( '../node_modules/font-awesome/css/font-awesome.min.css' )

Vue.config.devtools = true;
Vue.config.productionTip = false
Vue.use( resource );

Vue.mixin({
  data: function() {
    return {
      globalVar:'global',
    }
  }
});

// Add CSRF Token to every request
Vue.http.interceptors.push( function ( request, next ) {
  // modify headers
  if ( request.url != api_endpoints.countries ) {
    request.headers.set( 'X-CSRFToken', helpers.getCookie( 'csrftoken' ) );
  }

  // continue to next interceptor
  next();
} );

Vue.filter('toCurrency', function(value) {
                if (typeof value !== "number") {
                    return value;
                }
                var formatter = new Intl.NumberFormat('en-AU', {
                    style: 'currency',
                    currency: 'AUD',
                    minimumFractionDigits: 2
                });
                return formatter.format(value);
            });

/* eslint-disable no-new */
Vue.prototype.current_tab = '';
window.vue = new Vue( {
    el: '#app',
    router,
    template: '<App/>',
    data: function() {
      return {
        currentTab: null,
        tabID: null,
      }
    },
    components: {
        App
    },
    computed: {
        wc_version: function (){
            return wc_version;
        }
    },
    created:function() {
        this.globalVar = "It's will change global var";
    },
    methods:{
        setSelectedTabId: function(target) {
            let vm = this;
            /*
            var tab_id = target.href.split('#')[1];
            vm.tabID = target.href.split('#')[1];
            this.$children[0].$children[0].$children[0].$children[0].$children[0].selected_activity_type_tab_id = parseInt(tab_id);
            return parseInt(tab_id);
            */
            //vm.tabID = parseInt(target.href.split('#')[1]);
            //this.current_tab = $("ul#tabs-section li.active")[0].textContent;
            this.$children[0].$children[0].$children[0].$children[0].$children[0].selected_activity_type_tab_id = vm.tabID;
            return vm.tabID;
        },
        /*
        getSelectedTabName: function() {
            return $("ul#tabs-section li.active")[0].textContent;
        },
        */
    },
    /*
    watch: {
        // whenever current_tab changes, this function will run
        tabID: function () {
            let vm = this;
            // The on tab shown event
            $('.nav-tabs a').on('shown.bs.tab', function (e) {
                vm.currentTab = $("ul#tabs-section li.active")[0].textContent;
                console.log('Tab has changed: ' + vm.currentTab + ' - ' + vm.tabID);
            });
        }    
    },
    */

})

Vue.config.devtools = true
