import ExternalDashboard from '../dashboard.vue'
import Proposal from '../proposal.vue'
export default
{
    path: '/external',
    component:
    {
        render(c)
        {
            return c('router-view')
        }
    },
    children: [
        {
            path: '/',
            component: ExternalDashboard
        },
        {
            path: 'proposal',
            component: Proposal,
            name:"new_proposal"
        }
    ]
}
