import urllib, urllib2
from data import *
import base64
import json
token = TOKEN
# do POST
url = URL + 'employer/report/assessment?token=%s&candidateId=%d'%(EMPLOYER_TOKEN,CANDIDATE_ID)
print url
rsp = urllib2.urlopen(url)
resp = json.loads(rsp.read())
print len(resp['content'].decode('base64'))
file = open("E://tmp/read1.pdf",'wb')
file.write(resp['content'].decode('base64'))
file.close()
