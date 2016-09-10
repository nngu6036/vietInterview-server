import  erppeek
from data import  *

#client = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
client = erppeek.Client('http://vietinterview.com:8069', 'career', 'admin', '123456')
session = client.model('career.session').get([('token','=','7NATKBG07ZEHAE58YQ8ESS9J')])
print session

#for job in client.model('hr.job').browse([]):
#    print job.id. job.name, job.isEnabled()



