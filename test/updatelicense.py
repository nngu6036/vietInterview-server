import requests
from data import *
import json

token = TOKEN
# do POST
url = URL + 'admin/license'
s_val = dict(id=1,name='Bronze',email='99',assignment='4')
license = json.dumps(s_val)
values = dict(token=token,license=license)
rsp = requests.put(url, data=values)
print rsp.content