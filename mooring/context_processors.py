from django.conf import settings

def mooring_url(request):
    return {
        'EXPLORE_PARKS_SEARCH': '{}/map'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_CONTACT': '{}/contact-us'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_CONSERVE': '{}/know/conserving-our-moorings'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_PEAK_PERIODS': '{}/know/when-visit'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_ENTRY_FEES': '{}/know/entry-fees'.format(settings.EXPLORE_PARKS_URL),
        'EXPLORE_PARKS_TERMS': '{}/know/online-mooring-site-booking-terms-and-conditions'.format(settings.EXPLORE_PARKS_URL),
        'PARKSTAY_EXTERNAL_URL': settings.PARKSTAY_EXTERNAL_URL,
        'DEV_STATIC': settings.DEV_STATIC,
        'DEV_STATIC_URL': settings.DEV_STATIC_URL
        }
