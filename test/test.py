import  erppeek
from data import  *

client = erppeek.Client('http://vietinterview.com:8069', 'career', 'admin', '123456')
company = client.model('res.company').get(3)
print company.user_ids
user  = client.model('res.users').get(5)
print user.company_id
print user.company_ids
