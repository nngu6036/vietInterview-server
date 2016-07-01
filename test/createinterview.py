import urllib, urllib2
from data import *
import json

# do POST
url = URL + 'employer/assignment/interview'
interview = dict(name='Sales Manager2',response=2, retry=2,introUrl='',exitUrl='',aboutUsUrl='')
interview = json.dumps(interview)
values = dict(interview=interview, token=EMPLOYER_TOKEN,assignmentId=ASSIGNMENT_ID)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content


