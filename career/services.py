# -*- coding: utf-8 -*-

from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime
import util

# monkey patching to allow scr not to be remove in html clean
# see openerp.tools.mail.py
import lxml.html.clean as clean
import re
clean._is_javascript_scheme = re.compile(
         r'(?:javascript|jscript|livescript|vbscript|about|mocha):',
         re.I).search
from jinja2.sandbox import SandboxedEnvironment
mako_template_env = SandboxedEnvironment(
    block_start_string="<%",
    block_end_string="%>",
    variable_start_string="${",
    variable_end_string="}",
    comment_start_string="<%doc>",
    comment_end_string="</%doc>",
    line_statement_prefix="%",
    line_comment_prefix="##",
    trim_blocks=True,               # do not output newline after blocks
    lstrip_blocks =True,
    autoescape=True,                # XML/HTML automatic escaping
)
from datetime import date, timedelta


class SessionService(osv.AbstractModel):
    _name = 'career.session_service'

    @api.model
    def login(self,db, account,password,role):
        uid = common.exp_authenticate(db,account,password,{})
        if not uid:
            print ("Invalid username %s or password %s" % (account, password))
            return False
        user = self.env['res.users'].browse(uid)
        if not self.validateUser(user,role):
            return False
        session = self.env['career.session'].create({'uid':user.id,'db':db,'user':account,'password':password})
        return session.token


    @api.model
    def logout(self, token):
        sessions = self.env['career.session'].search([('token', '=', token)])
        sessions.unlink()
        return True


    @api.model
    def validateUser(self,user,role):
          if role == 'admin':
              admin_group = self.env.ref('career.admin_group')
              if admin_group.id in user.groups_id.ids:
                  return True
          if role == 'employer':
              license_service = self.env['career.license_service']
              if not license_service.validateLicense(user.company_id.id):
                print 'License validation error for user ',user
                return False
              employer_group = self.env.ref('career.employer_group')
              if employer_group.id in user.groups_id.ids:
                  return True
          if role == 'employee':
              employee_group = self.env.ref('career.employee_group')
              if employee_group.id in user.groups_id.ids:
                  return True
          return False

    @api.model
    def validateToken(self,token,roles):
        for session in self.env['career.session'].search([('token','=',token)]):
            user = self.env['res.users'].browse(session.uid)
            for role in roles:
                if self.validateUser(user,role):
                  return {'uid':session.uid,'user':session.user,'password':session.password,'db':session.db}
        return False

    @api.model
    def changePass(self,login,oldpass,newpass):
        user = self.env['res.users'].search([('login','=',login)])
        if user.write({'password':newpass}):
            return True
        return False

