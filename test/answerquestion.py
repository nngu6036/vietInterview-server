import urllib, urllib2
from data import *
import json

# do POST
url = URL + 'candidate/interview/answer?code='+CODE
values = dict(questionId=33, videoUrl='https://vietinterview.com/videos/46301506142016Tue_Jun_14_2016_153045_GMT0700_SE_Asia_Standard_Timevideo.webm')
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content


