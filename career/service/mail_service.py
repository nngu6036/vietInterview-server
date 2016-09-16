# -*- coding: utf-8 -*-

from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime
from .. import util
# monkey patching to allow scr not to be remove in html clean
# see openerp.tools.mail.py
import lxml.html.clean as clean
from datetime import date, timedelta



class MailService(osv.AbstractModel):
    _name = 'career.mail_service'


    @api.model
    def sendVideoInterviewInvitation(self,candidate,subject):
        cr, uid, context = self.env.args
        interview = candidate.interview_id
        lang = util.lang_resolver(interview.language)
        email_template = self.env.ref('career.interview_invitation_email_template')
        if not email_template:
            return False
        email_template.write({'subject':subject})
        license_service = self.env['career.license_service']
        if not license_service.validateLicense(candidate.company_id.id):
            print "License error ", candidate.company_id.name
            return False
        self.pool.get('email.template').send_mail(cr, uid, email_template.id, candidate.id, True,False,{'lang':lang})
        license_service.consumeEmail(candidate.id)
        return True


    @api.model
    def sendConferenceInvitation(self,candidate,subject):
        cr, uid, context = self.env.args
        interview = candidate.interview_id
        lang = util.lang_resolver(interview[0].language)
        email_template = self.env.ref('career.conference_invitation_email_template')
        if not email_template:
            return False
        email_template.write({'subject':subject})
        license_service = self.env['career.license_service']
        if not license_service.validateLicense(candidate.company_id.id):
            print "License error ", candidate.company_id.name
            return False
        for conference in self.env['career.conference'].search([('interview_id','=',candidate.interview_id.id),('applicant_id','=',candidate.id)]):
            for member in conference.member_ids:
                if member.role=='candidate':
                    self.pool.get('email.template').send_mail(cr, uid, email_template.id, member.id, True,False,{'lang':lang})
        license_service.consumeEmail(candidate.id)
        return True



    @api.model
    def sendInterviewThankyou(self,inteviewId,email):
        cr, uid, context = self.env.args
        for interview in self.env['survey.survey'].browse(inteviewId):
            lang = util.lang_resolver(interview[0].language)
            email_template = self.env.ref('career.interview_thankyou_email_template')
            if not email_template:
                return False
            candidate = self.env['hr.applicant'].search([('email_from','=',email),('interview_id','=',inteviewId)])
            if not candidate:
                return False
            self.pool.get('email.template').send_mail(cr, uid, email_template.id, candidate.id, True,False,{'lang':lang})
        return True


    @api.model
    def sendNewJobNotification(self,assignmentId):
        cr, uid, context = self.env.args
        email_template = self.env.ref('career.new_job_notification_email_template')
        if not email_template:
            return False
        self.pool.get('email.template').send_mail(cr, uid, email_template.id, assignmentId, True,False,)
        return True

    @api.model
    def sendJobApprovalNotification(self,assignmentId):
        cr, uid, context = self.env.args
        email_template = self.env.ref('career.job_approval_notification_email_template')
        if not email_template:
            return False
        self.pool.get('email.template').send_mail(cr, uid, email_template.id, assignmentId, True,False,)
        return True

    @api.model
    def sendResetPasswordInstructionMail(self, email):
        cr, uid, context = self.env.args
        otk = self.env['career.otk'].create({'email': email})
        template = self.env.ref('career.reset_pass_email_template')
        return self.pool.get('email.template').send_mail(cr, uid, template.id, otk.id, True)

    @api.model
    def sendJobApplyLetter(self, applicantId):
        cr, uid, context = self.env.args
        email_template = self.env.ref('career.job_cover_letter_email_template')
        if not email_template:
            return False
        self.pool.get('email.template').send_mail(cr, uid, email_template.id, applicantId, True, False, )
        return True