import requests
from data import *
import json

token = EMPLOYER_TOKEN
# do POST
url = URL + 'employer/assignment/interview'
interview = dict(id=3,name='Sales Manager2',response=2, retry=2,introUrl='',exitUrl='',aboutUsUrl='')
interview = json.dumps(interview)
values = dict(token=token,interview=interview)
rsp = requests.put(url, data=values)
print rsp.content