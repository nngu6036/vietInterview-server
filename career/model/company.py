from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import base64
import datetime
from datetime import date, timedelta

class License(models.Model):
	_name = 'career.license'

	name = fields.Char(string='Name', required=True)
	assignment = fields.Integer(string='Assignment limit')
	email = fields.Integer(string='Email limit')
	validity = fields.Integer(string='Validity period')

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

class LicenseInstance(models.Model):
	_name = 'career.license_instance'

	license_id = fields.Many2one('career.license', string="License")
	expire_date = fields.Date(string="Expired date")
	effect_date = fields.Date(string="Effective date ")
	state = fields.Selection([('initial', 'Initial state'), ('suspend', 'Suspended state'), ('active', 'Active state'),
                              ('closed', 'Closed state')], default='initial')
	email_history_ids = fields.One2many('career.email.history','license_instance_id','Email history')

	@api.one
	def isEnabled(self):
		if self.state != 'active' :
			return False
		if not self.expire_date:
			return True
		expire_date = datetime.datetime.strptime(self.expire_date, "%Y-%m-%d")
		if  expire_date < datetime.datetime.now():
			return False
		return True

class LicenseEmailHistory(models.Model):
	_name = 'career.email.history'

	applicant_id = fields.Many2one('hr.applicant',string='Applicant ')
	company_id = fields.Many2one('res.company',related='employer_id.user_id.company_id')
	email = fields.Char(string='email',related='applicant_id.email_from')
	assignment_id = fields.Many2one(string='Job',related='applicant_id.job_id')
	survey_id = fields.Many2one('survey.survey',related='applicant_id.join_survey_id')
	date_send = fields.Date(string="Send date")
	employer_id = fields.Many2one('career.employer',string='Employer user')
	license_instance_id = fields.Many2one('career.license_instance',string='Applied license')

class CompanyUser(models.Model):
	_name = 'career.employer'
	_inherits = {'res.users':'user_id'}

	user_id = fields.Many2one('res.users',string='User',required=True)
	login = fields.Char(string='Login name',related='user_id.login')
	password = fields.Char(string='Password',related='user_id.password')
	name = fields.Char(string='Name',related='user_id.name')

	@api.one
	def createAssignment(self,vals):
		address = self.env['res.partner'].create({'name': vals['name'], 'type': 'contact',
												  'country_id': 'countryId' in vals and int(vals['countryId']),
												  'state_id': 'provinceId' in vals and int(vals['provinceId']),
												  'company_id': self.id})
		assignment = self.env['hr.job'].create({'name': vals['name'], 'description': vals['description'],
												'deadline': vals['deadline'], 'company_id': self.user_id.company_id.id,
												'requirements': vals['requirements'] or False,
												'category_id': 'categoryId' in vals and int(vals['categoryId']),
												'position_id': 'positionId' in vals and int(vals['positionId']),
												'address_id': address.id, 'state': 'open'})
		self.env['career.mail_service'].sendNewJobNotification(assignment.id)
		return assignment.id


	@api.one
	def openAssignment(self, id):
		assignment = self.env['hr.job'].browse(id)
		if assignment:
			assignment.write({'status': 'published'})
			return True
		return False

	@api.one
	def closeAssignment(self, id):
		assignment = self.env['hr.job'].browse(id)
		if assignment:
			assignment.write({'status': 'closed'})
			return True
		return False

	@api.model
	def updateCompanyUser(self,id,vals):
		employer = self.env['career.employer'].browse(id)
		if employer:
			employer.user_id.write({'name':vals['name']})
			return True
		return False

	@api.one
	def getCompanyInfo(self):
		return {'id': self.company_id.id, 'name': self.company_id.name,	'image': self.company_id.logo or False,
				'email':self.company_id.partner_id.email}


	@api.one
	def createInterview(self, assignmentId, vals):
		interview = self.env['survey.survey'].create({'title': vals['name'], 'response': int(vals['response']),
													   'retry': int(vals['retry']) if 'retry' in vals else False ,
													  'introUrl': vals['introUrl'], 'job_id': assignmentId,
													  'exitUrl': vals['exitUrl'], 'aboutUsUrl': vals['aboutUsUrl'],
													  'prepare': int(vals['prepare']) if 'prepare' in vals else False,
													  'language': vals['language'] if 'language' in vals else False,
													  'round': int(vals['round']) if 'roumd' in vals else False,
													  'mode': vals['mode'] if 'mode' in vals else False})
		return interview.id

	@api.one
	def openInterview(self, id):
		for interview in self.env['survey.survey'].browse(id):
			if interview.status!='published' and interview.job_id.status=='published' and not self.env['survey.survey'].search([('job_id', '=', interview.job_id.id), ('status', '=', 'published')]):
				interview.write({'status': 'published'})
				return True
		return False

	@api.one
	def closeInterview(self, id):
		for interview in self.env['survey.survey'].browse(id):
			interview.write({'status': 'closed'})
			return True
		return False

	@api.one
	def submitAssessment(self, assessmentResult):
		company = self.user_id.company_id
		hr_interview_assessment = self.env['hr.evaluation.interview'].search([('user_id', '=', self.user_id.id), ('applicant_id', '=', int(assessmentResult['candidateId']))])
		if not hr_interview_assessment:
			hr_eval_phase = self.env['hr_evaluation.plan.phase'].search([('company_id', '=', company['id'])])
			hr_eval = self.env['hr_evaluation.evaluation'].create({'employee_id': self.id,
										   'plan_id': hr_eval_phase.plan_id.id,
										   'state': 'progress'})
			hr_interview_assessment = self.env['hr.evaluation.interview'].create({'evaluation_id': hr_eval.id, 'phase_id': hr_eval_phase.id,
			 'applicant_id': int(assessmentResult['candidateId']), 'state': 'done', 'user_id': self.user_id.id})
		hr_interview_assessment.write( {'rating': int(assessmentResult['vote']), 'note_summary': assessmentResult['comment']})
		for jAns in assessmentResult['answerList']:
			if not self.env['survey.user_input_line'].search([('user_input_id', '=', hr_interview_assessment[0].request_id.id),
				 ('question_id', '=', int(jAns['questionId']))]):
				self.env['survey.user_input_line'].create({'user_input_id': hr_interview_assessment[0].request_id.id,
									   'question_id': int(jAns['questionId']),
									   'answer_type': 'number',
									   'value_number': int(jAns['answer'])})
		return hr_interview_assessment.id

	@api.one
	def getSelfAssessment(self, assessmentId, applicantId):
		hr_interview_assessment = self.env['hr.evaluation.interview'].search(	[('applicant_id', '=', applicantId), ('user_id', '=', self.user_id.id)])
		answerList = [{'id': answer.id, 'questionId': answer.question_id.id, 'answer': answer.value_number}
					  for answer in  hr_interview_assessment.request_id.user_input_line_ids]
		return {'id': hr_interview_assessment.id, 'comment': hr_interview_assessment.note_summary,
			'vote': hr_interview_assessment.rating, 'answerList': answerList}

	@api.one
	def getOtherAssessment(self, assessmentId, applicantId):
		assessmentResultList = []
		for hr_interview_assessment in self.env['hr.evaluation.interview'].search([('applicant_id', '=', applicantId), ('user_id', '!=', self.user_id.id)]):
			assessmentResultList.append(
				{'answertList': [{'id': answer.id, 'questionId': answer.question_id.id, 'answer': answer.value_number}  for answer in hr_interview_assessment.request_id.user_input_line_ids],
				'id': hr_interview_assessment.id, 'comment': hr_interview_assessment.note_summary,
				'vote': hr_interview_assessment.rating,
				'user': hr_interview_assessment.user_id.name})
		return assessmentResultList


