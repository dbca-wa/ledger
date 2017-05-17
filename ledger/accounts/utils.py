import urllib.request as req
import urllib
bs4 import BeautifulSoup

def abn_lookup(abn):
    f = { 'searchString' : abn,'includeHistoricalDetails':'N','authenticationGuid':UID}
    f = urllib.urlencode(f)
    url = "http://abr.business.gov.au/abrxmlsearchRPC/AbrXmlSearch.asmx/SearchByABNv201408?"+f
    conn = req.urlopen(url)
    content = conn.read();
    soup = BeautifulSoup(content,'xml')