class AdminService(osv.AbstractModel):
    _name = 'career.admin_service'

    @api.model
    def createEmployee(self,login,password):
        user = self.env['res.users'].search([('login', '=', login)])
        if user:
            print ("Emplyee login %s already exist" % login)
            return False
        employee_group = self.env.ref('career.employee_group')
        hr_group = self.env.ref('base.group_hr_user')
        survey_group = self.env.ref('base.group_survey_user')
        user = self.env['res.users'].create({'login':login,'password':password,'name':login,'notify_email':'none',
                                             'email':login, 'groups_id':[(6,0,[employee_group.id,hr_group.id,survey_group.id])]})
        employee = self.env['career.employee'].create({'user_id':user.id})
        return employee.id


    @api.model
    def createCompany(self,vals):
        license = self.env['career.license'].browse(int(vals['licenseId']))
        expiryDdate = d = date.today() + timedelta(days=license.validity)

        license_instance = self.env['career.license_instance'].create({'license_id':license.id,
                                                                       'expire_date':'%d-%d-%d %d:%d:%d' % (
        expiryDdate.year, expiryDdate.month, expiryDdate.day, expiryDdate.hour, expiryDdate.minute, expiryDdate.second)})
        company = self.env['res.company'].create({'name':vals['name'],'logo':vals['image'] if 'image' in vals else False,'license_instance_id':license_instance.id})
        hr_eval_plan = self.env['hr_evaluation.plan'].create({'name':'Assessment','company_id':company.id})
        assessment_form = self.env.ref('career.assessment_form')
        self.env['hr_evaluation.plan.phase'].create({'name':'Assessment','company_id':company.id,'plan_id':hr_eval_plan.id,
                                                         'action':'final','survey_id':assessment_form.id})
        return company.id

    @api.model
    def updateCompany(self,id,vals):
        company = self.env['res.company'].browse(id)
        if company:
            company.write({'name':vals['name'],'logo':vals['image'] if 'image' in vals else False,'license_instance_id':vals['licenseId']})
            return True
        return False

    @api.model
    def getCompany(self):
        main_compnay = self.env.ref('base.main_company')
        companys = self.env['res.company'].search([('id','!=',main_compnay.id)])
        companyList = [{'id':c.id,'name':c.name,'image':c.logo or False,'licenseId':  c.license_instance_id.license_id.id if c.license_instance_id else False,
                         'licenseExpire': c.expire_date if c.license_instance_id else False} for c in companys]
        return companyList


    @api.model
    def createCompanyUser(self,companyId,vals):
            user = self.env['res.users'].search([('login', '=', vals['email'])])
            if user:
                print ("Emplyer login %s already exist" % vals['email'])
                return False
            employer_group = self.env.ref('career.employer_group')
            hr_group = self.env.ref('base.group_hr_manager')
            survey_group = self.env.ref('base.group_survey_manager')
            admin_group = self.env.ref('base.group_erp_manager')
            company = self.env['res.company'].browse(companyId)
            user = self.env['res.users'].create({'login':vals['email'],'password':vals['password'],'name':vals['name'],'notify_email':'none',
                                                 'email':vals['email']})
            user.write({'company_ids':[(4,company.id)]})
            user.write({'company_id':company.id, 'groups_id':[(6,0,[employer_group.id,hr_group.id,survey_group.id,admin_group.id])]})
            self.env['hr.employee'].create({'address_id':company.partner_id.id,'work_email':vals['email'],'name':vals['name'],
                                           'user_id':user.id,'company_id':company.id})
            new_employer = self.env['career.employer'].create({ 'user_id':user.id,'is_admin':False})
            return new_employer.id


    @api.model
    def updateCompanyUser(self,id,vals):
        employer = self.env['career.employer'].browse(id)
        if employer:
            employer.user_id.write({'name':vals['name']})
            return True
        return False

    @api.model
    def getCompanyUser(self,companyId):
        userList=[]
        for company in  self.env['res.company'].browse(companyId):
          for user in company.user_ids:
            if user.company_id.id == companyId:
              userList.append({'id':user.id,'name':user.name,'email':user.login})
        return userList



    @api.model
    def updateLicense(self,id,vals):
        license = self.env['career.license'].browse(id)
        if license:
            license.write({'name':vals['name'],'email':int(vals['email']),'assignment':int(vals['assignment'])})
            return True
        return False

    @api.model
    def getLicense(self):
        licenses = self.env['career.license'].search([])
        licenseList = [{'id':l.id,'name':l.name,'email':l.email,'assignment':l.assignment} for l in licenses]
        return licenseList


class ContentService(osv.AbstractModel):
    _name = 'career.content_service'

    @api.model
    def getQuestionCategory(self,lang):
        categories = self.env['career.question_category'].search([('lang','=',lang)])
        categoryList = [{'id':c.id,'title':c.title} for c in categories]
        return categoryList

    @api.model
    def getQuestion(self,lang):
        questions = self.env['career.question'].search([('lang','=',lang)])
        questionList = [{'id':q.id,'title':q.title,'content':q.content,'videoUrl':q.videoUrl,'categoryId':q.category_id.id    } for q in questions]
        return questionList

    @api.model
    def getAssessment(self,lang):
        context = {'lang':util.lang_resolver(lang)}
        assessment_form = self.env.ref('career.assessment_form')
        groupList=[]
        questionList = []
        for page in self.env['survey.page'].with_context(context).browse(assessment_form.page_ids.ids):
            groupList.append({'id':page.id,'name':page.title,'order':page.sequence} )
            for question in self.env['survey.question'].with_context(context).browse(page.question_ids.ids):
                questionList.append({'id':question.id,'content':question.question,'groupId':question.page_id.id,
                                 'minVal':question.validation_min_float_value,'maxVal':question.validation_max_float_value} )
        return {'id':assessment_form.id,'groupList':groupList,'questionList':questionList}

    @api.model
    def createQuestionCategory(self,vals):
        category = self.env['career.question_category'].create({'title':vals['title'],'lang':vals['lang']})
        return category.id

    @api.model
    def updateQuestionCategory(self,id,vals):
        category = self.env['career.question_category'].browse(id)
        if category:
            category.write({'title':vals['title']})
            return True
        return False

    @api.model
    def createQuestion(self,vals):
        question = self.env['career.question'].create({'title':vals['title'],'content':vals['content'],'videoUrl':vals['videoUrl'],
                                                       'categoryId':int(vals['categoryId']),'lang':vals['lang']})
        return question.id

    @api.model
    def updateQuestion(self,id,vals):
        question = self.env['career.question'].browse(id)
        if question:
            question.write({'title':vals['title'],'content':vals['content'],'videoUrl':vals['videoUrl'],
                                                       'categoryId':int(vals['categoryId'])})
            return True
        return False



