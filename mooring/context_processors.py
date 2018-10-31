from django.conf import settings

def mooring_url(request):
    web_url = request.META['HTTP_HOST']
    if web_url in settings.ROTTNEST_ISLAND_URL:
       template_group = 'rottnest'
    else:
       template_group = 'pvs'
    
    return {
        'EXPLORE_PARKS_SEARCH': '/map',
        'EXPLORE_PARKS_CONTACT': '/contact-us',
        'EXPLORE_PARKS_CONSERVE': '/know/conserving-our-moorings',
        'EXPLORE_PARKS_PEAK_PERIODS': '/know/when-visit',
        'EXPLORE_PARKS_ENTRY_FEES': '/know/entry-fees',
        'EXPLORE_PARKS_TERMS': '/know/online-mooring-site-booking-terms-and-conditions',
        'PARKSTAY_EXTERNAL_URL': settings.PARKSTAY_EXTERNAL_URL,
        'DEV_STATIC': settings.DEV_STATIC,
        'DEV_STATIC_URL': settings.DEV_STATIC_URL,
        'TEMPLATE_GROUP' : template_group
        }
