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
                                                                       'expire_date':'%d-%d-%d ' % (expiryDdate.year, expiryDdate.month, expiryDdate.day)})
        company = self.env['res.company'].create({'name':vals['name'],'logo':vals['image'] if 'image' in vals else False,'license_instance_id':license_instance.id})
        company.partner_id.write({'email':vals['email']})
        hr_eval_plan = self.env['hr_evaluation.plan'].create({'name':'Assessment','company_id':company.id})
        assessment_form = self.env.ref('career.assessment_form')
        self.env['hr_evaluation.plan.phase'].create({'name':'Assessment','company_id':company.id,'plan_id':hr_eval_plan.id,
                                                         'action':'final','survey_id':assessment_form.id})
        return company.id

    @api.model
    def updateCompany(self,id,vals):
        company = self.env['res.company'].browse(id)
        if company:
            company.write({'name':vals['name'],'logo':vals['image'] if 'image' in vals else False})
            company.partner_id.write({'email':vals['email']})
            return True
        return False

    @api.model
    def getCompany(self):
        main_compnay = self.env.ref('base.main_company')
        companys = self.env['res.company'].search([('id','!=',main_compnay.id)])
        companyList = [{'id':c.id,'name':c.name,'image':c.logo or False,'licenseId':  c.license_instance_id.license_id.id if c.license_instance_id else False,
                        'license':  c.license_instance_id.license_id.name if c.license_instance_id else False,
                         'licenseExpire': c.expire_date if c.license_instance_id else False,'email':c.partner_id.email} for c in companys]
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
    def createLicense(self,vals):
        license = self.env['career.license'].create({'name':vals['name'],'email':int(vals['email']),'assignment':int(vals['assignment']),
                                                       'validity':int(vals['validity'])})
        return license.id

    @api.model
    def getLicense(self):
        licenses = self.env['career.license'].search([])
        licenseList = [{'id':l.id,'name':l.name,'email':l.email,'assignment':l.assignment,'validity':l.validity,'createDate':l.create_date} for l in licenses]
        return licenseList

    @api.model
    def approveAssignment(self,id):
        assignment = self.env['hr.job'].browse(id)
        if assignment and assignment.state!='recruit':
            assignment.write({'state':'recruit'})
            self.env['career.mail_service'].sendJobApprovalNotification(assignment.id)
            return True
        return False

    @api.model
    def getAssignment(self):
        assignments = self.env['hr.job'].search([])
        assignmentList = [{'id':a.id,'name':a.name,'description':a.description,'deadline':a.deadline,'status':a.status,
                           'requirements':a.requirements,'approved':a.state=='recruit',
                           'company':a.company_id.name,'companyId':a.company_id.id,
                           'countryId':a.country_id.id, 'provinceId':a.province_id.id,
                           'createDate':a.create_date,
                           'categoryId':a.category_id.id, 'positionId':a.position_id.id} for a in assignments]
        return assignmentList

    @api.model
    def createAssignment(self, vals):
            address = self.env['res.partner'].create({'name': vals['name'], 'type': 'contact',
                                                      'country_id': 'countryId' in vals and int(vals['countryId']),
                                                      'state_id': 'provinceId' in vals and int(vals['provinceId']),
                                                      'company_id': vals['companyId']})
            assignment = self.env['hr.job'].create({'name': vals['name'], 'description': vals['description'],
                                                    'deadline': vals['deadline'], 'company_id': vals['companyId'],
                                                    'requirements': vals['requirements'] or False,
                                                    'category_id': 'categoryId' in vals and int(vals['categoryId']),
                                                    'position_id': 'positionId' in vals and int(vals['positionId']),
                                                    'address_id': address.id, 'state': 'open'})
            '''self.env['career.mail_service'].sendNewJobNotification(assignment.id)'''
            return assignment.id

    @api.model
    def updateAssignment(self, id, vals):
        assignment = self.env['hr.job'].browse(id)
        if assignment:
            assignment.write({'deadline': vals['deadline'], 'description': vals['description'], 'name': vals['name'],
                              'requirements': vals['requirements'],
                              'category_id': int(vals['categoryId']) or False,
                              'position_id': int(vals['positionId']) or False})
            assignment.address_id.write(
                {'country_id': int(vals['countryId']) or False, 'state_id': int(vals['provinceId']) or False})
            return True
        return False


    @api.model
    def openAssignment(self, id):
        assignment = self.env['hr.job'].browse(id)
        if assignment:
            assignment.write({'status': 'published'})
            return True
        return False

    @api.model
    def closeAssignment(self, id):
        assignment = self.env['hr.job'].browse(id)
        if assignment:
            assignment.write({'status': 'closed'})
            return True
        return False

    @api.model
    def deleteAssignment(self, id):
        for assignment in self.env['hr.job'].browse(id):
            if assignment.status == 'initial':
                assignment.unlink()
                return True
        return False