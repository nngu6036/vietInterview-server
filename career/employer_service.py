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
from datetime import date, timedelta




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
            company.partner_id.write({'email':vals['email']})
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
                                                    'address_id':address.id,'state':'open'} )
            self.env['career.mail_service'].sendNewJobNotification(assignment.id)
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
                           'requirements':a.requirements,'approved':a.state=='recruit',
                           'countryId':a.country_id.id, 'provinceId':a.province_id.id,
                           'createDate':a.create_date,
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
              response['documentList'] = [{'id':doc.id,'title':doc.name,'filename':doc.datas_fname,'filedata':doc.store_fname} for doc in documents]
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

