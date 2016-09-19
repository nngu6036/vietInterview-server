import  erppeek
from data import  *

#client = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
client = erppeek.Client('http://10.158.7.18:8069', 'career', 'admin', '123456')
#companys = client.model('res.company').browse([])
#companys.write({'website':'https://vietinterview.com'})
companys = client.model('res.company').browse([])
companys.write({'website':'https://vietinterview.com'})




