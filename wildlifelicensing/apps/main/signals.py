import django.dispatch

identification_uploaded = django.dispatch.Signal(providing_args=['user'])
