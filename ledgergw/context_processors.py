from django.conf import settings

def global_config(request):
    
    config = {'settings': settings,
              'template_group' : 'dbcablack',
              'DJANGO_SETTINGS': settings,
              }
    return config
