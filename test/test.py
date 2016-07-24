import  erppeek
from data import  *

#lient = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
client = erppeek.Client('http://vietinterview.com:8069', 'career', 'admin', '123456')
for intervieww in   client.model('survey.survey').browse([]):
    intervieww.write({'prepare':1})
for question in   client.model('survey.question').browse([]):
    question.write({'prepare':1})

