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
        domain = [('status','=','published'),('state','=','recruit')]
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


    @api.model
    def getApplicantHistory(self,uid):
        applicationList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            applicants = self.env['hr.applicant'].search([('email_from','=',employee.login)])
            for applicant in applicants:
                interview_link = False
                if applicant.response_id:
                    interview_link = "https://vietinterview.com/interview?code=%s&" % applicant.response_id.token
                applicationList.append({'id':applicant.id,'title':applicant.job_id.name,'company':applicant.company_id.name,
                                       'deadline':applicant.job_id.deadline,'applyDate':applicant.create_date,'interview_link':interview_link})
        return applicationList

    @api.model
    def searchPotentialCandidate(self,assignmentId):
      employeeList = []
      for assignment in self.env['hr.job'].browse(assignmentId):
          if assignment.category_id:
            experiences = self.env['career.work_experience'].search([('cat_id','=',assignment.category_id.id)])
            employeeList = [{'id':employee.id,'name':employee.user_id.name,'email':employee.user_id.login} for employee in self.env['career.employee'].browse(experiences.employee_id.ids)]
      return employeeList