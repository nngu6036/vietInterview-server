'''
Created on Sep 9, 2015

@author: QuangN
'''
import erppeek
from flask import jsonify, request
from career_api import app

class Session(object):
    def __init__(self):
        pass;

    @staticmethod
    def start(login,password,role):
        token = mainInstance.model('career.session').login(app.config['ERP_DB'], login, password, role)
        return token

    @staticmethod
    def stop( token):
        mainInstance.model('career.session').logout(token)

    @classmethod
    def resume(self,token,roles):
         session = Session()
         session.info = mainInstance.model('career.session').validateToken(token,roles)
         if not session.info:
             raise Exception("Invalid token %s ", token)
         return session

mainInstance = erppeek.Client(app.config['ERP_SERVER_URL'], app.config['ERP_DB'], app.config['ERP_DB_USER'],
                              app.config['ERP_DB_PASS'])

admin_service = mainInstance.model('career.admin_service')
common_service = mainInstance.model('career.common_service')
account_service = mainInstance.model('career.account_service')
license_service = mainInstance.model('career.license_service')
mail_service = mainInstance.model('career.mail_service')

license_obj = mainInstance.model('career.license')
license_category_obj = mainInstance.model('career.license_category')
license_instance_obj = mainInstance.model('career.license_instance')
assessment_obj = mainInstance.model('hr.evaluation.interview')
job_cat_obj = mainInstance.model('career.job_category')
job_pos_obj = mainInstance.model('career.job_position')
question_obj = mainInstance.model('career.question')
question_category_obj = mainInstance.model('career.question_category')
degree_obj = mainInstance.model('hr.recruitment.degree')
country_obj = mainInstance.model('res.country')
province_obj = mainInstance.model('res.country.state')
company_obj = mainInstance.model('res.company')
assignment_obj = mainInstance.model('hr.job')
work_exp_obj = mainInstance.model('career.work_experience')
certificate_obj = mainInstance.model('career.certificate')
edu_hist_obj = mainInstance.model('career.education_history')
document_obj = mainInstance.model('ir.attachment')

conference_member_obj = mainInstance.model('career.conference_member')
company_user_obj = mainInstance.model('career.employer')
user_obj = mainInstance.model('career.employee')
admin_obj = mainInstance.model('res.users')
applicant_obj = mainInstance.model('hr.applicant')

# decorator
def admin_session(func):
    def func_wrapper():
        token = request.values['token']
        session = Session.resume(token, ['admin', 'cc'])
        return func(session)
    return func_wrapper

def employee_session(func):
    def func_wrapper():
        token = request.values['token']
        session = Session.resume(token, ['employee'])
        employee = user_obj.get([('user_id', '=', session.info['uid'])])
        return func(employee)
    return func_wrapper

def employer_session(func):
    def func_wrapper():
        token = request.values['token']
        session = Session.resume(token, ['employer'])
        employer = company_user_obj.get([('user_id', '=', session.info['uid'])])
        return func(employer)
    return func_wrapper

def interview_session(func):
    def func_wrapper():
        inviteCode = request.values['code']
        applicant = applicant_obj.get([('input_token', '=', inviteCode)])
        return func(applicant)
    return func_wrapper

def conference_session(func):
    def func_wrapper():
        meetingId = request.values['meetingId']
        memberId = request.values['memberId']
        member = conference_member_obj.get([('member_id', '=', memberId), ('meeting_id', '=', meetingId)])
        return func(member)
    return func_wrapper