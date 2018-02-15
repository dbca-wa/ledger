import ExternalDashboard from '../dashboard.vue'
import Application from '../application.vue'
import ApplicationApply from '../application_apply.vue'
import ApplicationSubmit from '../application_submit.vue'
import Organisation from '../organisations/manage.vue'
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
            component: ExternalDashboard,
            name: 'external-applications-dash' 
        },
        {
            path: 'organisations/manage/:org_id',
            component: Organisation
        },
        {
            path: 'application',
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
                    component: ApplicationApply,
                    name:"apply_application"
                },
                {
                    path: 'submit',
                    component: ApplicationSubmit,
                    name:"submit_application"
                },
                {
                    path: ':application_id',
                    component: Application,
                    name:"draft_application"
                },
            ]
        }
    ]
}
