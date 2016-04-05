from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as auth_logout
from django.contrib import messages


# Example views, most of them are just template rendering


def home(request):
    return render(request, 'customers/home.html')


def done(request):
    return render(request, 'customers/done.html')


def bounce(request):
    if ('HTTP_REFERER' in request.META) and (request.META['HTTP_REFERER']):
        return redirect(request.META['HTTP_REFERER'])
    return redirect('/')


def validation_sent(request):
    messages.success(request,
                     "An email has been sent to you. "
                     "Check your mailbox and click on the link to complete the login process.")
    return bounce(request)


def logout(request):
    auth_logout(request)
    messages.success(request,
                     "You have successfully logged out.")
    return bounce(request)


# The user will get an email with a link pointing to this view, this view just
# redirects the user to PSA complete process for the email backend. The mail
# link could point directly to PSA view but it's handy to proxy it and do
# additional computation if needed.
def token_login(request, token):
    redirect_url = '{}?verification_code={}'.format(
        reverse('social:complete', args=('email',)),
        token
    )
    if request.user and hasattr(request.user, 'email'):
        redirect_url += '&email={}'.format(request.user.email)
    return redirect(redirect_url)
