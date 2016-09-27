import erppeek
from data import *

client = erppeek.Client('http://demo.vietinterview.com:8069', 'career', 'admin', '123456')
#client = erppeek.Client('http://10.158.7.18:8069', 'career', 'admin', '123456')
# user = client.model('res.users').browse([('login','=','hdsaison')])

# print user.company_id.url
# for job in  client.model('hr.job').browse([]):
#	print job.status, job.state

# job.write({'status':'published'})

for applicant in client.model('hr.applicant').browse([]):
    for employee in client.model('career.employee').browse([('login', '=', applicant.email_from)]):
        print employee.user_id.id
        applicant.write({'user_id': employee.user_id.id})
