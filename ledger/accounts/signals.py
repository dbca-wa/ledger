import django.dispatch

name_changed = django.dispatch.Signal(providing_args=['user'])
