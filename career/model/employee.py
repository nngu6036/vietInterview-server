from openerp import models, fields, api, tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime


class UserProfile(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    gender = fields.Char(string="Gender")


class WorkExperience(models.Model):
    _name = 'career.work_experience'

    title = fields.Text(string="Title")
    employer = fields.Text(string="Employer")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    cat_id = fields.Many2one('career.job_category', string="Reason to leave")
    description = fields.Text(string="Description")
    current = fields.Boolean(string='Is current')
    country_id = fields.Many2one('res.country', string="Country ")
    province_id = fields.Many2one('res.country.state', string="Province ")
    employee_id = fields.Many2one('career.employee', string="Employee")

    @api.model
    def updateWorkExperience(self, vals):
        self.env['career.work_experience'].browse(int(vals['id'])).write(
            {'title': vals['title'], 'employer': vals['employer'], 'start_date': vals['startDate'],
             'end_date': vals['endDate'], 'current': vals['current'], 'cat_id': vals['categoryId'],
             'country_id': int(vals['countryId']), 'province_id': int(vals['provinceId']),
             'description': vals['description']})
        return True

    @api.model
    def removeWorkExperience(self, ids):
        self.env['career.work_experience'].browse(ids).unlink()
        return True


class EducationHistory(models.Model):
    _name = 'career.education_history'

    institute = fields.Text(string="Institute")
    start_date = fields.Date(string="Start date")
    complete_date = fields.Date(string="Complete date")
    program = fields.Text(string="Program")
    status = fields.Selection([('graduated', 'Graduated'), ('enrolled', 'Current enrolled')])
    level_id = fields.Many2one('hr.recruitment.degree', string="Degree ")
    employee_id = fields.Many2one('career.employee', string="Employee")

    @api.model
    def updateEducationHistory(self, vals):
        self.env['career.education_history'].browse(int(vals['id'])).write(
            {'program': vals['program'], 'institute': vals['institute'],
             'complete_date': vals['finishDate'], 'status': vals['status'],
             'level_id': int(vals['levelId'])})
        return True

    @api.model
    def removeEducationHistory(self, ids):
        if self.env['career.education_history'].browse(ids).unlink():
            return True
        return False


class Certificate(models.Model):
    _name = 'career.certificate'

    title = fields.Text(string="Title")
    issuer = fields.Text(string="Issuer")
    issue_date = fields.Date(string="Date of issuer")
    employee_id = fields.Many2one('career.employee', string="Employee")

    @api.model
    def updateCertificate(self, vals):
        self.env['career.certificate'].browse(int(vals['id'])).write({'title': vals['title'], 'issuer': vals['issuer'],
                                                                      'issue_date': vals['issueDate']})
        return True

    @api.model
    def removeCertificate(self, ids):
        if self.env['career.certificate'].browse(ids).unlink():
            return True
        return False


class Document(models.Model):
    _name = 'ir.attachment'
    _inherit = 'ir.attachment'

    @api.model
    def removeDocument(self, ids):
        self.env['ir.attachment'].browse(ids).unlink()
        return True


class EmployeeUser(models.Model):
    _name = 'career.employee'
    _inherits = {'res.users': 'user_id'}

    user_id = fields.Many2one('res.users', string='User', required=True)
    login = fields.Char(string='Login name', related='user_id.login')
    password = fields.Char(string='Password', related='user_id.password')
    name = fields.Char(string='Name', related='user_id.name')
    experience_ids = fields.One2many('career.work_experience', 'employee_id', string="Working experience")
    education_ids = fields.One2many('career.education_history', 'employee_id', string="Education history")
    certificate_ids = fields.One2many('career.certificate', 'employee_id', string="Certificate")

    @api.model
    def createEmployee(self, login, password):
        user = self.env['res.users'].search([('login', '=', login)])
        if user:
            print ("Emplyee login %s already exist" % login)
            return False
        employee_group = self.env.ref('career.employee_group')
        hr_group = self.env.ref('base.group_hr_user')
        survey_group = self.env.ref('base.group_survey_user')
        user = self.env['res.users'].create(
            {'login': login, 'password': password, 'name': login, 'notify_email': 'none',
             'email': login, 'groups_id': [(6, 0, [employee_group.id, hr_group.id, survey_group.id])]})
        employee = self.env['career.employee'].create({'user_id': user.id})
        return employee.id

    @api.model
    def getEmployee(self):
        employees = self.env['career.employee'].search([])
        employeeList = [{'id': e.id, 'name': e.user_id.partner_id.name, 'email': e.user_id.partner_id.email, 'mobile': e.user_id.partner_id.mobile or False,
                         'countryId': e.user_id.partner_id.country_id.id} for e in employees]
        return employeeList

    @api.one
    def getProfile(self):
        partner = self.user_id.partner_id
        return {'id': partner.id, 'name': partner.name, 'phone': partner.phone, 'mobile': partner.mobile,
                'email': partner.email, 'address': partner.street, 'countryId': partner.country_id.id,
                'provinceId': partner.state_id.id, 'birthdate': partner.birthdate or False,
                'image': partner.image or False,
                'gender': partner.gender or False}

    @api.one
    def updateProfile(self, vals):
        self.user_id.partner_id.write({'name': vals['name'], 'phone': vals['phone'], 'mobile': vals['mobile'],
                                       'email': vals['email'], 'street': vals['address'],
                                       'country_id': vals['countryId'],
                                       'state_id': vals['provinceId'],
                                       'birthdate': vals['birthdate'] if 'birthdate' in vals else None,
                                       'image': vals['image'] if 'image' in vals else None,
                                       'gender': vals['gender'] if 'gender' in vals else None
                                       })
        return True

    @api.one
    def getWorkExperience(self):
        expList = []
        for exp in self.experience_ids:
            expList.append({'id': exp.id, 'title': exp.title, 'employer': exp.employer, 'startDate': exp.start_date,
                            'endDate': exp.end_date,
                            'current': exp.current, 'categoryId': exp.cat_id.id if exp.cat_id else False,
                            'countryId': exp.country_id.id, 'provinceId': exp.province_id.id,
                            'description': exp.description})
        return expList

    @api.one
    def addWorkExperience(self, vals):
        exp = self.env['career.work_experience'].create({'title': vals['title'], 'employer': vals['employer'],
                                                         'start_date': 'startDate' in vals and vals['startDate'],
                                                         'description': vals['description'],
                                                         'end_date': 'endDate' in vals and vals['endDate'],
                                                         'current': vals['current'],
                                                         'cat_id': vals['categoryId'],
                                                         'country_id': 'countryId' in vals and int(vals['countryId']),
                                                         'province_id': 'provinceId' in vals and int(
                                                             vals['provinceId']),
                                                         'employee_id': self.id})
        return exp.id

    @api.one
    def getEducationHistory(self):
        eduList = []
        for edu in self.education_ids:
            eduList.append(
                {'id': edu.id, 'program': edu.program, 'institute': edu.institute, 'finishDate': edu.complete_date,
                 'status': edu.status, 'levelId': edu.level_id.id})
        return eduList

    @api.one
    def addEducationHistory(self, vals):
        edu = self.env['career.education_history'].create({'program': vals['program'], 'institute': vals['institute'],
                                                           'complete_date': vals['finishDate'],
                                                           'status': vals['status'],
                                                           'level_id': int(vals['levelId']), 'employee_id': self.id})
        return edu.id

    @api.one
    def applyJob(self, assignmentId):
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.isEnabled():
                for survey in assignment.survey_ids:
                    if survey.status == 'published':
                        user_input = self.env['survey.user_input'].search(
                            [('email', '=', self.user_id.login), ('survey_id', '=', survey.id)])
                        if not user_input:
                            user_input = self.env['survey.user_input'].create(
                                {'survey_id': survey.id, 'deadline': assignment.deadline,
                                 'type': 'link', 'state': 'new', 'email': self.user_id.login})
                        candidate = self.env['hr.applicant'].search(
                            [('email_from', '=', self.user_id.login), ('job_id', '=', assignment.id),
                             ('join_survey_id', '=', survey.id)])
                        if not candidate:
                            self.env['hr.applicant'].create(
                                {'name': self.name, 'email_from': self.user_id.login, 'job_id': assignment.id,
                                 'company_id': assignment.company_id.id, 'response_id': user_input.id,
                                 'join_survey_id': survey.id})
                        return True
        return False

    @api.one
    def getApplicantHistory(self):
        applicationList = []
        applicants = self.env['hr.applicant'].search([('email_from', '=', self.user_id.login)])
        for applicant in applicants:
            interview_link = False
            if applicant.response_id:
                interview_link = "https://vietinterview.com/interview?code=%s&" % applicant.response_id.token
            applicationList.append(
                {'id': applicant.id, 'title': applicant.job_id.name, 'company': applicant.company_id.name,
                 'interview': applicant.join_survey_id.title, 'round': applicant.join_survey_id.round,
                 'deadline': applicant.job_id.deadline, 'applyDate': applicant.create_date,
                 'interview_link': interview_link})
        return applicationList

    @api.one
    def getCertificate(self):
        certList = []
        for cert in self.certificate_ids:
            certList.append({'id': cert.id, 'title': cert.title, 'issuer': cert.issuer, 'issueDate': cert.issue_date})
        return certList

    @api.one
    def addCertificate(self, vals):
        cert = self.env['career.certificate'].create({'title': vals['title'], 'issuer': vals['issuer'],
                                                      'issue_date': vals['issueDate'], 'employee_id': self.id})
        return cert.id

    @api.one
    def getDocument(self):
        certList = []
        documents = self.env['ir.attachment'].search([('res_model', '=', 'career.employee'), ('res_id', '=', self.id)])
        for doc in documents:
            certList.append({'id': doc.id, 'title': doc.name, 'filename': doc.datas_fname, 'filedata': doc.store_fname})
        return certList

    @api.one
    def addDocument(self, title, filename, file_location):
        doc = self.env['ir.attachment'].create(
            {'name': title, 'description': title, 'res_model': 'career.employee', 'res_id': self.id,
             'type': 'binary', 'store_fname': file_location, 'datas_fname': filename})
        return doc.id
