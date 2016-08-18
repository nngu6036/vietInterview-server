from openerp import models, fields, api, tools
from openerp.osv import osv
from openerp.service import common
import base64
import base64
import datetime
from datetime import date, timedelta
from .. import util
import string


class Applicant(models.Model):
    _name = 'hr.applicant'
    _inherit = 'hr.applicant'

    shortlist = fields.Boolean(string="Short-listed", default=False)
    interview_id = fields.Many2one('survey.survey', string="Interview to join")
    member_id = fields.Many2one('career.conference_member', string="Conference member")


class ConferenceMember(models.Model):
    _name = 'career.conference_member'

    name = fields.Text(string="Member name")
    member_id = fields.Char(string="Member ID")
    role = fields.Selection([('moderator', 'Moderator'), ('guest', 'Participant'), ('candidate', 'Candidate')],
                            default='guest')
    access_code = fields.Char(string="Conference access code")
    conference_id = fields.Many2one('career.conference', string="Conference to join")

    @api.model
    def create(self, vals):
        vals['member_id'] = util.id_generator(24, string.digits)
        conf = super(ConferenceMember, self).create(vals)
        return conf


class Conference(models.Model):
    _name = 'career.conference'

    name = fields.Text(string="Conference name")
    meeting_id = fields.Char(string="Metting ID")
    applicant_id = fields.Many2one('hr.applicant', string="Candidate")
    access_code = fields.Char(string="Conference access code")
    mod_access_code = fields.Char(string="Conference moderator access code")
    interview_id = fields.Many2one('survey.survey', string='Interview')
    language = fields.Char(string='Language', related='interview_id.language')
    member_ids = fields.One2many('career.conference_member', 'conference_id')
    schedule = fields.Datetime("Interview schedule")
    status = fields.Selection([('pending', 'Initial status'), ('started', 'Start status'), ('ended', 'Closed status')],
                              default='pending')

    @api.model
    def create(self, vals):
        vals['access_code'] = util.id_generator(12, string.digits)
        vals['mod_access_code'] = util.id_generator(12, string.digits)
        conf = super(Conference, self).create(vals)
        return conf

    @api.one
    def action_launch(self):
        if not self.env['career.conference_service'].openMeeting(self.id):
            return False
        return {'id': self.id, 'name': self.name, 'meetingId': self.meeting_id, 'moderatorPwd': self.mod_access_code}

    @api.model
    def getConference(self):
        conferences = self.env['career.conference'].search([])
        conferenceList = [
            {'id': c.id, 'name': c.name, 'language': c.language, 'meetingId': c.meeting_id,
             'job': c.interview_id.job_id.name, 'interview': c.interview_id.round, 'candidate': c.applicant_id.name,
             'schedule': c.schedule, 'status': c.status,
             'memberList': [{'name': m.name, 'memberId': m.member_id, 'role': m.role} for m in c.member_ids]} for c in
            conferences]
        return conferenceList


