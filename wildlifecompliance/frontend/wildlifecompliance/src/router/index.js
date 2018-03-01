import Vue from 'vue'
import Router from 'vue-router'
import Hello from '@/components/Hello'
import Profile from '@/components/user/profile.vue'
import ProfileDashTable from '@/components/user/profile_dashboard.vue'
import UserProfile from '@/components/user/manage_profile.vue'
import external_routes from '@/components/external/routes'
import internal_routes from '@/components/internal/routes'
Vue.use(Router)

export default new Router({
    mode: 'history',
    routes: [
        {
          path: '/firsttime',
          name: 'first-time',
          component: Profile
        },
        {
          path: '/account',
          name: 'account',
          component: Profile
        },
        {
            path: '/profiles',
            component: {
                render(c)
                {
                    return c('router-view')
                }
            },
            children: [
                {
                    path: '/',
                    component: ProfileDashTable,
                    name:"profiles-dash"
                },
                {
                    path: ':profile_id',
                    component: UserProfile,
                    name:"profile-detail"
                },
            ]
        },
        external_routes,
        internal_routes
    ]
})
