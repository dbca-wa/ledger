// The following line loads the standalone build of Vue instead of the runtime-only build,
// so you don't have to do: import Vue from 'vue/dist/vue'
// This is done with the browser options. For the config, see package.json
import Vue from 'vue'
if (process.env.NODE_ENV == "development") {
    Vue.config.devtools = true;
}
import resource from 'vue-resource'
import Campgrounds from '../components/campgrounds/campgrounds.vue'
import Campground from '../components/campgrounds/campground.vue'
import AddCampground from '../components/campgrounds/addCampground.vue'
import Campsite from '../components/campsites/campsite.vue'
import firstLevelSearch from '../components/booking/first-level-search.vue'
import bookingDashboard from '../components/booking/dashboard.vue'
import addBooking from '../components/booking/addbooking.vue'
import bookingCloseClasses from '../components/booking/booking-close-classes.vue'
import BookingIndex from '../components/booking/index.vue'
import editBooking from '../components/booking/changebooking2.vue'
import page_404 from '../components/utils/404.vue'
import Reports from '../components/reports/reports.vue'
import Router from 'vue-router'
import Campsite_type_dash from '../components/campsites-types/campsite-types-dash.vue'
import Campsite_type from '../components/campsites-types/campsite-type.vue'
import Bulkpricing from '../components/bulkpricing/bulkpricing.vue'
import Profile from '../components/user/profile.vue'
import alert from '../components/utils/alert.vue'
import store from './store'
import { mapGetters } from 'vuex'
import $ from '../hooks'
var css = require('../hooks-css.js');
Vue.use(Router);
Vue.use(resource);

global.$ = $

const routes = [
    {
        path: '/',
        component: {
            render (c) { return c('router-view') }
        },
        children: [
            {
                path: "account",
                name: "profile",
                component: Profile
            },
            {
                path:'dashboard',
                component: {
                    render (c) { return c('router-view') }
                },
                children: [
                    {
                        path:'campsite-types',
                        name:'campsite-types',
                        component: Campsite_type_dash
                    },
                    {
                        path:'campsite-type',
                        component: {
                            render (c) { return c('router-view') }
                        },
                        children: [
                            {
                                path: '/',
                                name: 'campsite-type',
                                component: Campsite_type_dash
                            },
                            {
                                path:':campsite_type_id',
                                name:'campsite-type-detail',
                                component: Campsite_type,
                            }
                        ]
                    },
                    {
                        path:'campgrounds/addCampground',
                        name:'cg_add',
                        component: AddCampground
                    },
                    {
                        path:'campgrounds',
                        component: {
                            render (c) { return c('router-view') }
                        },
                        children:[
                            {
                                path: '/',
                                name: 'cg_main',
                                component: Campgrounds,
                            },
                            {
                                path:':id',
                                name:'cg_detail',
                                component: Campground,
                            },
                            {
                                path:':id/campsites/add',
                                name:'add_campsite',
                                component:Campsite
                            },
                            {
                                path:':id/campsites/:campsite_id',
                                name:'view_campsite',
                                component:Campsite
                            },
                        ]
                    },{
                        path:'bookings',
                        component: BookingIndex,
                        children:[
                            {
                                path: '/',
                                name: 'booking-dashboard',
                                component: bookingDashboard,
                            },
                            {
                                path: 'add/:cg',
                                name: 'add-booking',
                                component: addBooking,
                            },
                            {
                                path: 'add/:cg/close_booking/',
                                name: 'booking-close-classes',
                                component: bookingCloseClasses,
                            },
                            {
                                path: 'edit/:booking_id',
                                name: 'edit-booking',
                                component: editBooking
                            },
                        ]
                    },
                    {
                        path:'bulkpricing',
                        name:'bulkpricing',
                        component:Bulkpricing
                    },
                    {
                        path:'reports',
                        name:'reports',
                        component:Reports
                    },
                ]
            },
            {
                path:'booking',
                component:{
                    render (c) { return c('router-view') }
                },
                children:[
                    {
                        path:'/',
                        name:'fl-search',
                        component: firstLevelSearch
                    }
                ]
            }
        ]
    },
    {
        path: '/404',
        name: '404',
        component: page_404
    }
];

const router = new Router({
  'routes' : routes,
  'mode': 'history'
});

new Vue({
    router,
}).$mount('#menu');

new Vue({
  'router':router,
  store,
  components:{
      alert
  },
  watch:{
      $route:function () {
          let vm =this;
          vm.$store.dispatch("updateAlert",{
              visible:false,
              type:"danger",
              message: ""
          });
      }
  },
  computed:{
      ...mapGetters([
          "showAlert",
          "alertType",
          "alertMessage"
      ])
  }
}).$mount('#app');
