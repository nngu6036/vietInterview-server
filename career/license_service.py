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


class LicenseService(osv.AbstractModel):
    _name = 'career.license_service'

    @api.model
    def validateLicense(self,companyId):
      for company in self.env['res.company'].browse(companyId):
        if not company.license_instance_id.isEnabled()[0]:
          return False
        else:
          return True
      return False

    @api.model
    def activateLicense(self,companyId):
      for company in self.env['res.company'].browse(companyId):
        if company.license_instance_id and company.license_instance_id.expire_date:
          expire_date = datetime.datetime.strptime(company.license_instance_id.expire_date, "%Y-%m-%d")
          if company.license_instance_id.state != 'active' and expire_date < datetime.datetime.now():
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
                              'expireDate':company.license_instance_id.expire_date,'state':company.license_instance_id.state}
      return stats

    @api.model
    def consumeEmail(self,applicantId):
      self.env['hr.applicant'].browse(applicantId)
      for applicant in self.env['hr.applicant'].browse(applicantId):
          license_instance = applicant.company_id.license_instance_id
          if license_instance:
              self.env['career.email.history'].create({'applicant_id':applicantId,'date_send':  fields.Datetime.now(),
                                                        'license_instance_id': license_instance.id})
              email_quota = self.env['career.email.history'].search_count([('license_instance_id','=',license_instance.id)])
              if email_quota >license_instance.license_id.email :
                  self.deactivateLicense(applicant.company_id.id)
      return True
