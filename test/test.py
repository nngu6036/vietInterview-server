import  erppeek
from data import  *

client = erppeek.Client('http://demo.vietinterview.com:8069', 'career', 'admin', '123456')
#client = erppeek.Client('http://10.158.7.18:8069', 'career', 'admin', '123456')
#user = client.model('res.users').browse([('login','=','hdsaison')])

#print user.company_id.url
for job in  client.model('hr.job').browse([]):
	print job.isEnabled()

#job.write({'status':'published'})




