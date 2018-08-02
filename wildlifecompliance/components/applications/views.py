from django.http import HttpResponse,JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from wildlifecompliance.components.applications.utils import create_data_from_form
from wildlifecompliance.components.applications.models import Application
from wildlifecompliance.components.main.utils import get_session_application, delete_session_application, bind_application_to_invoice
import json,traceback

class ApplicationView(TemplateView):
    template_name = 'wildlifecompliance/application.html'

    def post(self, request, *args, **kwargs):
        extracted_fields = []
        try:
            print(' ---- applications views.py ---- ')
            application_id = request.POST.pop('application_id')
            application = Application.objects.get(application_id)
            schema = json.loads(request.POST.pop('schema')[0])
            extracted_fields = create_data_from_form(schema,request.POST, request.FILES)
            application.schema = schema;
            application.data = extracted_fields
            print(application_id)
            print(application)
            application.save()
            return redirect(reverse('external'))
        except:
            traceback.print_exc
            return JsonResponse({error:"something went wrong"},safe=False,status=400)


class ApplicationSuccessView(TemplateView):
    template_name = 'wildlifecompliance/templates/wildlifecompliance/application_success.html'

    def get(self, request, *args, **kwargs):
        try:
            application = get_session_application(request.session)
            invoice_ref = request.GET.get('invoice')
            print('application success view')
            print('application')
            print(application)
            print('invoice_ref')
            print(invoice_ref)
            try:
                bind_application_to_invoice(request, application, invoice_ref)
            except BindApplicationException:
                delete_session_application(request.session)
                return redirect('home')

        except Exception as e:
                delete_session_application(request.session)
                return redirect('home')

        context = {
            'application': application
        }
        print('context')
        print(context)
        delete_session_application(request.session)
        return render(request, self.template_name, context)