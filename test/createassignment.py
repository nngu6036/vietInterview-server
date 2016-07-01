import urllib, urllib2
from data import *
import json

# do POST
url = URL + 'employer/assignment'
assignment = dict(name='Sales Manager2',description='HR', deadline='2017-01-01')
assignment = json.dumps(assignment)
values = dict(assignment=assignment, token=EMPLOYER_TOKEN)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content


