import urllib, urllib2
from data import *

# do POST
url = URL + 'admin/account/logout'
values = dict(token=TOKEN)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content