from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import base64
import datetime
from datetime import date, timedelta




class Applicant(models.Model):
	_name = 'hr.applicant'
	_inherit = 'hr.applicant'

	shortlist = fields.Boolean(string="Short-listed")
	join_survey_id = fields.Many2one('survey.survey', string="Interview to join")



class Conference(models.Model):
	_name = 'career.conference'

class Interview(models.Model):
	_name = 'survey.survey'
	_inherit = 'survey.survey'

	response = fields.Integer(string="Response time  for one question")
	prepare = fields.Integer(string="Prepare time  for one question")
	retry = fields.Integer(string="Number of attempts for one question, -1 means unlimited")
	introUrl = fields.Text(string="Introduction Video URL")
	exitUrl = fields.Text(string="Thank you Video URL")
	aboutUsUrl = fields.Text(string="About Us Video URL")
	language = fields.Char(string="Language",default="en")
	job_id = fields.Many2one('hr.job', string="Job")
	status = fields.Selection([('initial', 'Initial status'), ('published', 'Published status'),  ('closed', 'Closed status')], default='initial')
	conference_id = fields.Many2one('career.conference', string="Conference")
	mode = fields.Selection([('conference', 'Conference interview'), ('video', 'Video interview')], default='video')
	round = fields.Integer(string="Interview round number")

	@api.model
	def updateInterview(self, id, vals):
		interview = self.env['survey.survey'].browse(id)
		if interview:
			interview.write({'title': vals['name'], 'response': int(vals['response']),
					 'retry': int(vals['retry']) if 'retry' in vals else False,
					 'introUrl': vals['introUrl'],
					 'exitUrl': vals['exitUrl'], 'aboutUsUrl': vals['aboutUsUrl'],
					 'prepare': int(vals['prepare']) if 'prepare' in vals else False,
					 'language': vals['language'] if 'language' in vals else False})
			return True
		return False

	@api.one
	def addInterviewQuestion(self, jQuestions):
		questionIds = []
		for jQuestion in jQuestions:
			page = self.env['survey.page'].create({'title': 'Single Page', 'survey_id': self.id})
			question = self.env['survey.question'].create({'question': jQuestion['title'], 'response': int(jQuestion['response']),
				 'retry': int(jQuestion['retry']) if 'retry' in jQuestions else False,
				 'videoUrl': jQuestion['videoUrl'],
				 'prepare': int(jQuestion['prepare']) if 'prepare' in jQuestion else False,
				 'source': jQuestion['source'], 'mode': jQuestion['type'], 'page_id': page.id,
				 'sequence': int(jQuestion['order']), 'survey_id': self.id})
			questionIds.append(question.id)
		return questionIds



	@api.one
	def getInterviewQuestion(self):
		questions = self.env['survey.question'].search([('survey_id', '=', self.id)])
		questionList = [
			{'id': q.id, 'title': q.question, 'response': q.response, 'retry': q.retry, 'videoUrl': q.videoUrl,
			 'source': q.source, 'type': q.mode, 'order': q.sequence, 'prepare': q.prepare} for q in questions]
		return questionList


	@api.one
	def getInterviewResponse(self):
		responseList = []
		for input in self.env['survey.user_input'].search([('survey_id', '=', self.id)]):
			for applicant in self.env['hr.applicant'].search(
				[('email_from', '=', input.email), ('response_id', '=', input.id)]):
				response = {'name': input.email, 'email': input.email, 'candidateId': applicant[0].id}
				response['answerList'] = [
				{'id': line.id, 'questionId': line.question_id.id, 'videoUrl': line.value_video_url} for line in input.user_input_line_ids]
				documents = self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant'), ('res_id', '=', applicant[0].id)])
				response['documentList'] = [
				{'id': doc.id, 'title': doc.name, 'filename': doc.datas_fname, 'filedata': doc.store_fname} for doc in
				documents]
				responseList.append(response)
		return responseList

class InterviewQuestion(models.Model):
	_name = 'survey.question'
	_inherit = 'survey.question'

	response = fields.Integer(string="Response time limit for one question")
	retry = fields.Integer(string="Number of attempts for one question, -1 means unlimited")
	prepare = fields.Integer(string="Prepare time for one question, -1 means unlimited",default=1)
	source = fields.Selection([('manual', 'User-defined'), ('system', 'System question')], default='system')
	mode = fields.Selection([('text', 'Reading'), ('video', 'Watching')], default='video')
	videoUrl = fields.Text(string="Question Video URL")



	@api.model
	def updateInterviewQuestion(self, jQuestions):
		for jQuestion in jQuestions:
			self.env['survey.question'].browse(int(jQuestion['id'])).write(
				{'question': jQuestion['title'], 'response': int(jQuestion['response']),
				 'retry': int(jQuestion['retry']) if 'retry' in jQuestions else False,
				 'videoUrl': jQuestion['videoUrl'],
				 'prepare': int(jQuestion['prepare']) if 'prepare' in jQuestion else False,
				 'source': jQuestion['source'], 'mode': jQuestion['type'],
				 'sequence': int(jQuestion['order'])})
		return True


	@api.model
	def removeInterviewQuestion(self, jQuestionIds):
		for qId in jQuestionIds:
			question = self.env['survey.question'].browse(int(qId))
			question.page_id.unlink()
			question.unlink()
		return True

class InterviewHistory(models.Model):
	_name = 'survey.user_input'
	_inherit = 'survey.user_input'

	wrap_up = fields.Boolean(string="Wrap-up completed")

class InterviewAnswer(models.Model):
	_name = 'survey.user_input_line'
	_inherit = 'survey.user_input_line'
	answer_type = fields.Selection([('text', 'Text'), ('number', 'Number'),('date', 'Date'),('free_text', 'Free Text'),
									('suggestion', 'Suggestion'),('url', 'URL')])
	value_video_url= fields.Text(string="URL Video reponse")