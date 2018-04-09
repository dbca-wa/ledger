from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlquote_plus, urlencode

from .forms import FirstTimeForm
from .models import EmailUser

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
