import Vue from 'vue'
import Router from 'vue-router'
import MyUserDetails from '@/components/user/manage_my_user_details.vue'
import ProfileDashTable from '@/components/user/profile_dashboard.vue'
import CreateProfile from '@/components/user/profile_create.vue'
import EditProfile from '@/components/user/profile_manage.vue'
import external_routes from '@/components/external/routes'
import internal_routes from '@/components/internal/routes'
Vue.use(Router)

export default new Router({
    mode: 'history',
    routes: [
        {
          path: '/firsttime',
          name: 'first-time',
          component: MyUserDetails
        },
        {
          path: '/account',
          name: 'account',
          component: MyUserDetails
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
                  path: 'create',
                  component: CreateProfile,
                  name:"profile-create"
              },
              {
                  path: ':profile_id',
                  component: EditProfile,
                  name:"profile-detail"
              },
          ]
        },
        external_routes,
        internal_routes
    ]
})
