from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from ledger.accounts import helpers
from ledger.accounts import forms as app_forms
from django.utils.http import urlquote_plus, urlencode
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .forms import FirstTimeForm
from .models import EmailUser,EmailUserChangeLog,PrivateDocument
import json

# Example views, most of them are just template rendering


def home(request):
    return render(request, 'customers/home.html')


def done(request):
    return render(request, 'customers/done.html')


def bounce(request):
    if ('HTTP_REFERER' in request.META) and (request.META['HTTP_REFERER']):
        return redirect(request.META['HTTP_REFERER'])
    return redirect('/')


@login_required(login_url='accounts:home')
def first_time(request): 
    context = {}
    if request.method == 'POST':
        form = FirstTimeForm(request.POST)
        redirect_url = form.data['redirect_url']
        if not redirect_url:
            redirect_url = '/'
        if form.is_valid():
            # set user attributes
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.dob = form.cleaned_data['dob']
            request.user.save()
            return redirect(redirect_url)
        context['form'] = form
        context['redirect_url'] = redirect_url
        return render(request, 'customers/firsttime.html', context)
    # GET default
    if 'next' in request.GET:
        context['redirect_url'] = request.GET['next']
    else:
        context['redirect_url'] = '/'
    return render(request, 'customers/firsttime.html', context)


def login_retry(request):
    messages.error(request, "There was an error validating your email address. Please try again.")
    return bounce(request)


def login_expired(request):
    messages.error(request,
                   "This sign-in link has expired. "
                   "Please log in again to generate a new sign-in link.")
    return bounce(request)


def validation_sent(request):
    messages.success(request,
                     "An email has been sent to you. "
                     "Check your mailbox and click on the link to complete the sign-in process.")
    return bounce(request)


def logout(request, *args, **kwargs):
    user = request.user
    auth_logout(request)
    if bool(request.GET.get('link_account')) and not user.profiles.all():
        user.delete()
    messages.success(request,
                     "You have successfully logged out.")
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    return bounce(request)


# The user will get an email with a link pointing to this view, this view just
# redirects the user to PSA complete process for the email backend. The mail
# link could point directly to PSA view but it's handy to proxy it and do
# additional computation if needed.
def token_login(request, token, email):
    redirect_url = '{}?{}'.format(
        reverse('social:complete', args=('email',)),
        urlencode({'verification_code': token, 'email': email})
    )
    return redirect(redirect_url)



class AccountManagement(generic.TemplateView):
    template_name = 'ledger/accounts/account_management.html'

    def get_context_data(self, **kwargs):
        ctx = super(AccountManagement,self).get_context_data(**kwargs)        
        if helpers.is_account_admin(self.request.user) is True:
            system_id = self.request.GET.get('system_id','')

        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return ctx
    
class AccountChange(LoginRequiredMixin, UpdateView):
   
    template_name = 'ledger/accounts/account_change.html'
    model = EmailUser
    form_class = app_forms.EmailUserForm    


    def get_initial(self):
        initial = super(AccountChange, self).get_initial()
        person = self.get_object()
        initial['id'] = person.id
        
        initial['identification2'] = person.identification2

        return initial
    def get_context_data(self, **kwargs):
        ctx = super(AccountChange,self).get_context_data(**kwargs)
        ctx['account_id'] = self.kwargs['pk']

        if helpers.is_account_admin(self.request.user) is True:
            pass

        else:
            self.template_name = 'dpaw_payments/forbidden.html'
        return ctx
    
    def get_absolute_url(self):       
        
        return "/ledger/account-management/"

    def get_absolute_account_url(self):        
        id = self.get_object().id
        return "/ledger/account-management/{}/change/".format(id)

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):            
            return HttpResponseRedirect(self.get_absolute_url())

        first_name  = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if len(first_name) < 1 and len(last_name) < 1:             
            messages.error(self.request, "No Given name or last name data")

        return super(AccountChange, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        if helpers.is_account_admin(self.request.user) is True:
            self.object = form.save(commit=False)
            forms_data = form.cleaned_data
            uservalue_map = {}
            eu = EmailUser.objects.filter(id=self.object.id).values()
            
            for e in eu[0].keys():
                uservalue_map[e] = eu[0][e]            
            
            if 'identification2_id' in uservalue_map:
                if uservalue_map['identification_id'] is not None:
                    self.object.identification2 = PrivateDocument.objects.get(id=uservalue_map['identification2_id'])

            identification2_filechanged = False
            if 'identification2_json' in self.request.POST:
            
                try:
                    json_data = json.loads(self.request.POST['identification2_json'])
                    if self.object.identification2:
                        if self.object.identification2.id != int(json_data['doc_id']):
                            doc = PrivateDocument.objects.get(id=int(json_data['doc_id']))
                            self.object.identification2 = doc
                            identification2_filechanged = True
                    else:
                        doc = PrivateDocument.objects.get(id=int(json_data['doc_id']))
                        self.object.identification2 = doc
                        identification2_filechanged = True                        
                        
                except Exception as e:
                    print (e)

            
            
            self.object.save()
            if identification2_filechanged is True:
                EmailUserChangeLog.objects.create(emailuser=self.object, change_key="identification2", change_value=str(self.object.identification2.id) + ":" +self.object.identification2.name,change_by=self.request.user)

            for fd in forms_data:
            
                if fd == 'identification2':
                    pass        
                else:
                    
                    if uservalue_map[fd] != forms_data[fd]:
                        EmailUserChangeLog.objects.create(emailuser=self.object, change_key=fd, change_value=forms_data[fd],change_by=self.request.user)
            # 


            messages.success(self.request, "Succesfully Updated {} {} <a href='{}' class='btn btn-sm btn-primary'>Change</a> ".format(self.object.first_name,self.object.last_name,self.get_absolute_account_url()))
            return HttpResponseRedirect(self.get_absolute_url())
        else:            
            return HttpResponseRedirect(self.get_absolute_account_url())
    