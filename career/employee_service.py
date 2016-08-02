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



class EmployeeService(osv.AbstractModel):
    _name = 'career.employee_service'


    @api.model
    def getUserProfile(self):
        cr, uid, context = self.env.args
        users = self.env['res.users'].browse(uid)
        if users:
            user = users[0]
            return {'id':user.partner_id.id, 'name':user.partner_id.name,'phone':user.partner_id.phone,'mobile':user.partner_id.mobile,
                    'email':user.partner_id.email,'address':user.partner_id.street, 'countryId':user.partner_id.country_id.id,
                    'provinceId':user.partner_id.state_id.id,'birthdate':user.partner_id.birthdate or False,'image':user.partner_id.image or False,
                    'gender':user.partner_id.gender or False }
        return False

    @api.model
    def updateUserProfile(self,vals):
        cr, uid, context = self.env.args
        users = self.env['res.users'].browse(uid)
        if users:
            users.partner_id.write({'name':vals['name'],'phone':vals['phone'],'mobile':vals['mobile'],
                                    'email':vals['email'],'street':vals['address'], 'country_id':vals['countryId'],
                                    'state_id':vals['provinceId'], 'birthdate':vals['birthdate'] if 'birthdate' in vals else None,
                                    'image':vals['image']  if 'image' in vals else None,
                                    'gender':vals['gender'] if 'gender' in vals else None
                                    })
        return True

    @api.model
    def getWorkExperience(self):
        cr, uid, context = self.env.args
        expList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            for exp in employee.experience_ids:
                expList.append({'id':exp.id,'title':exp.title,'employer':exp.employer,'startDate':exp.start_date,'endDate':exp.end_date,
                                'current':exp.current,'categoryId':  exp.cat_id.id if exp.cat_id else False,'countryId':exp.country_id.id,'provinceId':exp.province_id.id,
                                'description':exp.description})
        return expList

    @api.model
    def addWorkExperience(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            exp = self.env['career.work_experience'].create({'title':vals['title'],'employer':vals['employer'],
                                                             'start_date':'startDate' in vals and vals['startDate'],
                                                             'description':vals['description'],
                                                            'end_date':'endDate' in vals and vals['endDate'],'current':vals['current'],
                                                             'cat_id':vals['categoryId'],
                                                             'country_id':'countryId' in vals and int(vals['countryId']),
                                                             'province_id':'provinceId' in vals and int(vals['provinceId']),
                                                             'employee_id':employee.id})
            return exp.id
        return False

    @api.model
    def updateWorkExperience(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.work_experience'].browse(int(vals['id'])).write({'title':vals['title'],'employer':vals['employer'],'start_date':vals['startDate'],
                                                            'end_date':vals['endDate'],'current':vals['current'],'cat_id':vals['categoryId'],
                                                             'country_id':int(vals['countryId']),'province_id':int(vals['provinceId']),
                                                             'employee_id':employee.id,'description':vals['description']})
            return True
        return False

    @api.model
    def removeWorkExperience(self,ids):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.work_experience'].browse(ids).unlink()
        return True



    @api.model
    def getEducationHistory(self):
        cr, uid, context = self.env.args
        eduList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            for edu in employee.education_ids:
                eduList.append({'id':edu.id,'program':edu.program,'institute':edu.institute,'finishDate':edu.complete_date,
                                'status':edu.status,'levelId':edu.level_id.id})
        return eduList

    @api.model
    def addEducationHistory(self,vals):
        cr, uid, context = self.env.args
        for employee in  self.env['career.employee'].search([('user_id','=',uid)]):
            edu = self.env['career.education_history'].create({'program':vals['program'],'institute':vals['institute'],
                                                            'complete_date':vals['finishDate'],'status':vals['status'],
                                                             'level_id':int(vals['levelId']),'employee_id':employee.id})
            return edu.id
        return False

    @api.model
    def updateEducationHistory(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.education_history'].browse(int(vals['id'])).write({'program':vals['program'],'institute':vals['institute'],
                                                            'complete_date':vals['finishDate'],'status':vals['status'],
                                                             'level_id':int(vals['levelId'])})
            return True
        return False

    @api.model
    def removeEducationHistory(self,ids):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.education_history'].browse(ids).unlink()
        return True

    @api.model
    def getCertificate(self):
        cr, uid, context = self.env.args
        certList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            for cert in employee.certificate_ids:
                certList.append({'id':cert.id,'title':cert.title,'issuer':cert.issuer,'issueDate':cert.issue_date})
        return certList

    @api.model
    def addCertificate(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            cert = self.env['career.certificate'].create({'title':vals['title'],'issuer':vals['issuer'],
                                                            'issue_date':vals['issueDate'],'employee_id':employee.id})
            return cert.id
        return False

    @api.model
    def updateCertificate(self,vals):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.certificate'].browse(int(vals['id'])).write({'title':vals['title'],'issuer':vals['issuer'],
                                                            'issue_date':vals['issueDate']})
            return True
        return False

    @api.model
    def removeCertificate(self,ids):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['career.certificate'].browse(ids).unlink()
        return True

    @api.model
    def getDocument(self):
        cr, uid, context = self.env.args
        certList = []
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            documents = self.env['ir.attachment'].search([('res_model','=','career.employee'),('res_id','=',employee.id)])
            for doc in documents:
                certList.append({'id':doc.id,'title':doc.name,'filename':doc.datas_fname,'filedata':doc.store_fname})
        return certList

    @api.model
    def addDocument(self,title,filename,file_location):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            doc = self.env['ir.attachment'].create({'name':title,'description':title,'res_model':'career.employee','res_id':employee.id,
                                                       'type':'binary','store_fname':file_location,'datas_fname':filename})
            return doc.id
        return False

    @api.model
    def removeDocument(self,ids):
        cr, uid, context = self.env.args
        employees = self.env['career.employee'].search([('user_id','=',uid)])
        for employee in employees:
            self.env['ir.attachment'].browse(ids).unlink()
        return True

