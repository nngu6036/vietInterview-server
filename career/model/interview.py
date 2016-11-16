import string

from openerp import models, fields, api

from .. import util


class Applicant(models.Model):
    _name = 'hr.applicant'
    _inherit = 'hr.applicant'

    shortlist = fields.Boolean(string="Short-listed", default=False)
    interview_id = fields.Many2one('survey.survey', string="Interview to join")
    input_token = fields.Char(string="Input token", related='response_id.token')
    letter = fields.Text(string="Cover letter")

    @api.one
    def getInterviewHistory(self):
        return {'id': self.response_id.id, 'state': self.response_id.state, 'deadline': self.response_id.deadline,
                'wrap_up': self.response_id.wrap_up}

    @api.one
    def getCandidateInfo(self):
        return {'id': self.id, 'name': self.name, 'email': self.email_from}

    @api.one
    def startInterview(self):
        if self.response_id.state == 'new':
            self.response_id.write({'state': 'skip'})
            return True
        return False

    @api.one
    def getInterviewScore(self):
        if self.response_id.state != 'done':
            return 0
        if len(self.response_id.user_input_line_ids) == 0:
            return 0
        return self.response_id.quizz_score * 100 / len(self.response_id.user_input_line_ids)

    @api.one
    def stopInterview(self):
        if self.response_id.state == 'new' or self.response_id.state == 'skip':
            self.response_id.write({'state': 'done'})
            self.env['career.mail_service'].sendInterviewThankyou(self.interview_id.id, self.email_from)
            return True
        return False

    @api.one
    def submitInterviewAnswer(self, questionId, videoUrl):
        if self.response_id.state == 'skip':
            self.response_id.write({'state': 'skip'})
            self.env['survey.user_input_line'].create({'user_input_id': self.response_id.id, 'question_id': questionId,
                                                       'skipped': False,
                                                       'answer_type': 'url',
                                                       'value_video_url': videoUrl})
            return True
        return False

    @api.one
    def submitQuizAnswer(self, questionId, optionId):
        if self.response_id.state == 'skip':
            self.response_id.write({'state': 'skip'})
            option = self.env['survey.label'].browse(optionId)
            self.env['survey.user_input_line'].create({'user_input_id': self.response_id.id, 'question_id': questionId,
                                                       'skipped': False,
                                                       'answer_type': 'suggestion',
                                                       'value_suggested': optionId,
                                                       'quizz_mark':option.quizz_mark})
            return True
        return False

    @api.one
    def attachDocument(self, file_name, file_location, comment):
        self.env['ir.attachment'].create({'name': comment, 'description': comment,
                                          'res_model': 'hr.applicant', 'res_id': self.id,
                                          'company_id': self.company_id.id, 'type': 'binary',
                                          'store_fname': file_location, 'datas_fname': file_name})
        return True


