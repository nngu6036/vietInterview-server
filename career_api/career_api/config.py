'''
Created on Sep 9, 2015

@author: QuangN
'''


class DefaultConfig(object):
    DEBUG = False
    TESTING = False
    JSON_AS_ASCII = False
    SECRET_KEY = '\xfd\xb7_N\xd7^\xb4\xf4\xee\xfb\x9fJ\xf3\x85$an\xc4\x81\x1e\xe9o)%'
    ERP_SERVER_URL = 'http://localhost:8069'
    ERP_DB = 'career'
    ERP_DB_USER = 'admin'
    ERP_DB_PASS = '123456'
    FILE_UPLOAD_FOLDER = '/home/data/Documents'
    VIDEO_UPLOAD_FOLDER = '/home/data/Videos'
    VIDEO_DOWNLOAD_FOLDER = 'https://vietinterview.com/videos/'
    RESET_PASS_LINK = '<a href="https://vietinterview.com/#/account/resetPass?token=${object.token}">Reset password link</a>'

