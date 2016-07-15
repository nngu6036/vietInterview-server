import time
import erppeek
import thread
module = 'career'

URL = 'http://vietinterview.com:8069'
#remoteClient = erppeek.Client(URL, db, 'admin', 'admin')
#remoteClient.upgrade(module)
#URL = 'http://192.168.2.4:8069'
client = erppeek.Client(URL)

dbs = client.db.list()
#dbs=['template_cafe@emaerp.vn']
for db in dbs:
    print db
    if not "@" in db:
        continue

    remoteClient = erppeek.Client(URL, db, 'admin', 'admin')
    ''' data1 = remoteClient.model('ir.model.data').browse([('name','=','account_company_product_sale'),('module','=','ema_pos')])
    if data1:
        data1.write({'name':'account_company_income'})
    data2 = remoteClient.model('ir.model.data').browse([('name','=','account_company_cost_of_good_sold'),('module','=','ema_pos')])
    if data2:
        data2.write({'name':'account_company_expense'})
    data3 = remoteClient.model('ir.model.data').browse([('name','=','account_general_receivable_pos_customer'),('module','=','ema_pos')])
    if data3:
        data3.write({'name':'account_company_receivable'})
    data4 = remoteClient.model('ir.model.data').browse([('name','=','account_general_payable_pos_customer'),('module','=','ema_pos')])
    if data4:
        data4.write({'name':'account_company_payable'})'''


    if remoteClient.modules(module)  and ('installed' in remoteClient.modules(module) or 'to upgrade' in remoteClient.modules(module)):
        remoteClient.upgrade(module)
        print db
    #time.sleep(10)