class EmployerService(osv.AbstractModel):
    _name = 'career.employer_service'

    @api.model
    def getCompany(self):
        cr, uid, context = self.env.args
        users = self.env['res.users'].browse(uid)
        if users:
            return {'id': users[0].company_id.id,'name': users[0].company_id.name,'image': users[0].company_id.logo or False}
        return False

    @api.model
    def updateCompany(self,id,vals):
        company = self.env['res.company'].browse(id)
        if company:
            company.write({'name':vals['name'],'logo':vals['image'] if 'image' in vals else False})
            return True
        return False


    @api.model
    def createAssignment(self,vals):
        company = self.getCompany()
        if company:
            address = self.env['res.partner'].create({'name':vals['name'],'type':'contact',
                                                      'country_id':'countryId' in vals and int(vals['countryId']) ,
                                                    'state_id':'provinceId' in vals and int(vals['provinceId']),
                                                      'company_id':company['id']})
            assignment = self.env['hr.job'].create({'name':vals['name'],'description':vals['description'],
                                                    'deadline':vals['deadline'], 'company_id':company['id'],
                                                    'requirements':vals['requirements'] or False,
                                                    'category_id':'categoryId' in vals and int(vals['categoryId']) ,
                                                    'position_id':'positionId' in vals and int(vals['positionId']) ,
                                                    'address_id':address.id} )
            return assignment.id
        return False

    @api.model
    def updateAssignment(self,id,vals):
        assignment = self.env['hr.job'].browse(id)
        if assignment:
            assignment.write({'deadline':vals['deadline'],'description':vals['description'],'name':vals['name'],
                              'requirements':vals['requirements'],
                              'category_id':int(vals['categoryId']) or False,'position_id':int(vals['positionId']) or False})
            assignment.address_id.write({'country_id':int(vals['countryId']) or False,'state_id':int(vals['provinceId']) or False})
            return True
        return False

    @api.model
    def getAssignment(self):
        company = self.getCompany()
        assignments = self.env['hr.job'].search([('company_id','=',company['id'])])
        assignmentList = [{'id':a.id,'name':a.name,'description':a.description,'deadline':a.deadline,'status':a.status,
                           'requirements':a.requirements,
                           'countryId':a.country_id.id, 'provinceId':a.province_id.id,
                           'categoryId':a.category_id.id, 'positionId':a.position_id.id} for a in assignments]
        return assignmentList

    @api.model
    def openAssignment(self,id):
        assignment = self.env['hr.job'].browse(id)
        if assignment:
            assignment.write({'status':'published'})
            return True
        return False

    @api.model
    def closeAssignment(self,id):
        assignment = self.env['hr.job'].browse(id)
        if assignment:
            assignment.write({'status':'closed'})
            return True
        return False

    @api.model
    def deleteAssignment(self,id):
        for assignment in self.env['hr.job'].browse(id):
          if assignment.status =='initial':
            assignment.unlink()
            return True
        return False

    @api.model
    def getAssignmentCandidate(self,assignmentId):
        applicants = self.env['hr.applicant'].search([('job_id','=',assignmentId)])
        candidateList = [{'id':a.id,'name':a.name,'email':a.email_from,
                          'invited':True if self.env['career.email.history'].search([('assignment_id','=',assignmentId),
                                                                                     ('email','=',a.email_from)]) else False }
                            for a in applicants]

        return candidateList



    @api.model
    def createInterview(self,assignmentId,vals):
        assignment = self.env['hr.job'].browse(assignmentId)
        interview = self.env['survey.survey'].create({'title':vals['name'],'response':int(vals['response']),
                                                              'retry':int(vals['retry']) if 'retry' in vals else False
                                                         , 'introUrl':vals['introUrl'],
                                                             'exitUrl':vals['exitUrl'],'aboutUsUrl':vals['aboutUsUrl'],
                                                             'prepare':int(vals['prepare']) if 'prepare' in vals else False,
                                                             'language':vals['language'] if 'language' in vals else False })
        assignment.write({'survey_id':interview.id})
        return interview.id

    @api.model
    def updateInterview(self,id,vals):
        interview = self.env['survey.survey'].browse(id)
        if interview:
            interview.write({ 'title':vals['name'],'response':int(vals['response']),
                                'retry':int(vals['retry']) if 'retry' in vals else False,
                              'introUrl':vals['introUrl'],
                               'exitUrl':vals['exitUrl'],'aboutUsUrl':vals['aboutUsUrl'],
                              'prepare':int(vals['prepare']) if 'prepare' in vals else False,
                              'language':vals['language'] if 'language' in vals else False})
            return True
        return False

    @api.model
    def getInterview(self,assignmentId):
        assignment = self.env['hr.job'].browse(assignmentId)
        if assignment.survey_id:
            interview = {'id':assignment.survey_id.id,'name':assignment.survey_id.title,'response':assignment.survey_id.response,
                          'retry':assignment.survey_id.retry,'introUrl':assignment.survey_id.introUrl,'exitUrl':assignment.survey_id.exitUrl,
                         'aboutUsUrl':assignment.survey_id.aboutUsUrl,'language':assignment.survey_id.language,'prepare':assignment.survey_id.prepare}
            return interview
        return False

    @api.model
    def addInterviewQuestion(self,interviewId,jQuestions):
        questionIds =[]
        for jQuestion in jQuestions:
            page = self.env['survey.page'].create({'title':'Single Page','survey_id':interviewId})
            question = self.env['survey.question'].create({'question':jQuestion['title'],'response':int(jQuestion['response']),
                                                                  'retry':int(jQuestion['retry']) if 'retry' in jQuestions else False,
                                                                'videoUrl':jQuestion['videoUrl'],
                                                                'prepare':int(jQuestion['prepare']) if 'prepare' in jQuestion else False,
                                                                 'source':jQuestion['source'],'mode':jQuestion['type'],'page_id':page.id,
                                                                'sequence':int(jQuestion['order']),'survey_id':interviewId})
            questionIds.append(question.id)
        return questionIds

    @api.model
    def updateInterviewQuestion(self,jQuestions):
        for jQuestion in jQuestions:
            self.env['survey.question'].browse(int(jQuestion['id'])).write({'question':jQuestion['title'],'response':int(jQuestion['response']),
                                                                 'retry':int(jQuestion['retry']) if 'retry' in jQuestions else False,
                                                                'videoUrl':jQuestion['videoUrl'],
                                                                'prepare':int(jQuestion['prepare']) if 'prepare' in jQuestion else False,
                                                                 'source':jQuestion['source'],'mode':jQuestion['type'],
                                                                'sequence':int(jQuestion['order'])})
        return True

    @api.model
    def removeInterviewQuestion(self,jQuestionIds):
        for qId in jQuestionIds:
            question = self.env['survey.question'].browse(int(qId))
            question.page_id.unlink()
            question.unlink()
        return True

    @api.model
    def getInterviewQuestion(self,interviewId):
        questions = self.env['survey.question'].search([('survey_id','=',interviewId)])
        questionList = [{'id':q.id,'title':q.question,'response':q.response,'retry':q.retry,'videoUrl':q.videoUrl,
                         'source':q.source,'type':q.mode,'order':q.sequence,'prepare':q.prepare} for q in questions]
        return questionList

    @api.model
    def getInterviewResponse(self,interviewId):
        responseList = []
        for input in self.env['survey.user_input'].search([('survey_id','=',interviewId)]):
            for applicant in self.env['hr.applicant'].search([('email_from','=',input.email),('response_id','=',input.id)]):
              response = {'name':input.email,'email':input.email,'candidateId':applicant[0].id}
              response['answerList'] = [{'id':line.id,'questionId':line.question_id.id,'videoUrl':line.value_video_url} for line in input.user_input_line_ids]
              documents = self.env['ir.attachment'].search([('res_model','=','hr.applicant'),('res_id','=',applicant[0].id)])
              response['documentList'] = [{'id':doc.id,'title':doc.name,'filename':doc.datas_fname,'filedata':doc.datas} for doc in documents]
              responseList.append(response)
        return responseList


    @api.model
    def submitAssessment(self,assessmentResult):
        cr, uid, context = self.env.args
        company = self.getCompany()
        employees = self.env['hr.employee'].search([('user_id','=',uid)])
        hr_interview_assessment =  self.env['hr.evaluation.interview'].search([('user_id','=',uid),('applicant_id','=',int(assessmentResult['candidateId']))])
        if not hr_interview_assessment:
          hr_eval_phase = self.env['hr_evaluation.plan.phase'].search([('company_id','=',company['id'])])
          hr_eval = self.env['hr_evaluation.evaluation'].create({'employee_id':employees[0].id,
                                                                       'plan_id':hr_eval_phase.plan_id.id,'state':'progress'})
          hr_interview_assessment = self.env['hr.evaluation.interview'].create({'evaluation_id':hr_eval.id,'phase_id':hr_eval_phase.id,
                                                            'applicant_id':int(assessmentResult['candidateId']),'state':'done','user_id':uid})
        hr_interview_assessment.write({'rating':int(assessmentResult['vote']),'note_summary':assessmentResult['comment']})
        for jAns in assessmentResult['answerList']:
          if not self.env['survey.user_input_line'].search([('user_input_id','=',hr_interview_assessment[0].request_id.id),('question_id','=',int(jAns['questionId']))]):
            self.env['survey.user_input_line'].create({'user_input_id':hr_interview_assessment[0].request_id.id,
                                                                    'question_id':int(jAns['questionId']),
                                                                    'answer_type':'number',
                                                                    'value_number':int(jAns['answer'])})
        return hr_interview_assessment.id

    @api.model
    def getSelfAssessment(self,assessmentId,applicantId):
        cr, uid, context = self.env.args
        hr_interview_assessment =  self.env['hr.evaluation.interview'].search([('applicant_id','=',applicantId),('user_id','=',uid)])
        answerList=[{'id':answer.id,'questionId':answer.question_id.id,'answer':answer.value_number} for answer in hr_interview_assessment.request_id.user_input_line_ids]
        return {'id':hr_interview_assessment.id,'comment':hr_interview_assessment.note_summary,
                'vote':hr_interview_assessment.rating,'answerList':answerList}

    @api.model
    def getOtherAssessment(self,assessmentId,applicantId):
        cr, uid, context = self.env.args
        assessmentResultList = []
        for hr_interview_assessment in self.env['hr.evaluation.interview'].search([('applicant_id','=',applicantId),('user_id','!=',uid)]):
            assessmentResultList.append({'answertList': [{'id':answer.id,'questionId':answer.question_id.id,'answer':answer.value_number}
                                                 for answer in hr_interview_assessment.request_id.user_input_line_ids ],
                                   'id':hr_interview_assessment.id,'comment':hr_interview_assessment.note_summary,
                                    'vote':hr_interview_assessment.rating,
                                    'user':hr_interview_assessment.user_id.name})
        return assessmentResultList

    @api.model
    def getAassignmentStatistic(self,assignmentId):
      assignment = self.env['hr.job'].browse(assignmentId)
      applicant_count = assignment.application_count
      invite_count = self.env['career.email.history'].search_count([('assignment_id','=',assignmentId)])
      response_count = self.env['survey.user_input'].search_count([('survey_id','=',assignment.survey_id.id),('state','=','done')])
      return {'applicant':applicant_count,'invitation':invite_count,'response':response_count}