class Interview(models.Model):
    _name = 'survey.survey'
    _inherit = 'survey.survey'

    response = fields.Integer(string="Response time  for one question")
    prepare = fields.Integer(string="Prepare time  for one question")
    retry = fields.Integer(string="Number of attempts for one question, -1 means unlimited")
    introUrl = fields.Text(string="Introduction Video URL")
    exitUrl = fields.Text(string="Thank you Video URL")
    aboutUsUrl = fields.Text(string="About Us Video URL")
    language = fields.Char(string="Language", default="en")
    job_id = fields.Many2one('hr.job', string="Job")
    status = fields.Selection(
        [('initial', 'Initial status'), ('published', 'Published status'), ('closed', 'Closed status')],
        default='initial')
    conference_ids = fields.One2many('career.conference', 'interview_id', string="Conference")
    mode = fields.Selection([('conference', 'Conference interview'), ('video', 'Video interview')], default='video')
    round = fields.Integer(string="Interview round number", default=1)

    @api.model
    def create(self, vals):
        vals['round'] = self.env['survey.survey'].search_count([('job_id', '=', vals['job_id'])]) + 1
        interview = super(Interview, self).create(vals)
        return interview

    @api.one
    def updateInterview(self, vals):
        self.write({'title': vals['name'], 'response': int(vals['response']) if 'response' in vals else False,
                    'retry': int(vals['retry']) if 'retry' in vals else False,
                    'introUrl': vals['introUrl'],
                    'mode': vals['mode'],
                    'exitUrl': vals['exitUrl'], 'aboutUsUrl': vals['aboutUsUrl'],
                    'prepare': int(vals['prepare']) if 'prepare' in vals else False,
                    'language': vals['language'] if 'language' in vals else False})
        return True

    @api.one
    def addInterviewQuestion(self, jQuestions):
        questionIds = []
        for jQuestion in jQuestions:
            page = self.env['survey.page'].create({'title': 'Single Page', 'survey_id': self.id})
            question = self.env['survey.question'].create(
                {'question': jQuestion['title'], 'response': int(jQuestion['response']),
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
                response = {}
                response['candidate'] = {'id': applicant.id, 'name': applicant.name, 'email': applicant.email_from,
                                         'shortlist': applicant.shortlist,
                                         'invited': True if self.env['career.email.history'].search(
                                             [('applicant_id', '=', applicant.id)]) else False}
                response['answerList'] = [
                    {'id': line.id, 'questionId': line.question_id.id, 'videoUrl': line.value_video_url} for line in
                    input.user_input_line_ids]
                documents = self.env['ir.attachment'].search(
                    [('res_model', '=', 'hr.applicant'), ('res_id', '=', applicant[0].id)])
                response['documentList'] = [
                    {'id': doc.id, 'title': doc.name, 'filename': doc.datas_fname, 'filedata': doc.store_fname} for doc
                    in
                    documents]
                responseList.append(response)
        return responseList

    @api.one
    def getCandidate(self):
        candidateList = []
        for applicant in self.env['hr.applicant'].search(
                ['|', ('interview_id', '=', self.id), ('survey', '=', self.id)]):
            candidate = {'id': applicant.id, 'name': applicant.name, 'email': applicant.email_from,
                         'shortlist': applicant.shortlist,
                         'invited': True if self.env['career.email.history'].search([('survey_id', '=', self.id),
                                                                                     ('email', '=',
                                                                                      applicant.email_from)]) else False}
            if self.mode == 'conference' and applicant.member_id:
                candidate['schedule'] = applicant.member_id.conference_id.schedule
            for employee in self.env['career.employee'].search([('login', '=', applicant.email_from)]):
                candidate['profile'] = employee.getProfile()
                candidate['expList'] = employee.getWorkExperience()
                candidate['eduList'] = employee.getEducationHistory()
                candidate['certList'] = employee.getCertificate()
                candidate['docList'] = employee.getDocument()
            candidateList.append(candidate)
        return candidateList

    @api.one
    def deleteInterview(self):
        if self.status == 'initial':
            self.unlink()
            return True
        return False

    @api.one
    def getInterviewStatistic(self):
        applicant_count = self.env['hr.applicant'].search_count([('interview_id', '=', self.id)])
        invite_count = self.env['career.email.history'].search_count([('survey_id', '=', self.id)])
        response_count = self.env['survey.user_input'].search_count(
            [('survey_id', '=', self.id), ('state', '=', 'done')])
        return {'applicant': applicant_count, 'invitation': invite_count, 'response': response_count}

    @api.one
    def action_open(self):
        if self.status != 'published' and self.job_id.status == 'published' \
                and not self.env['survey.survey'].search(
                    [('job_id', '=', self.job_id.id), ('status', '=', 'published')]):
            self.write({'status': 'published'})
            return True
        return False

    @api.one
    def action_close(self):
        if self.write({'status': 'closed'}):
            return True
        return False

    @api.one
    def createCandidate(self, candidate):
        if self.job_id.status != 'published' or self.status != 'published':
            return False
        user_input = self.env['survey.user_input'].search([('email', '=', candidate['email']), ('survey_id', '=', self.id)])
        if not user_input:
            user_input = self.env['survey.user_input'].create({'survey_id': self.id, 'deadline': self.job_id.deadline,
                                                               'type': 'link', 'state': 'new', 'email': candidate['email']})
        candidate = self.env['hr.applicant'].search(
            [('email_from', '=', candidate['email']), '|', ('survey', '=', self.id), ('interview_id', '=', self.id)])
        if not candidate:
            candidate = self.env['hr.applicant'].create(
                {'name': candidate['name'] or candidate['email'], 'email_from': candidate['email'], 'job_id': self.job_id.id, 'interview_id': self.id,
                 'company_id': self.job_id.company_id.id, 'response_id': user_input.id})
        return candidate


class InterviewQuestion(models.Model):
    _name = 'survey.question'
    _inherit = 'survey.question'

    response = fields.Integer(string="Response time limit for one question")
    retry = fields.Integer(string="Number of attempts for one question, -1 means unlimited")
    prepare = fields.Integer(string="Prepare time for one question, -1 means unlimited", default=1)
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
    answer_type = fields.Selection(
        [('text', 'Text'), ('number', 'Number'), ('date', 'Date'), ('free_text', 'Free Text'),
         ('suggestion', 'Suggestion'), ('url', 'URL')])
    value_video_url = fields.Text(string="URL Video reponse")
