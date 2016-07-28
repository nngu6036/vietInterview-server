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