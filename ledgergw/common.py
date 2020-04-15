from ledgergw import models as ledgergw_models
import ipaddress


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def api_allow(clientip,apikey):
    allow = False
    if ledgergw_models.API.objects.filter(api_key=apikey,active=1).count() > 0:
        api = ledgergw_models.API.objects.filter(api_key=apikey)[0]
        allowed_ips = api.allowed_ips.splitlines()
        for line in allowed_ips:
            print (line)
            if ipaddress.ip_address(clientip) in ipaddress.ip_network(line):
                allow = True
                print ('YES') 
    
              
    #ipaddress.ip_address('192.168.0.1') in ipaddress.ip_network('192.168.0.0/24')


    return allow
