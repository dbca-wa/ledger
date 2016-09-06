import django.dispatch

identification_uploaded = django.dispatch.Signal(providing_args=['request'])

licence_issued = django.dispatch.Signal(providing_args=['wildlice_licence'])
