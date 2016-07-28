import  erppeek
from data import  *

#client = erppeek.Client('http://192.168.1.200:8069', 'career', 'admin', '123456')
client = erppeek.Client('http://10.158.7.18:8069', 'career', 'admin', '123456')
for job in   client.model('hr.job').browse([('name','like','Xe')]):
    print job


