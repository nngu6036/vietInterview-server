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
    def searchJob(self,keyword,options,start=None,length=None,count=False):
        assignmentList = []
        domain = [('state','=','recruit')]
        countryId = options['countryId'] if options and options['countryId'] else False
        provinceId = options['provinceId'] if options and options['provinceId'] else False
        positionId = options['positionId'] if options and options['positionId'] else False
        categoryId = options['categoryId'] if options and options['categoryId'] else False
        if countryId:
            domain.append(('country_id','=',int(options['countryId'])))
        if provinceId:
            domain.append(('province_id','=',int(options['provinceId'])))
        if positionId:
            domain.append(('position_id','=',int(options['positionId'])))

        if keyword:
            domain.append('|')
            domain.append(('description','ilike',keyword))
            domain.append(('name','ilike',keyword))
        totalTal  = 0
        if count:
            for a in self.env['hr.job'].search(domain, limit=int(length), offset=int(start)):
                if categoryId and a.category_ids and not categoryId in a.category_ids.ids:
                    continue
                totalTal = totalTal +1

        for a in self.env['hr.job'].search(domain,limit=int(length),offset=int(start)):
            if categoryId and a.category_ids and not categoryId in a.category_ids.ids:
                continue
            assignmentList.append({'id':a.id,'name':a.name,'description':a.description,'deadline':a.deadline,'status':a.status,
                               'countryId':a.country_id.id, 'provinceId':a.province_id.id,'requirements':a.requirements,
                               'categoryIdList':list(a.category_ids.ids), 'positionId':a.position_id.id,'company':a.company_id.name} )
        return {'assignmentList':assignmentList,'total':totalTal}


    @api.model
    def getCompanyInfo(self,assignmentId):
        for assignment in self.env['hr.job'].browse(assignmentId):
            return {'id': assignment.company_id.id, 'name': assignment.company_id.name,
                    'image': assignment.company_id.logo or False,
                    'description': assignment.company_id.partner_id.description,
                    'videoUrl': assignment.company_id.partner_id.videoUrl}

