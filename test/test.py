import  erppeek
from data import  *

#lient = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
client = erppeek.Client('http://vietinterview.com:8069', 'career', 'admin', '123456')
q =  client.model('career.question').browse([('lang','=','vi')])
q.unlink()
c =  client.model('career.question_category').browse([('lang','=','vi')])
c.unlink()
