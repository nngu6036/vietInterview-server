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


class CommonService(osv.AbstractModel):
    _name = 'career.common_service'

    @api.model
    def searchPotentialCandidate(self,assignmentId):
        candidateList = []
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.category_ids:
                for cat_id in assignment.category_ids.ids:
                    for exp in self.env['career.work_experience'].search([]):
                        if cat_id in exp.cat_ids.ids:
                            employee_id =  exp.employee_id
                            candidate  = {'id':employee_id.id,'name':employee_id.user_id.name,'email':employee_id.user_id.login}
                            candidate['profile'] = employee_id.getProfile()
                            candidate['expList'] = employee_id.getWorkExperience()
                            candidate['eduList'] = employee_id.getEducationHistory()
                            candidate['certList'] = employee_id.getCertificate()
                            candidate['docList'] = employee_id.getDocument()
                            candidateList.append(candidate)
        return candidateList

    @api.model
    def searchJob(self,keyword,options):
        assignmentList = []
        domain = [('state','=','recruit')]
        if options:
            if options['countryId']:
                domain.append(('country_id','=',int(options['countryId'])))
            if options['provinceId']:
                domain.append(('province_id','=',int(options['provinceId'])))
            if options['positionId']:
                domain.append(('position_id','=',int(options['positionId'])))

        if keyword:
            domain.append('|')
            domain.append(('description','like',keyword))
            domain.append(('name','like',keyword))

        for a in self.env['hr.job'].search(domain):
            if options['categoryId'] and a.category_ids and not int(options['categoryId']) in a.category_ids.ids:
                continue
            assignmentList.append({'id':a.id,'name':a.name,'description':a.description,'deadline':a.deadline,'status':a.status,
                               'countryId':a.country_id.id, 'provinceId':a.province_id.id,'requirements':a.requirements,
                               'categoryIdList':list(a.category_ids.ids), 'positionId':a.position_id.id} )
        return assignmentList


    @api.model
    def getCompanyInfo(self,assignmentId):
        for assignment in self.env['hr.job'].browse(assignmentId):
            return {'id': assignment.company_id.id, 'name': assignment.company_id.name, 'image': assignment.company_id.logo or False}

    @api.model
    def searchEmployee(self, email):
        employees = self.env['career.employee'].search([('login', '=', email)])
        employeeList = [{'id': e.id, 'name': e.user_id.name, 'email': e.user_id.login,
                         'profile': e.getProfile(),
                         'expList': e.getWorkExperience(),
                         'eduList': e.getEducationHistory(),
                         'certList': e.getCertificate(),
                         'docList': e.getDocument(),
                         } for e in employees]
        return employeeList