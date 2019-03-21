import InternalDashboard from '../dashboard.vue'
import Search from '../search.vue'
import OrgAccessTable from '../organisations/dashboard.vue'
import OrgAccess from '../organisations/access.vue'
import Organisation from '../organisations/manage.vue'
import UserDashTable from '../users/dashboard.vue'
import User from '../users/manage.vue'
import Application from '../applications/application.vue'
import LicenceDashTable from '../licences/dashboard.vue'
import CallEmailTableDash from '../call_email/call_email_dashboard.vue'
import ReturnDashTable from '../returns/dashboard.vue'
import Returns from '../returns/access.vue'

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
            path: 'call_email',
            component: CallEmailTableDash,
            name:"internal-call-email-dash"
        },
        {
            path: 'returns',
            component: ReturnDashTable,
            name:"internal-returns-dash"
        },
        {
            path: 'search',
            component: Search,
            name:"internal-search"
        },
        {
            path: 'return/:return_id',
            component: Returns,
            name:'access_return'
        },
        {
            path: 'users',
            component: {
                render(c)
                {
                    return c('router-view')
                }
            },
            children: [
                {
                    path: '/',
                    component: UserDashTable,
                    name:"internal-users-dash"
                },
                {
                    path: ':user_id',
                    component: User,
                    name:"internal-user-detail"
                },
            ]
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