class CandidateService(osv.AbstractModel):
    _name = 'career.guest_service'

    @api.model
    def getInterview(self,invite_code):
        user_input = self.env['survey.user_input'].search([('token','=',invite_code)])
        if user_input:
            interview = user_input[0].survey_id
            return {'id':interview.id,'name':interview.title,'response':interview.response,'prepare':interview.prepare,
                              'retry':interview.retry,'introUrl':interview.introUrl,'exitUrl':interview.exitUrl,
                             'aboutUsUrl':interview.aboutUsUrl}
        return False

    @api.model
    def getCandidate(self,invite_code):
        user_input = self.env['survey.user_input'].search([('token','=',invite_code)])
        if user_input:
            for applicant in self.env['hr.applicant'].search([('email_from','=',user_input[0].email)]):
                return {'id':applicant.id,'name':applicant.name,'email':applicant.email_from}
        return False

    @api.model
    def getInterviewHistory(self,invite_code):
        user_input = self.env['survey.user_input'].search([('token','=',invite_code)])
        if user_input:
            return {'id':user_input.id,'state':user_input.state,'deadline':user_input.deadline,
                              'wrap_up':user_input.wrap_up}
        return False

    @api.model
    def getInterviewQuestion(self,invite_code):
        user_input = self.env['survey.user_input'].search([('token','=',invite_code)])
        if user_input:
            interview = user_input[0].survey_id
            questions = self.env['survey.question'].search([('survey_id','=',interview.id)])
            questionList = [{'id':q.id,'title':q.question,'response':q.response,'retry':q.retry,'prepare':q.prepare,'videoUrl':q.videoUrl,
                             'source':q.source,'type':q.mode,'order':q.sequence} for q in questions]
            return questionList
        return False

    @api.model
    def startInterview(self,invite_code):
        user_input = self.env['survey.user_input'].search([('token','=',invite_code)])
        if user_input and user_input[0].state=='new':
            user_input.write({'state':'skip'})
            return True
        return False

    @api.model
    def stopInterview(self,invite_code):
        user_input = self.env['survey.user_input'].search([('token','=',invite_code)])
        if user_input and (user_input[0].state=='new' or user_input[0].state=='skip'):
            user_input.write({'state':'done'})
            self.env['career.mail_service'].sendInterviewThankyou(user_input.survey_id.id,user_input[0].email)
            return True
        return False

    @api.model
    def submitInterviewAnswer(self,invite_code,questionId,videoUrl):
        user_input = self.env['survey.user_input'].search([('token','=',invite_code)])
        if user_input[0].state=='skip':
            user_input.write({'state':'skip'})
            input_line = self.env['survey.user_input_line'].create({'user_input_id':user_input[0].id,'question_id':questionId,
                                                                    'skipped':False,
                                                                    'answer_type':'url',
                                                                    'value_video_url':videoUrl})
            return True
        return False

    @api.model
    def attachDocument(self,invite_code,file_name,file_location,comment):
        user_input = self.env['survey.user_input'].search([('token','=',invite_code)])
        if user_input:
            applicants = self.env['hr.applicant'].search([('email_from','=',user_input[0].email)])
            if applicants:
                applicant = applicants[0]
                assignment = applicant.job_id
                if assignment and assignment.status=='published' and  assignment.survey_id:
                     self.env['ir.attachment'].create({'name':file_name,'description':comment,
                                                       'res_model':'hr.applicant','res_id':applicant[0].id,
                                                       'company_id':assignment.company_id.id,'type':'binary',
                                                       'store_fname':file_location,'datas_fname':file_name})
                     return True
        return False

