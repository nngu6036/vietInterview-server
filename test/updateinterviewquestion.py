import requests
from data import *
import json

token = EMPLOYER_TOKEN
# do POST
url = URL + 'employer/assignment/interview/question'
questionList = [dict(id=10,title='What',order=1, source='system',type='video',response=2,retry=-1,videoUrl='https://www.youtube.com/watch?v=bInUCgRNROA'),
                dict(id=11,title='When',order=2, source='manual',type='text',response=2,retry=-1,videoUrl='')]

questionList = json.dumps(questionList)
values = dict(token=token,questionList=questionList)
rsp = requests.put(url, data=values)
print rsp.content