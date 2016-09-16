import  erppeek
from data import  *

#client = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
client = erppeek.Client('http://demo.vietinterview.com:8069', 'career', 'admin', '123456')
user = client.model('career.employer').get([('login','=','homecredit')])
print user.company_id.website
user.company_id.write({'website':'https://homecredit.demo.vietinterview.com'})




