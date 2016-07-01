import requests
from data import *
import json

token = TOKEN
# do POST
url = URL + 'admin/employer'
employer = dict(id=1,name='Cong ty Sapoche100',licenseId=1,licenseExpire='2017-01-02',
               login='sapoche15',password='123456')
employer = json.dumps(employer)
values = dict(employer=employer, token=TOKEN)
rsp = requests.put(url, data=values)
print rsp.content