class MailService(osv.AbstractModel):
    _name = 'career.mail_service'

    @api.model
    def sendInterviewInvitation(self,inteviewId,emails,subject):
        cr, uid, context = self.env.args
        assignments = self.env['hr.job'].search([('survey_id','=',inteviewId)])
        if not assignments or assignments[0].status !='published':
            return False
        assignment =  assignments[0]
        interview = self.env['survey.survey'].browse(inteviewId)
        if not interview:
          return False
        lang = util.lang_resolver(interview[0].language)
        email_template = self.env.ref('career.invitation_email_template')
        if not email_template:
            return False
        email_template.write({'subject':subject})
        license_service = self.env['career.license_service']
        for email in emails:
            if not license_service.validateLicense(assignment.company_id.id):
              print "License error ", assignment.company_id.name
              return False
            user_input = self.env['survey.user_input'].search([('email','=',email),('survey_id','=',inteviewId)])
            if not user_input:
                user_input = self.env['survey.user_input'].create({'survey_id':inteviewId,'deadline':assignment.deadline,
                                                                   'type':'link','state':'new','email':email})
            candidate = self.env['hr.applicant'].search([('email_from','=',email),('job_id','=',assignment.id)])
            if not candidate:
                candidate = self.env['hr.applicant'].create({'name':email,'email_from':email,'job_id':assignment.id,
                                                             'company_id':assignment.company_id.id,'response_id':user_input.id})
            self.pool.get('email.template').send_mail(cr, uid, email_template.id, candidate.id, True,False,{'lang':lang})
            license_service.consumeEmail(candidate.id)
        return True


    @api.model
    def sendInterviewThankyou(self,inteviewId,email):
        cr, uid, context = self.env.args
        assignments = self.env['hr.job'].search([('survey_id','=',inteviewId)])
        assignment =  assignments[0]
        interview = self.env['survey.survey'].browse(inteviewId)
        if not interview:
          return False
        lang = util.lang_resolver(interview[0].language)
        email_template = self.env.ref('career.thankyou_email_template')
        if not email_template:
            return False
        candidate = self.env['hr.applicant'].search([('email_from','=',email),('job_id','=',assignment.id)])
        if not candidate:
            return False
        self.pool.get('email.template').send_mail(cr, uid, email_template.id, candidate.id, True,False,{'lang':lang})
        return True

