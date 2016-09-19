# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime

# monkey patching to allow scr not to be remove in html clean
# see openerp.tools.mail.py
import lxml.html.clean as clean
from datetime import date, timedelta


class LicenseService(osv.AbstractModel):
    _name = 'career.license_service'

    @api.model
    def validateLicense(self, companyId):
        for company in self.env['res.company'].browse(companyId):
            if not company.license_instance_id.isEnabled():
                return False
            else:
                return True
        return False

    @api.model
    def activateLicense(self, companyId):
        for company in self.env['res.company'].browse(companyId):
            if company.license_instance_id and company.license_instance_id.expire_date:
                expire_date = datetime.datetime.strptime(company.license_instance_id.expire_date, "%Y-%m-%d")
                if company.license_instance_id.state != 'active' and expire_date < datetime.datetime.now():
                    return False
                company.license_instance_id.write({'state': 'active'})
                return True
        return False

    @api.model
    def deactivateLicense(self, companyId):
        for company in self.env['res.company'].browse(companyId):
            if company.license_instance_id:
                company.license_instance_id.write({'state': 'suspend'})
                return True
        return False

    @api.model
    def consumeEmail(self, applicantId):
        self.env['hr.applicant'].browse(applicantId)
        for applicant in self.env['hr.applicant'].browse(applicantId):
            license_instance = applicant.company_id.license_instance_id
            if license_instance:
                self.env['career.email.history'].create(
                    {'applicant_id': applicantId, 'date_send': fields.Datetime.now(),
                     'license_instance_id': license_instance.id})
                email_quota = self.env['career.email.history'].search_count(
                    [('license_instance_id', '=', license_instance.id)])
                if email_quota > license_instance.license_id.email:
                    self.deactivateLicense(applicant.company_id.id)
        return True

    @api.model
    def consumeEmployee(self, companyId, employerId,employeeId):
        cost = 1
        employee_quota = 0
        for company in self.env['res.company'].browse(companyId):
            license_instance = company.license_instance_id
            if license_instance:
                for employee in self.env['career.employee'].browse(employeeId):
                    for exp in employee.experience_ids.sorted(key=lambda r: r.start_date):
                        for license_rule in license_instance.license_id.rule_ids:
                            if license_rule.position_id.id == exp.position_id.id:
                                if license_rule.cost > cost:
                                    cost = license_rule.cost
                self.env['career.employee.history'].create({'employee_id': employeeId,
                     'cost': cost,'employer_id':employerId,
                     'license_instance_id': license_instance.id})
                for employeeHistory in self.env['career.employee.history'].search(
                        [('license_instance_id', '=', license_instance.id)]):
                    employee_quota += employeeHistory.cost
                if employee_quota > license_instance.license_id.point:
                    self.deactivateLicense(companyId)
        return True

    @api.one
    def renewLicense(self, companyId, licenseId):
        license = self.env['career.license'].browse(int(licenseId))
        expiryDdate = date.today() + timedelta(days=license.validity)
        license_instance = self.env['career.license_instance'].create({'license_id': license.id,
                                                                       'expire_date': '%d-%d-%d ' % (
                                                                           expiryDdate.year, expiryDdate.month,
                                                                           expiryDdate.day),
                                                                       'email': int(license.email),
                                                                       'point': int(license.point),
                                                                       'assignment': int(license.assignment)})
        return self.env['res.company'].browse(companyId).write({'license_instance_id': license_instance.id,})

    @api.one
    def addLicense(self, companyId, licenseId):
        license = self.env['career.license'].browse(int(licenseId))
        company = self.env['res.company'].browse(int(companyId))
        license_instance_id = company.license_instance_id.id
        license_instance = self.env['career.license_instance'].browse(int(license_instance_id))
        expiryDdate = datetime.datetime.strptime(license_instance.expire_date, "%Y-%m-%d") + timedelta(days=license.validity)
        result = license_instance.write({ 'expire_date': '%d-%d-%d ' % (expiryDdate.year, expiryDdate.month,
                                                                        expiryDdate.day),
                                          'email': int(license.email) + int(license_instance.email),
                                          'point': int(license.point) + int(license_instance.point),
                                          'assignment': int(license.assignment) + int(license_instance.assignment)})
        if result:
            return True
        return False
