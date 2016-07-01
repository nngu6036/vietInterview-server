import urllib, urllib2
from data import *
import json

# do POST
url = URL + 'employer/assignment/interview/question'
questionList = [dict(title='What',order=1, source='system',type='video',response=2,retry=-1,videoUrl='https://www.youtube.com/watch?v=bInUCgRNROA'),
                dict(title='When',order=2, source='manual',type='text',response=2,retry=-1,videoUrl='https://www.youtube.com/watch?v=bInUCgRNROA')]
questionList = json.dumps(questionList)
values = dict(questionList=questionList,interviewId=INTERVIEW_ID, token=EMPLOYER_TOKEN)
data = urllib.urlencode(values)
req = urllib2.Request(url, data)
rsp = urllib2.urlopen(req)
content = rsp.read()
print content


