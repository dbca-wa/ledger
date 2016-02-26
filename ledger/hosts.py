from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'ledger', 'ledger.urls', name='ledger'),
    host(r'wildlifelicensing', 'wildlifelicensing.urls', name='wildlifelicensing')
)
