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
                     self.env['ir.attachment'].create({'name':comment,'description':comment,
                                                       'res_model':'hr.applicant','res_id':applicant[0].id,
                                                       'company_id':assignment.company_id.id,'type':'binary',
                                                       'store_fname':file_location,'datas_fname':file_name})
                     return True
        return False