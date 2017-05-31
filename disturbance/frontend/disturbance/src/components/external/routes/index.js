import ExternalDashboard from '../dashboard.vue'

export default {
    path: '/external',
    component: {
        render (c) { return c('router-view') }
    },
    children: [
        {
            path: '/',
            component: ExternalDashboard
        }
    ]
}
