import urllib, urllib2
from data import *
import json

# do POST
url = URL + 'employer/assignment/interview/invite'
values = dict(subject='Invite', body='Invite',candidates=json.dumps(['kamezoko@yahoo.com','kamezoko@yahoo.com']),token=EMPLOYER_TOKEN,interviewId=INTERVIEW_ID)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content


