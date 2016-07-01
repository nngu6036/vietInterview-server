import requests
from data import *
import json

token = EMPLOYER_TOKEN
# do POST
url = URL + 'employer/assignment/interview/question'
questionIds=[11]
questionIds = json.dumps(questionIds)
values = dict(token=token, questionIds=questionIds)
rsp = requests.delete(url, data=values)
print rsp.content