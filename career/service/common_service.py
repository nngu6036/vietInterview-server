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
        employeeList = []
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.category_id:
                experiences = self.env['career.work_experience'].search([('cat_id','=',assignment.category_id.id)])
                employeeList = [{'id':employee.id,'name':employee.user_id.name,'email':employee.user_id.login} for employee in self.env['career.employee'].browse(experiences.employee_id.ids)]
        return employeeList

    @api.model
    def searchJob(self,keyword,options):
        domain = [('state','=','recruit')]
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

