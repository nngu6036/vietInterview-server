from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
from .. import util
import datetime
from datetime import date, timedelta



class JobCategory(models.Model):
	_name = 'career.job_category'
	title = fields.Text(string="Title",translate=True)

	@api.model
	def getJobCategory(self,lang):
		lang = util.lang_resolver(lang)
		context = {'lang':lang}
		categories = self.env['career.job_category'].with_context(context).search([])
		categoryList = [{'id':c.id,'title':c.title} for c in categories]
		return categoryList

class JobPosition(models.Model):
	_name = 'career.job_position'
	title = fields.Text(string="Title",translate=True)

	@api.model
	def getJobPosition(self,lang):
		lang = util.lang_resolver(lang)
		context = {'lang':lang}
		positions = self.env['career.job_position'].with_context(context).search([])
		positionList = [{'id':p.id,'title':p.title} for p in positions]
		return positionList



class Assignment(models.Model):
	_name = 'hr.job'
	_inherit = 'hr.job'

	status = fields.Selection([('initial', 'Initial status'), ('published', 'Published status'),  ('closed', 'Closed status')], default='initial')
	deadline = fields.Date(string="Application deadline")
	category_id = fields.Many2one('career.job_category', string="Category")
	position_id = fields.Many2one('career.job_position', string="Position")
	country_id = fields.Many2one(string='Country',related='address_id.country_id')
	province_id = fields.Many2one(string='Province ',related='address_id.state_id')
	survey_ids = fields.One2many('survey.survey', 'job_id',string="Interview rounds")

	@api.one
	def isEnabled(self):
		if self.state !='recruit':
			return False
		if not self.deadline:
			return True
		deadline = datetime.datetime.strptime(self.deadline, "%Y-%m-%d")
		if deadline < datetime.datetime.now():
			return False
		return True

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
	def deleteAssignment(self, id):
		for assignment in self.env['hr.job'].browse(id):
			if assignment.status == 'initial':
				assignment.unlink()
				return True
		return False

	@api.one
	def getCompanyInfo(self):
		return {'id': self.company_id.id,'name': self.company_id.name,'image': self.company_id.logo or False}

	@api.one
	def getCandidate(self):
		applicants = self.env['hr.applicant'].search([('job_id', '=', self.id), ('survey', 'in', self.survey_id.id)])
		candidateList = [{'id': a.id, 'name': a.name, 'email': a.email_from, 'shortlist': a.shortlist,
				  'invited': True if self.env['career.email.history'].search( [('assignment_id', '=', self.id),
					   ('email', '=', a.email_from)]) else False} for a in applicants]
		return candidateList

	@api.one
	def getInterview(self):
		if self.survey_id:
			interview = {'id': self.survey_id.id, 'name': self.survey_id.title,
					 'response': self.survey_id.response,
					 'retry': self.survey_id.retry, 'introUrl': self.survey_id.introUrl,
					 'exitUrl': self.survey_id.exitUrl,
					 'aboutUsUrl': self.survey_id.aboutUsUrl, 'language': self.survey_id.language,
					 'prepare': self.survey_id.prepare,'job_id':self.id,'round':self.survey_id.round,
					 'mode':self.survey_id.mode,'status':self.survey_id.status}
			return interview

	@api.one
	def getAassignmentStatistic(self):
		applicant_count = self.application_count
		invite_count = self.env['career.email.history'].search_count([('assignment_id', '=', self.id)])
		response_count = self.env['survey.user_input'].search_count(
			[('survey_id', '=', self.survey_id.id), ('state', '=', 'done')])
		return {'applicant': applicant_count, 'invitation': invite_count, 'response': response_count}