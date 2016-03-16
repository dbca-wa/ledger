from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.views.generic import RedirectView


# Example views, most of them are just template rendering


def home(request):
    return render(request, 'customers/home.html')


def done(request):
    return render(request, 'customers/done.html')


def login_form(request):
    return render(request, 'customers/form.html')


def validation_sent(request):
    messages.success(request,
                     "An email has been sent to you. "
                     "Check your mailbox and click on the link to complete the login process.")
    return redirect('/')


def logout(request):
    auth_logout(request)
    return redirect('/')


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


class VerificationView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        redirect_url = '{}?verification_code={}'.format(
            reverse('social:complete', args=('email',)),
            kwargs['token']
        )
        if self.request.user and hasattr(self.request.user, 'email'):
            redirect_url += '&email={}'.format(self.request.user.email)
        return redirect_url
