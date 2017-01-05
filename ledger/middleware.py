from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.http import urlquote_plus

class FirstTimeNagScreenMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and request.method == 'GET':
            #print('DEBUG: {}: {} == {}, {} == {}, {} == {}'.format(request.user, request.user.first_name, (not request.user.first_name), request.user.last_name, (not request.user.last_name), request.user.dob, (not request.user.dob) ))
            if (not request.user.first_name) or (not request.user.last_name) or (not request.user.dob):
                path_ft = reverse('accounts:first_time')
                path_logout = reverse('accounts:logout')
                if request.path not in (path_ft, path_logout):
                    return redirect(reverse('accounts:first_time')+"?next="+urlquote_plus(request.get_full_path()))
