import InternalDashboard from '../dashboard.vue'
//import Proposal from '../proposal.vue'
export default
{
    path: '/internal',
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
            component: InternalDashboard
        },
        /*{
            path: 'proposal',
            component: Proposal,
            name:"new_proposal"
        }*/
    ]
}
