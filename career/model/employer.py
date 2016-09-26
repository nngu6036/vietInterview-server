import datetime
from datetime import date, timedelta

from openerp import models, fields, api


class CompanyUser(models.Model):
    _name = 'career.employer'
    _inherits = {'res.users': 'user_id'}

    user_id = fields.Many2one('res.users', string='User', required=True)
    login = fields.Char(string='Login name', related='user_id.login')
    company_id = fields.Many2one(string='Company', related='user_id.company_id')
    password = fields.Char(string='Password', related='user_id.password')
    name = fields.Char(string='Name', related='user_id.name')

    @api.one
    def createAssignment(self, vals):
        catIdList = vals['categoryIdList']
        address = self.env['res.partner'].create({'name': vals['name'], 'type': 'contact',
                                                  'country_id': 'countryId' in vals and int(vals['countryId']),
                                                  'state_id': 'provinceId' in vals and int(vals['provinceId']),
                                                  'company_id': self.user_id.company_id.id})
        assignment = self.env['hr.job'].create({'name': vals['name'], 'description': vals['description'],
                                                'deadline': vals['deadline'], 'company_id': self.user_id.company_id.id,
                                                'requirements': vals['requirements'] or False,
                                                'category_ids': [(6, 0, catIdList)],
                                                'position_id': int(
                                                    vals['positionId']) if 'positionId' in vals else False,
                                                'address_id': address.id, 'state': 'open'})
        self.env['career.mail_service'].sendNewJobNotification(assignment.id)
        return assignment.id

    @api.one
    def updateCompanyUser(self, vals):
        self.user_id.write({'name': vals['name'], 'password': vals['password']})
        return True

    @api.one
    def deleteCompanyUser(self, vals):
        if self.user_id.unlink():
            return True
        else:
            return False

    @api.one
    def getCompanyInfo(self):
        return {'id': self.company_id.id, 'name': self.company_id.name, 'image': self.company_id.logo or False,
                'email': self.company_id.partner_id.email, 'videoUrl': self.company_id.partner_id.videoUrl,
                'description': self.company_id.partner_id.description, 'street': self.company_id.partner_id.street,
                'street2': self.company_id.partner_id.street2, 'zip': self.company_id.partner_id.zip,
                'city': self.company_id.partner_id.city, 'stateId': self.company_id.partner_id.state_id.id,
                'countryId': self.company_id.partner_id.country_id.id, 'vat': self.company_id.partner_id.vat,
                'phone': self.company_id.partner_id.phone}

    @api.one
    def createInterview(self, assignmentId, vals):
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.company_id.id == self.company_id.id:
                interview = self.env['survey.survey'].create(
                    {'title': vals['name'], 'response': int(vals['response']) if 'response' in vals else False,
                     'retry': int(vals['retry']) if 'retry' in vals else False,
                     'introUrl': vals['introUrl'], 'job_id': assignmentId,
                     'exitUrl': vals['exitUrl'],
                     'prepare': int(vals['prepare']) if 'prepare' in vals else False,
                     'language': vals['language'] if 'language' in vals else False,
                     'round': int(vals['round']) if 'roumd' in vals else False,
                     'aboutUsUrl': self.company_id.partner_id.videoUrl,
                     'mode': vals['mode'] if 'mode' in vals else False})

                return interview.id
        return False

    @api.one
    def getConference(self):
        conferences = self.env['career.conference'].search([('company_id', '=', self.company_id.id)])
        conferenceList = [
            {'id': c.id, 'name': c.name, 'language': c.language, 'meetingId': c.meeting_id,
             'job': c.interview_id.job_id.name, 'interview': c.interview_id.round, 'candidate': c.applicant_id.name,
             'schedule': c.schedule, 'status': c.status,
             'memberList': [{'name': m.name, 'memberId': m.member_id, 'role': m.role} for m in c.member_ids]} for c in
            conferences]
        return conferenceList

    @api.one
    def submitAssessment(self, assessmentResult):
        company = self.user_id.company_id
        hr_interview_assessment = self.env['hr.evaluation.interview'].search(
            [('user_id', '=', self.user_id.id), ('applicant_id', '=', int(assessmentResult['candidateId']))])
        if not hr_interview_assessment:
            hr_eval_phase = self.env['hr_evaluation.plan.phase'].search([('company_id', '=', company['id'])])
            hr_eval = self.env['hr_evaluation.evaluation'].create({'employee_id': self.id,
                                                                   'plan_id': hr_eval_phase.plan_id.id,
                                                                   'state': 'progress'})
            hr_interview_assessment = self.env['hr.evaluation.interview'].create(
                {'evaluation_id': hr_eval.id, 'phase_id': hr_eval_phase.id,
                 'applicant_id': int(assessmentResult['candidateId']), 'state': 'done', 'user_id': self.user_id.id})
        hr_interview_assessment.write(
            {'rating': int(assessmentResult['vote']), 'note_summary': assessmentResult['comment']})
        for jAns in assessmentResult['answerList']:
            if not self.env['survey.user_input_line'].search(
                    [('user_input_id', '=', hr_interview_assessment[0].request_id.id),
                     ('question_id', '=', int(jAns['questionId']))]):
                self.env['survey.user_input_line'].create({'user_input_id': hr_interview_assessment[0].request_id.id,
                                                           'question_id': int(jAns['questionId']),
                                                           'answer_type': 'number',
                                                           'value_number': int(jAns['answer'])})
        return hr_interview_assessment.id

    @api.one
    def getSelfAssessment(self, assessmentId, applicantId):
        hr_interview_assessment = self.env['hr.evaluation.interview'].search(
            [('applicant_id', '=', applicantId), ('user_id', '=', self.user_id.id)])
        answerList = [{'id': answer.id, 'questionId': answer.question_id.id, 'answer': answer.value_number}
                      for answer in hr_interview_assessment.request_id.user_input_line_ids]
        return {'id': hr_interview_assessment.id, 'comment': hr_interview_assessment.note_summary,
                'vote': hr_interview_assessment.rating, 'answerList': answerList}

    @api.one
    def shortlistCandidate(self, applicantId):
        for applicant in self.env['hr.applicant'].browse(applicantId):
            applicant.write({'shortlist': not applicant.shortlist})
        return True

    @api.one
    def getOtherAssessment(self, assessmentId, applicantId):
        assessmentResultList = []
        for hr_interview_assessment in self.env['hr.evaluation.interview'].search(
                [('applicant_id', '=', applicantId), ('user_id', '!=', self.user_id.id)]):
            assessmentResultList.append(
                {'answertList': [{'id': answer.id, 'questionId': answer.question_id.id, 'answer': answer.value_number}
                                 for answer in hr_interview_assessment.request_id.user_input_line_ids],
                 'id': hr_interview_assessment.id, 'comment': hr_interview_assessment.note_summary,
                 'vote': hr_interview_assessment.rating,
                 'user': hr_interview_assessment.user_id.name})
        return assessmentResultList

    @api.one
    def inviteCandidate(self, jsCandidates, subject, interviewId):
        for jsCandidate in jsCandidates:
            for interview in self.env['survey.survey'].browse(interviewId):
                for candidate in interview.createCandidate(jsCandidate):
                    if interview.mode == 'video':
                        self.env['career.mail_service'].sendVideoInterviewInvitation(candidate, subject)
                    if interview.mode == 'conference':
                        self.scheduleMeeting(candidate, jsCandidate['schedule'])
                        self.env['career.mail_service'].sendConferenceInvitation(candidate, subject)
        return True

    @api.one
    def scheduleMeeting(self, candidate, schedule):
        meeting = self.env['career.conference'].search([('applicant_id', '=', candidate.id)])
        if not meeting:
            meeting = self.env['career.conference'].create(
                {'name': candidate.interview_id.title, 'applicant_id': candidate.id,
                 'interview_id': candidate.interview_id.id,
                 'schedule': schedule, 'meeting_id': candidate.response_id.token})
            mode_member = self.env['career.conference_member'].create({'name': self.name, 'role': 'moderator',
                                                                       'access_code': meeting.mod_access_code,
                                                                       'conference_id': meeting.id,
                                                                       'rec_model': self._name, 'rec_id': self.id})
            candidate_member = self.env['career.conference_member'].create({'name': candidate.name, 'role': 'candidate',
                                                                            'access_code': meeting.access_code,
                                                                            'conference_id': meeting.id,
                                                                            'rec_model': 'hr.applicant',
                                                                            'rec_id': candidate.id})
            candidate.write({'member': candidate_member.id})
        return meeting

    @api.one
    def updateAssignment(self, vals):
        for assignment in self.env['hr.job'].browse(int(vals['id'])):
            if assignment.company_id.id == self.company_id.id:
                return assignment.updateAssignment(vals)
        return False

    @api.one
    def updateInterview(self, vals):
        for interview in self.env['survey.survey'].browse(int(vals['id'])):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.updateInterview(vals)
        return False

    @api.one
    def openAssignment(self, assignmentId):
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.company_id.id == self.company_id.id:
                return assignment.action_open()
        return False

    @api.one
    def closeAssignment(self, assignmentId):
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.company_id.id == self.company_id.id:
                return assignment.action_close()
        return False

    @api.one
    def deleteAssignment(self, assignmentId):
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.company_id.id == self.company_id.id:
                return assignment.deleteAssignment()
        return False

    @api.one
    def getInterviewList(self, assignmentId):
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.company_id.id == self.company_id.id:
                return assignment.getInterviewList()
        return False

    @api.one
    def openInterview(self, interviewId):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.action_open()
        return False

    @api.one
    def closeInterview(self, interviewId):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.action_close()
        return False

    @api.one
    def deleteInterview(self, interviewId):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.deleteInterview()
        return False

    @api.one
    def getInterviewResponse(self, interviewId):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.getInterviewResponse()
        return False

    @api.one
    def getCandidateByInterview(self, interviewId):
        print interviewId
        for interview in self.env['survey.survey'].browse(interviewId):
            print interview
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.getCandidate()
        return False

    @api.one
    def getCandidate(self, start=None, length=None, count=True):
        candidateList = []
        total = 0
        if count:
            total = self.env['hr.applicant'].search_count([('company_id', '=', self.company_id.id)])
        for applicant in self.env['hr.applicant'].search([('company_id', '=', self.company_id.id)], limit=int(length),
                                                         offset=int(start), order='create_date desc'):
            candidate = {}
            candidate['jobId'] = applicant.job_id.id
            candidate['jobName'] = applicant.job_id.name
            for employee in self.env['career.employee'].search([('login', '=', applicant.email_from)]):
                candidate['employeeId'] = employee.id
                candidate['profile'] = employee.getProfile()
                candidate['expList'] = employee.getWorkExperience()
                candidate['eduList'] = employee.getEducationHistory()
                candidate['certList'] = employee.getCertificate()
                candidate['docList'] = employee.getDocument()
            candidateList.append(candidate)
        return {'result': True, 'candidateList': candidateList, 'total': total}

    @api.one
    def addInterviewQuestion(self, interviewId, jQuestions):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.addInterviewQuestion(jQuestions)
        return False

    @api.one
    def getInterviewQuestion(self, interviewId):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.getInterviewQuestion()
        return False

    @api.one
    def updateInterviewQuestion(self, jQuestions):
        for jQuestion in jQuestions:
            self.env['survey.question'].browse(int(jQuestion['id'])).updateInterviewQuestion(jQuestion)
        return True

    @api.one
    def removeInterviewQuestion(self, jIds):
        for id in jIds:
            self.env['survey.question'].browse(id).removeInterviewQuestion()
        return True

    @api.one
    def openConference(self, conferenceId):
        for conference in self.env['career.conference'].browse(conferenceId):
            if conference.interview_id.job_id.company_id.id == self.company_id.id:
                return conference.action_open()
        return False

    @api.one
    def closeConference(self, conferenceId):
        for conference in self.env['career.conference'].browse(conferenceId):
            if conference.interview_id.job_id.company_id.id == self.company_id.id:
                return conference.action_end()
        return False

    @api.one
    def getInterviewStatistic(self, interviewId):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.getInterviewStatistic()
        return False

    @api.one
    def getAssessmentSummaryReport(self, candidateId):
        for candidate in self.env['hr.applicant'].browse(candidateId):
            if candidate.company_id.id == self.company_id.id:
                return self.env['career.report_service'].getAssessmentSummaryReport(candidateId)
        return False

    @api.one
    def searchEmployee(self, options):
        employeeList = []
        domain = []
        if options:
            if options['countryId']:
                domain.append(('country_id', '=', int(options['countryId'])))
            if options['provinceId']:
                domain.append(('state_id', '=', int(options['provinceId'])))
        categoryId = int(options['categoryId']) if 'categoryId' in options and options['categoryId'] != '' else False
        positionId = int(options['positionId']) if 'positionId' in options and options['positionId'] != '' else False
        keyword = options['keyword'] if 'keyword' in options and options['keyword'] != '' else False
        for e in self.env['career.employee'].search(domain):
            latest_exp = self.env['career.work_experience'].search([('employee_id', '=', e.id)], offset=0, limit=1,
                                                                   order='start_date desc')
            match = True
            if match and positionId:
                if not latest_exp or not latest_exp.position_id:
                    continue
                if positionId != latest_exp[0].position_id.id:
                    continue
                match = True
            if match and categoryId:
                match = False
                for exp in e.experience_ids:
                    if categoryId in exp.cat_ids.ids:
                        match = True
                        break
            if match and keyword:
                match = False
                if keyword in e.user_id.partner_id.email:
                    match = True
                if not match:
                    for exp in e.experience_ids:
                        if keyword.lower() in exp.title.lower() or keyword.lower() in exp.employer.lower() \
                                or keyword.lower() in exp.description.lower():
                            match = True
                            break
            if match:
                employeeList.append({'employeeId': e.id, 'name': e.name, 'provinceId': e.partner_id.state_id.id,
                                     'countryId': e.partner_id.country_id.id, 'positionID': latest_exp.position_id.ids,
                                     'categoryIds': list(latest_exp.cat_ids.ids),
                                     'viewed': self.env['career.employee.history'].search_count(
                                         [('employee_id', '=', e.id),
                                         ('company_id', '=', self.company_id.id)]) > 0})
        return employeeList

    @api.one
    def getEmployeeDetail(self, employeeId):
        for employee in self.env['career.employee'].browse(employeeId):
            cost = 0
            for exp in employee.experience_ids.sorted(key=lambda r: r.start_date):
                for license_rule in self.company_id.license_instance_id.license_id.rule_ids:
                    if license_rule.position_id.id == exp.position_id.id:
                        if license_rule.cost > cost:
                            cost = license_rule.cost
            employeeDetail = {'name': employee.user_id.name}
            employeeDetail['profile'] = employee.getProfile()
            employeeDetail['expList'] = employee.getWorkExperience()
            employeeDetail['eduList'] = employee.getEducationHistory()
            employeeDetail['certList'] = employee.getCertificate()
            employeeDetail['docList'] = employee.getDocument()
            employeeDetail['viewed'] = self.env['career.employee.history'].search_count(
                [('employee_id', '=', employeeId), ('company_id', '=', self.company_id.id)]) > 0
            employeeDetail['cost'] = cost
            return employeeDetail
        return False

    @api.one
    def viewContactInfo(self, employeeId):
        license_service = self.env['career.license_service']
        if not license_service.validateLicense(self.company_id.id):
            print "License error ", self.company_id.name
            return False
        license_service.consumeEmployee(self.company_id.id, self.id, employeeId)
        return True

    @api.one
    def searchEmployeeByEmail(self, email):
        employee = [{'employeeId': e.id, 'name': e.user_id.name, 'email': e.user_id.login,
                     'profile': e.getProfile(),
                     'expList': e.getWorkExperience(),
                     'eduList': e.getEducationHistory(),
                     'certList': e.getCertificate(),
                     'docList': e.getDocument(),
                     'viewed': self.env['career.employee.history'].search_count(
                         [('employee_id', '=', e.id), ('company_id', '=', self.company_id.id)]) > 0
                     } for e in self.env['career.employee'].search([('login', '=', email)])]
        return employee
