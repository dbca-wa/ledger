import django.dispatch

identification_uploaded = django.dispatch.Signal(providing_args=['user'])

licence_issued = django.dispatch.Signal(providing_args=['wildlice_licence'])
