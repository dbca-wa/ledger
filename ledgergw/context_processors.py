from django.conf import settings

def global_config(request):
    
    config = {'settings': settings}
    return config
