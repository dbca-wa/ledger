import ExternalDashboard from '../dashboard.vue'
import Application from '../application.vue'
import ApplicationApply from '../application_apply.vue'
import ApplicationApplyOrganisation from '../application_apply_organisation.vue'
import ApplicationApplyLicence from '../application_apply_licence.vue'
import ApplicationSubmit from '../application_submit.vue'
import Organisation from '../organisations/manage.vue'
import Returns from '../returns/enter_return.vue'
import ReturnsQuestion from '../returns/enter_return_question.vue'
import ReturnsSheet from '../returns/enter_return_sheet.vue'
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
            path: 'return',
            component:
            {
                render(c)
                {
                    return c('router-view')
                }
            },
            children: [
                {
                    path: ':return_id',
                    component: Returns,
                    name: 'enter_return'
                },
                {
                    path: 'question/:return_id',
                    component: ReturnsQuestion,
                    name: 'enter_return_question'
                },
                {
                    path: 'sheet/:return_id',
                    component: ReturnsSheet,
                    name: 'enter_return_sheet'
                },
            ]
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
                    path: 'org_select',
                    component: ApplicationApplyOrganisation,
                    name:"apply_application_organisation"
                },
                {
                    path: 'licence_select',
                    component: ApplicationApplyLicence,
                    name:"apply_application_licence"
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
