from openerp import models, fields, api, tools
from openerp.osv import osv
from openerp.service import common
import base64
import json
import datetime
from datetime import date, timedelta

class CompanyProfile(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    description = fields.Char(string="Description")

class LicenseCategory(models.Model):
    _name = 'career.license_category'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='License category code')

    @api.model
    def createLicenseCategory(self, vals):
        licenseCategory = self.env['career.license_category'].create(
            {'name': vals['name'], 'code': vals['code']})
        return licenseCategory.id

    @api.model
    def getLicenseCategory(self):
        licenseCategories = self.env['career.license_category'].search([])
        licenseCategoryList = [
            {'id': l.id, 'name': l.name, 'code': l.code} for l in licenseCategories]
        return licenseCategoryList


class LicenseRule(models.Model):
    _name = 'career.license_rule'

    name = fields.Char(string='Name', required=True)
    cost = fields.Integer(string='Cost per action on entry')
    position_id = fields.Many2one('career.job_position',string='Job position')
    license_id = fields.Many2one('career.license',string='License')
    type = fields.Selection([('view', 'View employee action')], default='view')

class License(models.Model):
    _name = 'career.license'

    name = fields.Char(string='Name', required=True)
    assignment = fields.Integer(string='Assignment limit')
    email = fields.Integer(string='Email limit')
    point = fields.Integer(string='Point limit')
    validity = fields.Integer(string='Validity period')
    cat_id = fields.Many2one('career.license_category', string='License category')
    rule_ids = fields.One2many('career.license_rule', 'license_id', 'License rule')

    @api.model
    def createLicense(self, vals):
        license = self.env['career.license'].create(
            {'name': vals['name'], 'email': int(vals['email']), 'point': int(vals['point']),'assignment': int(vals['assignment']),
             'validity': int(vals['validity']), 'cat_id': int(vals['categoryId'])})
        return license.id

    @api.model
    def getLicense(self):
        licenses = self.env['career.license'].search([])
        licenseList = [
            {'id': l.id, 'name': l.name,'point':l.point, 'email': l.email, 'assignment': l.assignment, 'validity': l.validity,
             'createDate': l.create_date, 'categoryId': l.cat_id.id} for l in licenses]
        return licenseList


class LicenseInstance(models.Model):
    _name = 'career.license_instance'

    license_id = fields.Many2one('career.license', string="License")
    expire_date = fields.Date(string="Expired date")
    effect_date = fields.Date(string="Effective date ")
    state = fields.Selection([('initial', 'Initial state'), ('suspend', 'Suspended state'), ('active', 'Active state'),
                              ('closed', 'Closed state')], default='initial')
    email_history_ids = fields.One2many('career.email.history', 'license_instance_id', 'Email history')

    @api.multi
    def isEnabled(self):
        self.ensure_one()
        if self.state != 'active':
            return False
        if not self.expire_date:
            return True
        expire_date = datetime.datetime.strptime(self.expire_date, "%Y-%m-%d")
        if expire_date < datetime.datetime.now():
            return False
        return True


class LicenseEmailHistory(models.Model):
    _name = 'career.email.history'

    applicant_id = fields.Many2one('hr.applicant', string='Applicant ')
    company_id = fields.Many2one('res.company', related='employer_id.company_id')
    email = fields.Char(string='email', related='applicant_id.email_from')
    assignment_id = fields.Many2one(string='Job', related='applicant_id.job_id')
    survey_id = fields.Many2one('survey.survey', related='applicant_id.interview_id')
    date_send = fields.Date(string="Send date")
    employer_id = fields.Many2one('career.employer', string='Employer user')
    license_instance_id = fields.Many2one('career.license_instance', string='Applied license')

