import Vue from 'vue'
import Router from 'vue-router'
import Hello from '@/components/Hello'
import Profile from '@/components/user/profile.vue'

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
