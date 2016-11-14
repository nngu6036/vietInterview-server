from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import base64
import datetime
from datetime import date, timedelta

class QuestionCategory(models.Model):
	_name = 'career.question_category'
	title = fields.Text(string="Title",translate=True)
	lang = fields.Char(string="Language",default="en")

	@api.model
	def getQuestionCategory(self,lang):
		categories = self.env['career.question_category'].search([('lang','=',lang)])
		categoryList = [{'id':c.id,'title':c.title} for c in categories]
		return categoryList

	@api.multi
	def updateQuestionCategory(self,vals):
		self.ensure_one()
		self.write({'title':vals['title']})
		return True

	@api.multi
	def createQuestionCategory(self,vals):
		category = self.env['career.question_category'].create({'title':vals['title'],'lang':vals['lang']})
		return category.id


class Question(models.Model):
	_name = 'career.question'
	title = fields.Text(string="Title",translate=True)
	content = fields.Text(string="Content",translate=True)
	videoUrl = fields.Text(string="VIdeo")
	category_id = fields.Many2one('career.question_category', string="Category")
	lang = fields.Char(string="Language",default="en")
	type = fields.Selection([('ET', 'Extended text'), ('SC', 'Single choice')],default='ET')
	option_ids  = fields.One2many('career.question_option', 'question_id',string="Option")

	@api.model
	def getQuestion(self,lang):
		questions = self.env['career.question'].search([('lang','=',lang)])
		questionList = [{'id':q.id,'title':q.title,'content':q.content,'videoUrl':q.videoUrl,'categoryId':q.category_id.id,
						 'type':q.type, 'options':[{'id':o.id,'title':o.title,'correct':o.correct} for o in q.option_ids]} for q in questions]
		return questionList

	@api.model
	def createQuestion(self,vals):
		question = self.env['career.question'].create({'title':vals['title'],'content':vals['content'],'videoUrl':vals['videoUrl'],
													   'categoryId':int(vals['categoryId']),'lang':vals['lang']})
		return question.id

	@api.multi
	def updateQuestion(self,vals):
		self.ensure_one()
		self.write({'title':vals['title'],'content':vals['content'],'videoUrl':vals['videoUrl'],
												   'categoryId':int(vals['categoryId'])})
		return True

class QuestionOption(models.Model):
	_name = 'career.question_option'
	title = fields.Text(string="Title",translate=True)
	correct = fields.Boolean(string="Is correct")
	question_id = fields.Many2one('career.question', string="Question")
	lang = fields.Char(string="Language",default="en")

	@api.model
	def createQuestionOption(self,vals):
		option = self.env['career.question_option'].create({'title':vals['title'],'correct':bool(vals['correct']),
															'question_id':int(vals['questionId']),'lang':vals['lang']})
		return option.id


	@api.multi
	def deleteQuestionOption(self):
		if self.unlink():
			return True
		return False