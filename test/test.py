import  erppeek
from data import  *

client = erppeek.Client('http://demo.vietinterview.com:8069', 'career', 'admin', '123456')
#client = erppeek.Client('http://10.158.7.18:8069', 'career', 'admin', '123456')
#user = client.model('res.users').browse([('login','=','hdsaison')])
#user.company_id.write({'url':'https://hdsaison.vietinterview.com'})
user = client.model('res.users').browse([('login','=','homecredit')])
user.company_id.write({'url':'https://homecredit.demo.vietinterview.com'})
#print user.company_id.url
#job = client.model('hr.job').browse([])
#job.write({'status':'published'})




