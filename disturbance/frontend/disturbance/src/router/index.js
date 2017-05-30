import Vue from 'vue'
import Router from 'vue-router'
import Hello from '@/components/Hello'
import Profile from '@/components/user/profile.vue'
import external_routes from '@/components/external/routes'
import internal_routes from '@/components/internal/routes'

Vue.use(Router)

export default new Router({
    mode: 'history',
    routes: [
        {
          path: '/',
          name: 'Hello',
          component: Hello
        },
        {
          path: '/firsttime',
          name: 'first-time',
          component: Profile
        }
    ]
})
