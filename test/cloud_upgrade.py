import time
import erppeek
import thread
module = 'career'
db='career'
URL = 'http://localhost:8069'
#remoteClient = erppeek.Client(URL, db, 'admin', 'admin')
#remoteClient.upgrade(module)
#URL = 'http://192.168.2.4:8069'
client = erppeek.Client(URL)

dbs = client.db.list()
#dbs=['template_cafe@emaerp.vn']


remoteClient = erppeek.Client(URL, db, 'admin', '123456')


if remoteClient.modules(module)  and ('installed' in remoteClient.modules(module) or 'to upgrade' in remoteClient.modules(module)):
    remoteClient.upgrade(module)
#time.sleep(10)
