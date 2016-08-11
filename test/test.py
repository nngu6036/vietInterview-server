import  erppeek
from data import  *

client = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
#client = erppeek.Client('http://10.158.7.18:8069', 'career', 'admin', '123456')
for job in client.model('hr.job').browse([]):
    if job.survey_id:
        job.survey_id.write({'job_id':job.id,'mode':'video','round':1})
        job.survey_id.write({'status': 'published'})
for candidate in  client.model('hr.applicant').browse([]):
    candidate.write({'interview_id':candidate.survey.id})