class Conpany(models.Model):
	_name = 'res.company'
	_inherit = 'res.company'

	license_instance_id = fields.Many2one('career.license_instance',string='License')
	expire_date = fields.Date(string='License expire date',related='license_instance_id.expire_date')

	@api.model
	def createCompany(self,vals):
		license = self.env['career.license'].browse(int(vals['licenseId']))
		expiryDdate =  date.today() + timedelta(days=license.validity)
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
		print vals
		if company:
			company.write({'name':vals['name'],'logo':vals['image'] if 'image' in vals else False})
			company.partner_id.write({'email':vals['email'] })
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

	@api.one
	def createCompanyUser(self,vals):
		user = self.env['res.users'].search([('login', '=', vals['email'])])
		if user:
			print ("Emplyer login %s already exist" % vals['email'])
			return False
		employer_group = self.env.ref('career.employer_group')
		hr_group = self.env.ref('base.group_hr_manager')
		survey_group = self.env.ref('base.group_survey_manager')
		admin_group = self.env.ref('base.group_erp_manager')
		user = self.env['res.users'].create({'login':vals['email'],'password':vals['password'],'name':vals['name'],'notify_email':'none',
											 'email':vals['email']})
		user.write({'company_ids':[(4,self.id)]})
		user.write({'company_id':self.id, 'groups_id':[(6,0,[employer_group.id,hr_group.id,survey_group.id,admin_group.id])]})
		self.env['hr.employee'].create({'address_id':self.partner_id.id,'work_email':vals['email'],'name':vals['name'],
									   'user_id':user.id,'company_id':self.id})
		new_employer = self.env['career.employer'].create({ 'user_id':user.id,'is_admin':False})
		return new_employer.id

	@api.one
	def getCompanyUser(self):
		userList=[]
		for user in self.user_ids:
			if user.company_id.id == self.id:
				userList.append({'id':user.id,'name':user.name,'email':user.login})
		return userList

	@api.one
	def getAssignment(self):
		assignments = self.env['hr.job'].search([('company_id', '=', self.id)])
		assignmentList = [{'id': a.id, 'name': a.name, 'description': a.description, 'deadline': a.deadline, 'status': a.status,
			'requirements': a.requirements, 'approved': a.state == 'recruit',
			'countryId': a.country_id.id, 'provinceId': a.province_id.id,
			'createDate': a.create_date,
			'categoryId': a.category_id.id, 'positionId': a.position_id.id} for a in assignments]
		return assignmentList

	@api.one
	def getLicenseStatistic(self):
		stats = {'email':0,'license':False}
		if self.license_instance_id:
			stats['email'] = self.env['career.email.history'].search_count([('license_instance_id','=',self.license_instance_id.id)])
			stats['license'] = {'name':self.license_instance_id.license_id.name,'email':self.license_instance_id.license_id.email,
							  'expireDate':self.license_instance_id.expire_date,'state':self.license_instance_id.state}
		return stats