'''
Created on Sep 9, 2015

@author: QuangN
'''
import erppeek

from career_api import app

class ErpInstance(object):


    def __init__(self):
        pass;

    @classmethod
    def fromToken(self,token,roles):
         erpInstance = ErpInstance()
         sessionInfo = session_service.validate(token,roles)
         if not sessionInfo:
             return False
         erpInstance.client = erppeek.Client(app.config['ERP_SERVER_URL'], sessionInfo['db'], sessionInfo['user'], sessionInfo['password'])
         return erpInstance

    def service(self,name):
        return self.client.model(name)

mainInstance =  erppeek.Client(app.config['ERP_SERVER_URL'], app.config['ERP_DB'], app.config['ERP_DB_USER'], app.config['ERP_DB_PASS'])
session_service = mainInstance.model('career.session_service')