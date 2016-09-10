import  erppeek
from data import  *

client = erppeek.Client('http://demo.vietinterview.com:8069', 'career', 'admin', '123456')
#client = erppeek.Client('http://10.158.7.18:8069', 'career', 'admin', '123456')
input = client.model('survey.user_input').get([('token','=',CODE)])
print input.state
input.write({'state':'new'})
#jobs = client.model('hr.job').browse([])
#jobs.write({'status':'published'})
#for job in client.model('hr.job').browse([('name','=','test')]):
#    print job
    #job.write({'state':'recruit'})
#    print job.isEnabled()
applicant = client.model('hr.applicant').get([('input_token', '=', CODE)])
print applicant.interview_id
print applicant.interview_id.job_id
print applicant.interview_id.job_id.status

