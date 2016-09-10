# -*- coding: utf-8 -*-

from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import base64
import datetime
from datetime import date, timedelta



class AdminService(osv.AbstractModel):
    _name = 'career.admin_service'

    @api.model
    def approveAssignment(self,assignmentId):
        assignment = self.env['hr.job'].browse(assignmentId)
        if assignment and assignment.state!='recruit':
            assignment.write({'state':'recruit'})
            self.env['career.mail_service'].sendJobApprovalNotification(assignment.id)
            return True
        return False

    @api.model
    def createAssignment(self,companyId, vals):
        catIdList = vals['categoryIdList']
        address = self.env['res.partner'].create({'name': vals['name'], 'type': 'contact',
                                                  'country_id': 'countryId' in vals and int(vals['countryId']),
                                                  'state_id': 'provinceId' in vals and int(vals['provinceId']),
                                                  'company_id': self.id})
        assignment = self.env['hr.job'].create({'name': vals['name'], 'description': vals['description'],
                                                'deadline': vals['deadline'], 'company_id': companyId,
                                                'requirements': vals['requirements'] or False,
                                                'category_ids': [(6, 0, catIdList)] or False,
                                                'position_id': 'positionId' in vals and int(vals['positionId']),
                                                'address_id': address.id, 'state': 'open'})
        self.approveAssignment(assignment.id)
        return assignment.id

