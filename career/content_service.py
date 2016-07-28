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



class ContentService(osv.AbstractModel):
    _name = 'career.content_service'

    @api.model
    def getQuestionCategory(self,lang):
        categories = self.env['career.question_category'].search([('lang','=',lang)])
        categoryList = [{'id':c.id,'title':c.title} for c in categories]
        return categoryList

    @api.model
    def getQuestion(self,lang):
        questions = self.env['career.question'].search([('lang','=',lang)])
        questionList = [{'id':q.id,'title':q.title,'content':q.content,'videoUrl':q.videoUrl,'categoryId':q.category_id.id    } for q in questions]
        return questionList

    @api.model
    def getAssessment(self,lang):
        context = {'lang':util.lang_resolver(lang)}
        assessment_form = self.env.ref('career.assessment_form')
        groupList=[]
        questionList = []
        for page in self.env['survey.page'].with_context(context).browse(assessment_form.page_ids.ids):
            groupList.append({'id':page.id,'name':page.title,'order':page.sequence} )
            for question in self.env['survey.question'].with_context(context).browse(page.question_ids.ids):
                questionList.append({'id':question.id,'content':question.question,'groupId':question.page_id.id,
                                 'minVal':question.validation_min_float_value,'maxVal':question.validation_max_float_value} )
        return {'id':assessment_form.id,'groupList':groupList,'questionList':questionList}

    @api.model
    def createQuestionCategory(self,vals):
        category = self.env['career.question_category'].create({'title':vals['title'],'lang':vals['lang']})
        return category.id

    @api.model
    def updateQuestionCategory(self,id,vals):
        category = self.env['career.question_category'].browse(id)
        if category:
            category.write({'title':vals['title']})
            return True
        return False

    @api.model
    def createQuestion(self,vals):
        question = self.env['career.question'].create({'title':vals['title'],'content':vals['content'],'videoUrl':vals['videoUrl'],
                                                       'categoryId':int(vals['categoryId']),'lang':vals['lang']})
        return question.id

    @api.model
    def updateQuestion(self,id,vals):
        question = self.env['career.question'].browse(id)
        if question:
            question.write({'title':vals['title'],'content':vals['content'],'videoUrl':vals['videoUrl'],
                                                       'categoryId':int(vals['categoryId'])})
            return True
        return False