class ConferenceMember(models.Model):
    _name = 'career.conference_member'

    name = fields.Text(string="Member name")
    member_id = fields.Char(string="Member ID")
    meeting_id = fields.Char(string="Meeting ID", related='conference_id.meeting_id')
    role = fields.Selection([('moderator', 'Moderator'), ('guest', 'Participant'), ('candidate', 'Candidate')],
                            default='guest')
    access_code = fields.Char(string="Conference access code")
    conference_id = fields.Many2one('career.conference', string="Conference to join")
    rec_model = fields.Char(string="Record model")
    rec_id = fields.Integer(string="Record ID")

    @api.model
    def create(self, vals):
        vals['member_id'] = util.id_generator(24, string.digits)
        conf = super(ConferenceMember, self).create(vals)
        return conf

    @api.multi
    def getMeetingInfo(self):
        self.ensure_one()
        info = {}
        info['status'] = self.conference_id.status
        if self.conference_id.status != 'ended':
            for member in self.conference_id.member_ids:
                if member.role == 'moderator':
                    info['moderator'] = {'name': member.name, 'role': member.role, 'memberId': member.member_id,
                                         'meetingId': member.meeting_id}
                    questions = self.env['survey.question'].search(
                        [('survey_id', '=', self.conference_id.interview_id.id)])
                    info['questionList'] = [
                        {'id': q.id, 'title': q.question, 'response': q.response, 'retry': q.retry,
                         'prepare': q.prepare, 'videoUrl': q.videoUrl, 'source': q.source,
                         'type': q.mode, 'order': q.sequence} for q in questions]
                if member.role == 'candidate':
                    info['candidate'] = {'name': member.name, 'role': member.role, 'memberId': member.member_id,
                                         'meetingId': member.meeting_id}
                    for applicant in self.env[member.rec_model].browse(member.rec_id):
                        for question in info['questionList']:
                            question['attempted'] = self.env['survey.user_input_line'].search_count(
                                [('user_input_id', '=', applicant.response_id.id),
                                 ('question_id', '=', question['id'])]) == 1
            job = self.conference_id.interview_id.job_id
            info['job'] = {'name': job.name, 'description': job.description, 'deadline': job.deadline,
                           'status': job.status,
                           'requirements': job.requirements, 'company': job.company_id.name,
                           'country': job.country_id.name,
                           'province': job.province_id.name, 'createDate': job.create_date}
        return info

    @api.multi
    def submitInterviewAnswer(self, candidateMemberId, questionId, videoUrl):
        self.ensure_one()
        if self.role != 'moderator':
            return False
        for member in self.env['career.conference_member'].search(
                [('member_id', '=', candidateMemberId), ('meeting_id', '=', self.meeting_id)]):
            for applicant in self.env[member.rec_model].browse(member.rec_id):
                applicant.response_id.write({'state': 'skip'})
                answer = self.env['survey.user_input_line'].search(
                    [('user_input_id', '=', applicant.response_id.id), ('question_id', '=', questionId)])
                if not answer:
                    self.env['survey.user_input_line'].create(
                        {'user_input_id': applicant.response_id.id, 'question_id': questionId,
                         'skipped': False,
                         'answer_type': 'url',
                         'value_video_url': videoUrl})
                else:
                    answer.write({'skipped': False, 'answer_type': 'url', 'value_video_url': videoUrl})
                return True
        return False

    @api.multi
    def submitAssessment(self, candidateMemberId, assessmentResult):
        self.ensure_one()
        if self.role != 'moderator':
            return False
        for employer in self.env[self.rec_model].browse(self.rec_id):
            for candidate_member in self.env['career.conference_member'].search(
                    [('member_id', '=', candidateMemberId), ('meeting_id', '=', self.meeting_id)]):
                for applicant in self.env[candidate_member.rec_model].browse(candidate_member.rec_id):
                    assessmentResult['candidateId'] = applicant.id
                    assessmentResult['answerList'] = {}
                    return employer.submitAssessment(assessmentResult)
        return False


