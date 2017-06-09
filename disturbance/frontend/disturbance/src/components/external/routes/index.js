import ExternalDashboard from '../dashboard.vue'
import Proposal from '../proposal.vue'
import ProposalApply from '../proposal_apply.vue'
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
                    component: ProposalApply,
                    name:"apply_proposal"
                },
                {
                    path: ':proposal_id',
                    component: Proposal,
                    name:"draft_proposal"
                },
            ]
        }
    ]
}
