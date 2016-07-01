import  erppeek
from data import  *

client = erppeek.Client('http://vietinterview.com:8069', 'career', 'admin', '123456')
group1 = client.model('res.groups').get([('name','=','Officer')])
print group1
group2 = client.model('res.groups').get([('name','=','Survey / User')])
print group2
print group1.id
print group2.id
for survey in client.model('survey.survey').browse([]):
    survey.write({'introUrl':"https://vietinterview.com/videos/53140906102016entry23434.mp4"})