class Conference(models.Model):
    _name = 'career.conference'

    name = fields.Text(string="Conference name")
    meeting_id = fields.Char(string="Metting ID")
    applicant_id = fields.Many2one('hr.applicant', string="Candidate")
    company_id = fields.Many2one(string='Company', related='applicant_id.company_id')
    access_code = fields.Char(string="Conference access code")
    mod_access_code = fields.Char(string="Conference moderator access code")
    interview_id = fields.Many2one('survey.survey', string='Interview')
    language = fields.Char(string='Language', related='interview_id.language')
    member_ids = fields.One2many('career.conference_member', 'conference_id')
    schedule = fields.Datetime("Interview schedule")
    status = fields.Selection([('pending', 'Initial status'), ('started', 'Start status'), ('ended', 'Closed status')],
                              default='pending')

    @api.multi
    def action_open(self):
        self.ensure_one()
        self.write({'status': 'started'})
        return True

    @api.multi
    def action_end(self):
        self.ensure_one()
        self.write({'status': 'ended'})
        return True

    @api.model
    def create(self, vals):
        vals['access_code'] = util.id_generator(12, string.digits)
        vals['mod_access_code'] = util.id_generator(12, string.digits)
        conf = super(Conference, self).create(vals)
        return conf

    @api.multi
    def action_launch(self):
        self.ensure_one()
        if not self.env['career.conference_service'].openMeeting(self.id):
            return False
        return {'id': self.id, 'name': self.name, 'meetingId': self.meeting_id, 'moderatorPwd': self.mod_access_code}


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
    mode = fields.Selection([('conference', 'Conference interview'), ('video', 'Video interview'),('quiz', 'Quiz interview')], default='video')
    round = fields.Integer(string="Interview round number", default=1)
    quest_num = fields.Integer("Number of question")
    benchmark = fields.Integer("Number of correct answer to pass the test")
    shuffle = fields.Boolean("Randomize the question order")
    quiz_time = fields.Integer("Total quiz time in second")

    @api.model
    def create(self, vals):
        if 'job_id' in vals:
            vals['round'] = self.env['survey.survey'].search_count([('job_id', '=', vals['job_id'])]) + 1
        interview = super(Interview, self).create(vals)
        return interview

    @api.one
    def updateInterview(self, vals):
        self.write({'title': vals['name'], 'response': int(vals['response']) if 'response' in vals else False,
                    'retry': int(vals['retry']) if 'retry' in vals else False,
                    'introUrl': vals['introUrl'],
                    'mode': vals['mode'],
                    'exitUrl': vals['exitUrl'],
                    'prepare': int(vals['prepare']) if 'prepare' in vals else False,
                    'language': vals['language'] if 'language' in vals else False,
                    'quest_num': int(vals['questionNum']) if 'questionNum' in vals else False,
                    'benchmark': int(vals['benchmark']) if 'benchmark' in vals else False,
                    'shuffle': bool(vals['shuffle']) if 'shuffle' in vals else False,
                    'quiz_time': int(vals['quizTime']) if 'quizTime' in vals else False
                    })
        return True

    @api.multi
    def addInterviewQuestion(self, jQuestions):
        self.ensure_one()
        questionIds = []
        print jQuestions
        for jQuestion in jQuestions:
            page = self.env['survey.page'].create({'title': 'Single Page', 'survey_id': self.id})
            question_type = 'free_text' if self.mode!='quiz' else 'simple_choice'
            question = self.env['survey.question'].create(
                {'question': jQuestion['title'],
                 'response': int(jQuestion['response']) if 'response' in jQuestion else False,
                 'retry': int(jQuestion['retry']) if 'retry' in jQuestion else False,
                 'videoUrl': jQuestion['videoUrl'],
                 'prepare': int(jQuestion['prepare']) if 'prepare' in jQuestion else False,
                 'source': jQuestion['source'], 'mode': jQuestion['type'], 'page_id': page.id,
                 'type':question_type,
                 'sequence': int(jQuestion['order']), 'survey_id': self.id})
            if self.mode=='quiz':
                for jOption in jQuestion['options']:
                    option = self.env['survey.label'].create(
                        {'question_id': question.id,
                         'value': jOption['title'], 'quizz_mark': 1 if jOption['correct'] else -1})
            questionIds.append(question.id)
        return questionIds

    @api.multi
    def getInterviewQuestion(self):
        self.ensure_one()
        questions = self.env['survey.question'].search([('survey_id', '=', self.id)])
        if self.mode != 'quiz':
            questionList = [
                {'id': q.id, 'title': q.question, 'response': q.response, 'retry': q.retry, 'videoUrl': q.videoUrl,
                'source': q.source, 'type': q.mode, 'order': q.sequence, 'prepare': q.prepare} for q in questions]
        else:
            questionList = [
                {'id': q.id, 'title': q.question, 'source': q.source, 'order': q.sequence,
                 'options': [{'id': o.id, 'title': o.value, 'correct': True if o.quizz_mark > 0 else False} for o in
                             q.labels_ids]} for q in questions]
        return questionList

    @api.multi
    def getInterviewResponse(self):
        self.ensure_one()
        responseList = []
        for input in self.env['survey.user_input'].search([('survey_id', '=', self.id)]):
            for applicant in self.env['hr.applicant'].search(
                    [('email_from', '=', input.email), ('response_id', '=', input.id)]):
                response = {}
                response['candidate'] = {'id': applicant.id, 'name': applicant.name, 'email': applicant.email_from,
                                         'shortlist': applicant.shortlist,
                                         'score': applicant.getInterviewScore(),
                                         'pass': applicant.getInterviewScore() >= self.benchmark,
                                         'invited': True if self.env['career.email.history'].search(
                                             [('applicant_id', '=', applicant.id)]) else False}
                response['answerList'] = [
                    {'id': line.id, 'questionId': line.question_id.id, 'videoUrl': line.value_video_url} for line in
                    input.user_input_line_ids]
                documents = self.env['ir.attachment'].search(
                    [('res_model', '=', 'hr.applicant'), ('res_id', '=', applicant[0].id)])
                response['documentList'] = [
                    {'id': doc.id, 'title': doc.name, 'filename': doc.datas_fname, 'filedata': doc.store_fname} for doc
                    in documents]
                responseList.append(response)
        return responseList

    @api.multi
    def getCandidate(self):
        self.ensure_one()
        candidateList = []
        for applicant in self.env['hr.applicant'].search(
                ['|', ('interview_id', '=', self.id), ('job_id', '=', self.job_id.id)]):
            candidate = {'id': applicant.id, 'name': applicant.name, 'email': applicant.email_from,
                         'shortlist': applicant.shortlist,
                         'round':applicant.interview_id.round,
                         'score': applicant.getInterviewScore(),
                         'pass':applicant.getInterviewScore() >= self.benchmark,
                         'invited': True if self.env['career.email.history'].search([('survey_id', '=', self.id),
                                                                                     ('email', '=',
                                                                                      applicant.email_from)]) else False}
            for conference in self.conference_ids:
                if conference.applicant_id.id == applicant.id:
                    candidate['schedule'] = conference.schedule
            for employee in self.env['career.employee'].search([('login', '=', applicant.email_from)]):
                candidate['employeeId'] = employee.id
                candidate['profile'] = employee.getProfile()
                candidate['expList'] = employee.getWorkExperience()
                candidate['eduList'] = employee.getEducationHistory()
                candidate['certList'] = employee.getCertificate()
                candidate['docList'] = employee.getDocument()
                candidate['viewed'] = self.env['career.employee.history'].search_count(
                    [('employee_id', '=', employee.id), ('company_id', '=', self.job_id.company_id.id)]) > 0
            candidateList.append(candidate)
        return candidateList

    @api.multi
    def deleteInterview(self):
        if self.status == 'initial':
            self.unlink()
            return True
        return False

    @api.multi
    def getInterviewStatistic(self):
        self.ensure_one()
        applicant_count = self.env['hr.applicant'].search_count([('interview_id', '=', self.id)])
        invite_count = self.env['career.email.history'].search_count([('survey_id', '=', self.id)])
        response_count = self.env['survey.user_input'].search_count(
            [('survey_id', '=', self.id), ('state', '=', 'done')])
        return {'applicant': applicant_count, 'invitation': invite_count, 'response': response_count}

    @api.multi
    def action_open(self):
        self.ensure_one()
        if self.status != 'published' and self.job_id.status == 'published' and not self.env['survey.survey'].search(
                [('job_id', '=', self.job_id.id), ('status', '=', 'published')]):
            self.write({'status': 'published'})
            return True
        return False

    @api.multi
    def action_close(self):
        self.ensure_one()
        if self.write({'status': 'closed'}):
            return True
        return False

    @api.multi
    def createCandidate(self, vals):
        self.ensure_one()
        if self.job_id.status != 'published' or self.status != 'published':
            return False
        user_input = self.env['survey.user_input'].search([('email', '=', vals['email']), ('survey_id', '=', self.id)])
        if not user_input:
            user_input = self.env['survey.user_input'].create({'survey_id': self.id, 'deadline': self.job_id.deadline,
                                                               'type': 'link', 'state': 'new', 'email': vals['email']})
        createNew = False
        candidate = self.env['hr.applicant'].search([('email_from', '=', vals['email'])])
        if not candidate:
            candidate = self.env['hr.applicant'].search(
                [('email_from', '=', vals['email']), '|', ('survey', '=', self.id), ('interview_id', '=', self.id)])
            if candidate:
                candidate.write({'interview_id': self.id})
            else:
                createNew = True
        else:
            createNew = True
        if createNew:
            candidate = self.env['hr.applicant'].create(
                {'name': vals['name'] or vals['email'], 'email_from': vals['email'], 'job_id': self.job_id.id,
                 'interview_id': self.id,
                 'company_id': self.job_id.company_id.id, 'response_id': user_input.id})
        return candidate

    @api.multi
    def getInterview(self):
        self.ensure_one()
        return {'id': self.id, 'name': self.title, 'response': self.response,
                'prepare': self.prepare,'status':self.status,'mode':self.mode,'round':self.round,
                'retry': self.retry, 'introUrl': self.introUrl, 'exitUrl': self.exitUrl,'language':self.language,
                'aboutUsUrl': self.aboutUsUrl,'benchmark':self.benchmark,'quizTime':self.quiz_time,'shuffle':self.shuffle}


class InterviewQuestion(models.Model):
    _name = 'survey.question'
    _inherit = 'survey.question'

    response = fields.Integer(string="Response time limit for one question")
    retry = fields.Integer(string="Number of attempts for one question, -1 means unlimited")
    prepare = fields.Integer(string="Prepare time for one question, -1 means unlimited", default=1)
    source = fields.Selection([('manual', 'User-defined'), ('system', 'System question')], default='system')
    mode = fields.Selection([('text', 'Reading'), ('video', 'Watching')], default='video')
    videoUrl = fields.Text(string="Question Video URL")

    @api.one
    def updateInterviewQuestion(self, vals):
        self.write(
            {'question': vals['title'],
             'response': int(vals['response']) if 'response' in vals else False,
             'retry': int(vals['retry']) if 'retry' in vals else False,
             'videoUrl': vals['videoUrl'],
             'prepare': int(vals['prepare']) if 'prepare' in vals else False,
             'source': vals['source'], 'mode': vals['type'],
             'sequence': int(vals['order'])})
        return True

    @api.one
    def removeInterviewQuestion(self):
        self.page_id.unlink()
        self.unlink()
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
