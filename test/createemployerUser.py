import urllib, urllib2
from data import *
import json

# do POST
url = URL + 'admin/company/user'
print url
user = dict(name='User3',email='nem3@gmail.com',
               password='123456')
user = json.dumps(user)
values = dict(user=user, companyId=24,token=TOKEN)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content

