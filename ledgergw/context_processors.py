from django.conf import settings

def global_config(request):
    print ('global_config') 
    config = {'settings': settings}
    return config
