import urllib, urllib2,json
from data import *

# do POST

url = URL + 'admin/account/login'
print url
values = dict(login=ACCOUNT, password=PASS)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
j = json.load(rsp)
print j

    
    
