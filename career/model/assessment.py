from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
from .. import util


class InterviewAssessment(models.Model):
	_name = 'hr.evaluation.interview'
	_inherit = 'hr.evaluation.interview'

	applicant_id = fields.Many2one('hr.applicant',tring='Applicant ')
	rating =  fields.Integer(string="Rating")
	note_summary =  fields.Text(string="Comment")


	@api.model
	def getAssessment(self,lang):
		context = {'lang': util.lang_resolver(lang)}
		assessment_form = self.env.ref('career.assessment_form')
		groupList=[]
		questionList = []
		for page in self.env['survey.page'].with_context(context).browse(assessment_form.page_ids.ids):
			groupList.append({'id':page.id,'name':page.title,'order':page.sequence} )
			for question in self.env['survey.question'].with_context(context).browse(page.question_ids.ids):
				questionList.append({'id':question.id,'content':question.question,'groupId':question.page_id.id,
								 'minVal':question.validation_min_float_value,'maxVal':question.validation_max_float_value} )
		return {'id':assessment_form.id,'groupList':groupList,'questionList':questionList}