class CommonService(osv.AbstractModel):
    _name = 'career.common_service'

    @api.model
    def getCompanyInfo(self,assignmentId):
        assignments = self.env['hr.job'].browse(assignmentId)
        for assignment in assignments:
            return {'id': assignment.company_id.id,'name': assignment.company_id.name,'image': assignment.company_id.logo or False}
        return False

    @api.model
    def getCountry(self):
        countries = self.env['res.country'].search([])
        countryList = [{'id':c.id,'title':c.name} for c in countries]
        return countryList

    @api.model
    def getProvince(self):
        states = self.env['res.country.state'].search([])
        provinceList = [{'id':s.id,'title':s.name,'countryId':s.country_id.id} for s in states]
        return provinceList

    @api.model
    def getJobCategory(self,lang):
        lang = util.lang_resolver(lang)
        context = {'lang':lang}
        categories = self.env['career.job_category'].with_context(context).search([])
        categoryList = [{'id':c.id,'title':c.title} for c in categories]
        return categoryList

    @api.model
    def getJobPosition(self,lang):
        lang = util.lang_resolver(lang)
        context = {'lang':lang}
        positions = self.env['career.job_position'].with_context(context).search([])
        positionList = [{'id':p.id,'title':p.title} for p in positions]
        return positionList

    @api.model
    def getEducationLevel(self,lang):
        lang = util.lang_resolver(lang)
        context = {'lang':lang}
        levels = self.env['hr.recruitment.degree'].with_context(context).search([])
        levelList = [{'id':l.id,'title':l.name} for l in levels]
        return levelList

    @api.model
    def searchJob(self,keyword,options):
        domain = [('status','=','published')]
        if options:
            if options['countryId']:
                domain.append(('country_id','=',int(options['countryId'])))
            if options['provinceId']:
                domain.append(('province_id','=',int(options['provinceId'])))
            if options['categoryId']:
                domain.append(('category_id','=',int(options['categoryId'])))
            if options['positionId']:
                domain.append(('position_id','=',int(options['positionId'])))

        if keyword:
            domain.append('|')
            domain.append(('description','like',keyword))
            domain.append(('name','like',keyword))

        assignments = self.env['hr.job'].search(domain)
        assignmentList = [{'id':a.id,'name':a.name,'description':a.description,'deadline':a.deadline,'status':a.status,
                           'countryId':a.country_id.id, 'provinceId':a.province_id.id,'requirements':a.requirements,
                           'categoryId':a.category_id.id, 'positionId':a.position_id.id} for a in assignments]
        return assignmentList

    @api.model
    def applyJob(self,uid,assignmentId):
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        assignments = self.env['hr.job'].browse(assignmentId)
        for employee in employees:
            for assignment in assignments:
                if assignment.isEnabled():
                    user_input = self.env['survey.user_input'].search([('email','=',employee.login),('survey_id','=',assignment.survey_id.id)])
                    if not user_input:
                        user_input = self.env['survey.user_input'].create({'survey_id':assignment.survey_id.id,'deadline':assignment.deadline,
                                                                           'type':'link','state':'new','email':employee.login})
                    candidate = self.env['hr.applicant'].search([('email_from','=',employee.login),('job_id','=',assignment.id)])
                    if not candidate:
                        self.env['hr.applicant'].create({'name':employee.name,'email_from':employee.login,'job_id':assignment.id,
                                                                     'company_id':assignment.company_id.id,'response_id':user_input.id})
                    return True
        return False



