import urllib, urllib2,json
from data import *

# do POST

url = URL + 'employer/account/login'
print url
values = dict(email='technicalmanager@gmail.com', password='123456')
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
j = json.load(rsp)
print j

    
    
