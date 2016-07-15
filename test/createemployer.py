import urllib, urllib2
from data import *
import json

# do POST
url = URL + 'admin/employer'
print url
employer = dict(name='Thanh Cong A Chau Sale 7',email='sales7@vietinterview.com',
               password='123456',licenseId='1',licenseExpire='2017-1-1')
employer = json.dumps(employer)
values = dict(employer=employer, token=TOKEN)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content