class EmployeeService(osv.AbstractModel):
    _name = 'career.employee_service'


    @api.model
    def getUserProfile(self):
        cr, uid, context = self.env.args
        users = self.env['res.users'].browse(uid)
        if users:
            user = users[0]
            return {'id':user.partner_id.id, 'name':user.partner_id.name,'phone':user.partner_id.phone,'mobile':user.partner_id.mobile,
                    'email':user.partner_id.email,'address':user.partner_id.street, 'countryId':user.partner_id.country_id.id,
                    'provinceId':user.partner_id.state_id.id}
        return False

    @api.model
    def updateUserProfile(self,vals):
        cr, uid, context = self.env.args
        users = self.env['res.users'].browse(uid)
        if users:
            users.partner_id.write({'name':vals['name'],'phone':vals['phone'],'mobile':vals['mobile'],
                    'email':vals['email'],'street':vals['address'], 'country_id':vals['countryId'],
                     'state_id':vals['provinceId']})
        return True

    @api.model
    def getWorkExperience(self):
        cr, uid, context = self.env.args
        expList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            for exp in employee.experience_ids:
                expList.append({'id':exp.id,'title':exp.title,'employer':exp.employer,'startDate':exp.start_date,'endDate':exp.end_date,
                                'current':exp.current,'leaveReason':exp.leave_reason,'countryId':exp.country_id.id,'provinceId':exp.province_id.id,
                                'description':exp.description})
        return expList

    @api.model
    def addWorkExperience(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            exp = self.env['career.work_experience'].create({'title':vals['title'],'employer':vals['employer'],
                                                             'start_date':'startDate' in vals and vals['startDate'],
                                                             'description':vals['description'],
                                                            'end_date':'endDate' in vals and vals['endDate'],'current':vals['current'],'leave_reason':vals['leaveReason'],
                                                             'country_id':'countryId' in vals and int(vals['countryId']),
                                                             'province_id':'provinceId' in vals and int(vals['provinceId']),
                                                             'employee_id':employee.id})
            return exp.id
        return False

    @api.model
    def updateWorkExperience(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.work_experience'].browse(int(vals['id'])).write({'title':vals['title'],'employer':vals['employer'],'start_date':vals['startDate'],
                                                            'end_date':vals['endDate'],'current':vals['current'],'leave_reason':vals['leaveReason'],
                                                             'country_id':int(vals['countryId']),'province_id':int(vals['provinceId']),
                                                             'employee_id':employee.id,'description':vals['description']})
            return True
        return False

    @api.model
    def removeWorkExperience(self,ids):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.work_experience'].browse(ids).unlink()
        return True



    @api.model
    def getEducationHistory(self):
        cr, uid, context = self.env.args
        eduList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            for edu in employee.education_ids:
                eduList.append({'id':edu.id,'program':edu.program,'institute':edu.institute,'finishDate':edu.complete_date,
                                'status':edu.status,'levelId':edu.level_id.id})
        return eduList

    @api.model
    def addEducationHistory(self,vals):
        cr, uid, context = self.env.args
        for employee in  self.env['career.employee'].search([('user_id','=',uid)]):
            edu = self.env['career.education_history'].create({'program':vals['program'],'institute':vals['institute'],
                                                            'complete_date':vals['finishDate'],'status':vals['status'],
                                                             'level_id':int(vals['levelId']),'employee_id':employee.id})
            return edu.id
        return False

    @api.model
    def updateEducationHistory(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.education_history'].browse(int(vals['id'])).write({'program':vals['program'],'institute':vals['institute'],
                                                            'complete_date':vals['finishDate'],'status':vals['status'],
                                                             'level_id':int(vals['levelId'])})
            return True
        return False

    @api.model
    def removeEducationHistory(self,ids):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.education_history'].browse(ids).unlink()
        return True

    @api.model
    def getCertificate(self):
        cr, uid, context = self.env.args
        certList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            for cert in employee.certificate_ids:
                certList.append({'id':cert.id,'title':cert.title,'issuer':cert.issuer,'issueDate':cert.issue_date})
        return certList

    @api.model
    def addCertificate(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            cert = self.env['career.certificate'].create({'title':vals['title'],'issuer':vals['issuer'],
                                                            'issue_date':vals['issueDate'],'employee_id':employee.id})
            return cert.id
        return False

    @api.model
    def updateCertificate(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.certificate'].browse(int(vals['id'])).write({'title':vals['title'],'issuer':vals['issuer'],
                                                            'issue_date':vals['issueDate']})
            return True
        return False

    @api.model
    def removeCertificate(self,ids):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.certificate'].browse(ids).unlink()
        return True

    @api.model
    def getDocument(self):
        cr, uid, context = self.env.args
        certList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            documents = self.env['ir.attachment'].search([('res_model','=','career.employee'),('res_id','=',employee.id)])
            for doc in documents:
                certList.append({'id':doc.id,'title':doc.name,'filename':doc.datas_fname,'filedata':doc.datas})
        return certList

    @api.model
    def addDocument(self,title,filename,file_location):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            doc = self.env['ir.attachment'].create({'name':title,'description':title,'res_model':'career.employee','res_id':employee.id,
                                                       'type':'binary','store_fname':file_location,'datas_fname':filename})
            return doc.id
        return False

    @api.model
    def removeDocument(self,ids):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['ir.attachment'].browse(ids).unlink()


    @api.model
    def getApplicantHistory(self):
        cr, uid, context = self.env.args
        applicationList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            applicants = self.env['hr.applicant'].search([('email_from','=',employee.login)])
            for applicant in applicants:
                interview_link = False
                if applicant.response_id:
                    interview_link = "https://vietinterview.com/interview?code=%s&" % applicant.response_id.token
                applicationList.append({'id':applicant.id,'title':applicant.job_id.name,'company':applicant.job_id.comopany_id.name,
                                       'deadline':applicant.job_id.deadline,'applyDate':applicant.create_date,'interview_link':interview_link})
        return applicationList


