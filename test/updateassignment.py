import requests
from data import *
import json

token = EMPLOYER_TOKEN
# do POST
url = URL + 'employer/assignment'
s_val = dict(id=4,name='Salesman',description='Sales',deadline='2017-02-02')
assignment = json.dumps(s_val)
values = dict(token=token,assignment=assignment)
rsp = requests.put(url, data=values)
print rsp.content