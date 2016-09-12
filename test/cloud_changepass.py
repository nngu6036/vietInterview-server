
import erppeek

account = 'homecredit'
passwd = '123456'
URL = 'http://demo.vietinterview.com:8069'

#client = erppeek.Client('http://cloud.emaerp.vn:8069', 'ema', 'admin', '123456')
client = erppeek.Client(URL, 'career', 'admin', '123456')
user = client.model('res.users').get([('login','=',account)])
user.write({'password':passwd})