class LicenseViewEmployeeHistory(models.Model):
    _name = 'career.employee.history'

    employee_id = fields.Many2one('career.employee', string='Employee ')
    position_id = fields.Many2one('career.job_position', string='Employee position ')
    cost = fields.Integer( string='View cost ')
    company_id = fields.Many2one('res.company', related='employer_id.company_id')
    employer_id = fields.Many2one('career.employer', string='Employer user')
    license_instance_id = fields.Many2one('career.license_instance', string='Applied license')

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
        print vals
        print vals['positionId']
        assignment = self.env['hr.job'].create({'name': vals['name'], 'description': vals['description'],
                                                'deadline': vals['deadline'], 'company_id': self.user_id.company_id.id,
                                                'requirements': vals['requirements'] or False,
                                                'category_ids': [(6, 0, catIdList)] ,
                                                'position_id':  int(vals['positionId']) if 'positionId' in vals else False,
                                                'address_id': address.id, 'state': 'open'})
        self.env['career.mail_service'].sendNewJobNotification(assignment.id)
        return assignment.id


    @api.one
    def updateCompanyUser(self, vals):
        self.user_id.write({'name': vals['name']})
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
                'description': self.company_id.partner_id.description}

    @api.one
    def createInterview(self, assignmentId, vals):
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.company_id.id == self.company_id.id:
                interview = self.env['survey.survey'].create({'title': vals['name'], 'response':int(vals['response']) if 'response' in vals else False,
                                                              'retry': int(vals['retry']) if 'retry' in vals else False,
                                                              'introUrl': vals['introUrl'], 'job_id': assignmentId,
                                                              'exitUrl': vals['exitUrl'],
                                                              'prepare': int(vals['prepare']) if 'prepare' in vals else False,
                                                              'language': vals['language'] if 'language' in vals else False,
                                                              'round': int(vals['round']) if 'roumd' in vals else False,
                                                              'aboutUsUrl':self.company_id.partner_id.videoUrl,
                                                              'mode': vals['mode'] if 'mode' in vals else False})

                return interview.id
        return False

    @api.one
    def getConference(self):
        conferences = self.env['career.conference'].search([('company_id','=',self.company_id.id)])
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
    def inviteCandidate(self,jsCandidates,subject,interviewId):
        for jsCandidate in jsCandidates:
            for interview in self.env['survey.survey'].browse(interviewId):
                for candidate in interview.createCandidate(jsCandidate):
                    if interview.mode == 'video':
                        self.env['career.mail_service'].sendVideoInterviewInvitation(candidate, subject)
                    if interview.mode == 'conference':
                        self.scheduleMeeting(candidate,jsCandidate['schedule'])
                        self.env['career.mail_service'].sendConferenceInvitation(candidate, subject)
        return True


    @api.one
    def scheduleMeeting(self, candidate,schedule):
        meeting = self.env['career.conference'].search([('applicant_id','=',candidate.id)])
        if not meeting:
            meeting = self.env['career.conference'].create({'name': candidate.interview_id.title, 'applicant_id': candidate.id,'interview_id':candidate.interview_id.id,
                                    'schedule': schedule,'meeting_id':candidate.response_id.token})
            mode_member = self.env['career.conference_member'].create({'name': self.name, 'role': 'moderator',
                 'access_code': meeting.mod_access_code, 'conference_id': meeting.id,'rec_model': self._name,'rec_id': self.id})
            candidate_member = self.env['career.conference_member'].create({'name': candidate.name, 'role': 'candidate',
                                                                       'access_code': meeting.access_code, 'conference_id': meeting.id,
                                                                        'rec_model': 'hr.applicant', 'rec_id': candidate.id})
            candidate.write({'member':candidate_member.id})
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
                return  assignment.getInterviewList()
        return False

    @api.one
    def openInterview(self, interviewId):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return  interview.action_open()
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
                return  interview.getInterviewResponse()
        return False

    @api.one
    def getCandidate(self, interviewId):
        for interview in self.env['survey.survey'].browse(interviewId):
            if interview.job_id.company_id.id == self.company_id.id:
                return interview.getCandidate()
        return False

    @api.one
    def getAllCandidate(self):
        candidateList = []
        for interview in self.env['survey.survey'].search([('status', '=', 'published')]):
            if interview.job_id.company_id.id == self.company_id.id:
                candidates = interview.getCandidate()
                for candidate in candidates:
                    candidate['jobId'] = interview.job_id.id
                    candidateList.append(candidate)
        if candidateList:
            return candidateList
        return False

    @api.one
    def addInterviewQuestion(self, interviewId,jQuestions):
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
    def getInterviewStatistic(self,interviewId):
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
            latest_exp = self.env['career.work_experience'].search([('employee_id','=',e.id)],offset=0,limit=1,
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
                        if keyword.lower() in exp.title.lower() or keyword.lower() in exp.employer.lower()\
                                or keyword.lower() in exp.description.lower():
                            match = True
                            break
            if match:
                employeeList.append({'id': e.id, 'name': e.name, 'provinceId': e.partner_id.state_id.id,
                                     'countryId': e.partner_id.country_id.id, 'positionID': latest_exp.position_id.ids,
                                     'categoryIds': list(latest_exp.cat_ids.ids)})
        return employeeList

    @api.one
    def getEmployeeDetail(self, employeeId):
        for employee in self.env['career.employee'].browse(employeeId):
            employeeDetail = {'name': employee.user_id.name}
            employeeDetail['profile'] = employee.getProfile()
            employeeDetail['expList'] = employee.getWorkExperience()
            employeeDetail['eduList'] = employee.getEducationHistory()
            employeeDetail['certList'] = employee.getCertificate()
            employeeDetail['docList'] = employee.getDocument()
            employeeDetail['viewed'] = self.env['career.employee.history'].search_count([('employee_id','=',employeeId),('company_id','=',self.company_id.id)]) >0
            return employeeDetail
        return False

    @api.one
    def viewContactInfo(self, employeeId):
        license_service = self.env['career.license_service']
        if not license_service.validateLicense(self.company_id.id):
            print "License error ", self.company_id.name
            return False
        license_service.consumeEmployee(self.company_id.id,self.id,employeeId)
        return True

class Conpany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    license_instance_id = fields.Many2one('career.license_instance', string='License')
    expire_date = fields.Date(string='License expire date', related='license_instance_id.expire_date')

    @api.model
    def createCompany(self, vals):
        license = self.env['career.license'].browse(int(vals['licenseId']))
        expiryDdate = date.today() + timedelta(days=license.validity)
        license_instance = self.env['career.license_instance'].create({'license_id': license.id,
                                                                       'expire_date': '%d-%d-%d ' % (
                                                                           expiryDdate.year, expiryDdate.month,
                                                                           expiryDdate.day)})
        company = self.env['res.company'].create(
            {'name': vals['name'], 'logo': vals['image'] if 'image' in vals else False,
             'license_instance_id': license_instance.id})
        company.partner_id.write({'email': vals['email']})
        hr_eval_plan = self.env['hr_evaluation.plan'].create({'name': 'Assessment', 'company_id': company.id})
        assessment_form = self.env.ref('career.assessment_form')
        self.env['hr_evaluation.plan.phase'].create(
            {'name': 'Assessment', 'company_id': company.id, 'plan_id': hr_eval_plan.id,
             'action': 'final', 'survey_id': assessment_form.id})
        return company.id

    @api.one
    def updateCompany(self,vals):
        self.write({'name': vals['name'], 'logo': vals['image'] if 'image' in vals else False})
        self.partner_id.write({'email': vals['email'],'videoUrl': vals['videoUrl'] if 'videoUrl' in vals else False,
                               'description': vals['description'] if 'description' in vals else False})
        return True

    @api.model
    def getCompany(self):
        main_compnay = self.env.ref('base.main_company')
        companys = self.env['res.company'].search([('id', '!=', main_compnay.id)])
        companyList = [{'id': c.id, 'name': c.name, 'image': c.logo or False,'videoUrl':c.partner_id.videoUrl,
                        'licenseId': c.license_instance_id.license_id.id if c.license_instance_id else False,
                        'license': c.license_instance_id.license_id.name if c.license_instance_id else False,
                        'licenseExpire': c.expire_date if c.license_instance_id else False, 'email': c.partner_id.email}
                       for c in companys]
        return companyList

    @api.one
    def createCompanyUser(self, vals):
        user = self.env['res.users'].search([('login', '=', vals['email'])])
        if user:
            print ("Emplyer login %s already exist" % vals['email'])
            return False
        employer_group = self.env.ref('career.employer_group')
        hr_group = self.env.ref('base.group_hr_manager')
        survey_group = self.env.ref('base.group_survey_manager')
        admin_group = self.env.ref('base.group_erp_manager')
        user = self.env['res.users'].create(
            {'login': vals['email'], 'password': vals['password'], 'name': vals['name'], 'notify_email': 'none',
             'email': vals['email']})
        user.write({'company_ids': [(4, self.id)]})
        user.write({'company_id': self.id,
                    'groups_id': [(6, 0, [employer_group.id, hr_group.id, survey_group.id, admin_group.id])]})
        self.env['hr.employee'].create(
            {'address_id': self.partner_id.id, 'work_email': vals['email'], 'name': vals['name'],
             'user_id': user.id, 'company_id': self.id})
        new_employer = self.env['career.employer'].create({'user_id': user.id, 'is_admin': False})
        return new_employer.id

    @api.one
    def getCompanyUser(self):
        userList = []
        for employer in self.env['career.employer'].search([('company_id','=',self.id)]):
                userList.append({'id': employer.id, 'name': employer.name, 'email': employer.login})
        return userList

    @api.one
    def getAssignment(self):
        assignments = self.env['hr.job'].search([('company_id', '=', self.id)])
        assignmentList = [
            {'id': a.id, 'name': a.name, 'description': a.description, 'deadline': a.deadline, 'status': a.status,
             'requirements': a.requirements, 'approved': a.state == 'recruit',
             'countryId': a.country_id.id, 'provinceId': a.province_id.id,
             'createDate': a.create_date,
             'categoryIdList': list(a.category_ids.ids), 'positionId': a.position_id.id} for a in assignments]
        return assignmentList

    @api.one
    def getLicenseStatistic(self):
        stats = {'email': 0, 'point':0,'license': False}
        remain_point = 0
        if self.license_instance_id:
            stats['email'] = self.env['career.email.history'].search_count(
                [('license_instance_id', '=', self.license_instance_id.id)])
            for employeeHistory in self.env['career.employee.history'].search(
                [('license_instance_id', '=', self.license_instance_id.id)]):
                remain_point += employeeHistory.cost
            stats['point'] = remain_point
            stats['license'] = {'name': self.license_instance_id.license_id.name,
                                'email': self.license_instance_id.license_id.email,
                                'assignment': self.license_instance_id.license_id.assignment,
                                'point': self.license_instance_id.license_id.point,
                                'expireDate': self.license_instance_id.expire_date,
                                'state': self.license_instance_id.state,
                                'code':self.license_instance_id.license_id.cat_id.code}
        return stats

