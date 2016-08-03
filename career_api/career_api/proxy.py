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
interview_service = mainInstance.model('career.interview_service')
license_service = mainInstance.model('career.license_service')
mail_service = mainInstance.model('career.mail_service')
report_service = mainInstance.model('career.report_service')
assessment_obj = mainInstance.model('hr.evaluation.interview')
job_cat_obj = mainInstance.model('career.job_category')
job_pos_obj = mainInstance.model('career.job_position')
assignment_obj = mainInstance.model('hr.job')
license_obj = mainInstance.model('career.license')
license_instance_obj = mainInstance.model('career.license_instance')
company_obj = mainInstance.model('res.company')
company_user_obj = mainInstance.model('career.employer')
user_obj = mainInstance.model('career.employee')
work_exp_obj = mainInstance.model('career.work_experience')
edu_hist_obj = mainInstance.model('career.education_history')
certificate_obj = mainInstance.model('career.certificate')
document_obj = mainInstance.model('ir.attachment')
applicant_obj = mainInstance.model('hr.applicant')
interview_obj = mainInstance.model('survey.survey')
interview_question_obj = mainInstance.model('survey.question')
interview_history_obj = mainInstance.model('survey.user_input')
interview_answer_obj = mainInstance.model('survey.user_input_line')
question_obj = mainInstance.model('career.question')
question_category_obj = mainInstance.model('career.question_category')
account_obj = mainInstance.model('res.users')
degree_obj = mainInstance.model('hr.recruitment.degree')
country_obj = mainInstance.model('res.country')
province_obj = mainInstance.model('res.country.state')

# decorator
def admin_session(func):
    def func_wrapper():
        token = request.values['token']
        session = Session.resume(token, ['admin'])
        return func(session)
    return func_wrapper

def employee_session(func):
    def func_wrapper():
        token = request.values['token']
        session = Session.resume(token, ['employee'])
        return func(session)
    return func_wrapper

def employer_session(func):
    def func_wrapper():
        token = request.values['token']
        session = Session.resume(token, ['employer'])
        return func(session)
    return func_wrapper

def interview_session(func):
    def func_wrapper():
        inviteCode = request.values['code']
        return func(inviteCode)
    return func_wrapper