class ReportService(osv.AbstractModel):
    _name = 'career.report_service'

    @api.model
    def getAssessmentSummaryReport(self,candidateId):
      applicant = self.env['hr.applicant'].browse(candidateId)
      content_pdf = self.env['report'].get_pdf(applicant, 'career.report_assessment_summary')
      encoded_content = base64.b64encode(content_pdf)
      return encoded_content

class LicenseService(osv.AbstractModel):
    _name = 'career.license_service'

    @api.model
    def validateLicense(self,companyId):
      for company in self.env['res.company'].browse(companyId):
        if not company.license_instance_id.isEnabled():
          return False
      return True

    @api.model
    def activateLicense(self,companyId):
      for company in self.env['res.company'].browse(companyId):
        if company.license_instance_id and company.license_instance_id.expire_date:
          expire_date = datetime.datetime.strptime(company.license_instance_id.expire_date, "%Y-%m-%d")
          if company.license_instance_id.state != 'active' and expire_date > datetime.datetime.now():
            return False
          company.license_instance_id.write({'state':'active'})
          return True
      return False

    @api.model
    def deactivateLicense(self,companyId):
      for company in self.env['res.company'].browse(companyId):
        if company.license_instance_id:
          company.license_instance_id.write({'state':'suspend'})
          return True
      return False

    @api.model
    def getLicenseStatistic(self,companyId):
      stats = {'email':0,'license':None}
      for company in self.env['res.company'].browse(companyId):
        if company.license_instance_id:
          stats['email'] = self.env['career.email.history'].search_count([('license_instance_id','=',company.license_instance_id.id)])
          stats['license'] = {'name':company.license_instance_id.license_id.name,'email':company.license_instance_id.license_id.email,
                              'expire_date':company.license_instance_id.expire_date,'state':company.license_instance_id.state}
      return stats

    @api.model
    def consumeEmail(self,applicantId,data_send=False):
      cr, uid, context = self.env.args
      for employer in self.env['career.employer'].search([('user_id','=',uid)]):
          license_instance = employer.user_id.company_id.license_instance_id
          self.env['career.email.history'].create({'applicant_id':applicantId,'date_send': data_send or fields.Datetime.now(),
                                               'employer_id':employer.id,'license_instance_id':license_instance and license_instance.id})
          email_quota = self.env['career.email.history'].search_count([('license_instance_id','=',license_instance.id)])
          if email_quota >=license_instance.license_id.email :
              self.deactivateLicense(employer.user_id.company_id.id)
      return True
