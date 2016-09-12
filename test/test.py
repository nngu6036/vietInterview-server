import  erppeek
from data import  *

#client = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
client = erppeek.Client('http://demo.vietinterview.com:8069', 'career', 'admin', '123456')
user = client.model('career.employer').get([('login','=','homecredit')])
print user.company_id.license_instance_id.license_id
print user.company_id.license_instance_id.state
license = client.model('career.license').get([('name','=','Platnium')])
print license
user.company_id.license_instance_id.write({'state':'active','license_id':license.id})
#for job in client.model('hr.job').browse([]):
#    print job.id. job.name, job.isEnabled()



