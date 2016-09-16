# -*- coding: utf-8 -*-

import urllib, urllib2
from data import *
import json

# do POST
url = URL + 'admin/company'
print url
company = dict(name='HD Saison',image='',licenseId='39',licenseExpire='2017-1-1',email='')
company = json.dumps(company)
values = dict(company=company, token=TOKEN)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content


