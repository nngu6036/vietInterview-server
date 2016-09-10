import  erppeek
from data import  *

#client = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
client = erppeek.Client('http://homecredit.demo.vietinterview.com:8069', 'career', 'admin', '123456')
interivew_input = client.model('survey.user_input').get([('token','=','95e2d807-312a-41c6-b6c5-e2a16544c1ec')])
print interivew_input.survey_id.job_id.isEnabled(), interivew_input.deadline
if interivew_input:
    interivew_input.write({'state':'new'})
#for job in client.model('hr.job').browse([]):
#    print job.id. job.name, job.isEnabled()



