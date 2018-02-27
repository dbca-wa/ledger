import InternalDashboard from '../dashboard.vue'
import Search from '../search.vue'
import OrgAccessTable from '../organisations/dashboard.vue'
import OrgAccess from '../organisations/access.vue'
import Organisation from '../organisations/manage.vue'
import CustomerDashTable from '../customers/dashboard.vue'
import Application from '../applications/application.vue'
import Referral from '../referrals/referral.vue'
import LicenceDashTable from '../licences/dashboard.vue'
import ReturnDashTable from '../returns/dashboard.vue'
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
        {
            path: 'licences',
            component: LicenceDashTable,
            name:"internal-licences-dash"
        },
        {
            path: 'returns',
            component: ReturnDashTable,
            name:"internal-returns-dash"
        },
        {
            path: 'customers',
            component: CustomerDashTable,
            name:"internal-customers-dash"
        },
        {
            path: 'search',
            component: Search,
            name:"internal-search"
        },
        {
            path: 'organisations',
            component: {
                render(c)
                {
                    return c('router-view')
                }
            },
            children: [
                {
                    path: 'access',
                    component: OrgAccessTable,
                    name:"org-access-dash"
                },
                {
                    path: 'access/:access_id',
                    component: OrgAccess,
                    name:"org-access"
                },
                {
                    path: ':org_id',
                    component: Organisation,
                    name:"internal-org-detail"
                },
 
            ]
        },
        {
            path: 'application',
            component: {
                render(c)
                {
                    return c('router-view')
                }
            },
            children: [
                {
                    path: ':application_id',
                    component: {
                        render(c)
                        {
                            return c('router-view')
                        }
                    },
                    children: [
                        {
                            path: '/',
                            component: Application,
                            name:"internal-application"
                        },
                        {
                            path: 'referral/:referral_id',
                            component: Referral,
                            name:"internal-referral"
                        },
                    ]
                },
 
            ]
        },
        /*{
            path: 'application',
            component: Application,
            name:"new_application"
        }*/
    ]
}
