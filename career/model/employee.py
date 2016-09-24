from openerp import models, fields, api, tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime


class UserProfile(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    gender = fields.Char(string="Gender")
    videoUrl = fields.Char(string="Video URL")
    description = fields.Char(string="Description")
    url = fields.Char(string="URL")

class WorkExperience(models.Model):
    _name = 'career.work_experience'

    title = fields.Text(string="Title")
    employer = fields.Text(string="Employer")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    cat_ids = fields.Many2many('career.job_category', string="Job category")
    position_id = fields.Many2one('career.job_position', string='Job position')
    description = fields.Text(string="Description")
    current = fields.Boolean(string='Is current')
    country_id = fields.Many2one('res.country', string="Country ")
    province_id = fields.Many2one('res.country.state', string="Province ")
    employee_id = fields.Many2one('career.employee', string="Employee")

    @api.multi
    def updateWorkExperience(self, vals):
        
        catIdList = vals['categoryIdList']
        self.write( {'title': vals['title'], 'employer': vals['employer'], 'start_date': vals['startDate'],
             'end_date': vals['endDate'], 'current': vals['current'], 'cat_ids': [(6, 0, catIdList)],
             'country_id': int(vals['countryId']), 'province_id': int(vals['provinceId']),
             'description': vals['description'], 'position_id': int(vals['positionId'])})
        return True

    @api.multi
    def removeWorkExperience(self):
        self.unlink()
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

    @api.multi
    def updateEducationHistory(self, vals):
        
        self.write(
            {'program': vals['program'], 'institute': vals['institute'],
             'complete_date': vals['finishDate'], 'status': vals['status'],
             'level_id': int(vals['levelId'])})
        return True

    @api.multi
    def removeEducationHistory(self):
        if self.unlink():
            return True
        return False


class Certificate(models.Model):
    _name = 'career.certificate'

    title = fields.Text(string="Title")
    issuer = fields.Text(string="Issuer")
    issue_date = fields.Date(string="Date of issuer")
    employee_id = fields.Many2one('career.employee', string="Employee")

    @api.multi
    def updateCertificate(self, vals):
        
        self.write({'title': vals['title'], 'issuer': vals['issuer'],
                                                                      'issue_date': vals['issueDate']})
        return True

    @api.multi
    def removeCertificate(self):
        if self.unlink():
            return True
        return False


class Document(models.Model):
    _name = 'ir.attachment'
    _inherit = 'ir.attachment'

    @api.multi
    def removeDocument(self):
        if self.unlink():
            return True
        return False


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

    @api.multi
    def getProfile(self):
        self.ensure_one()
        partner = self.user_id.partner_id
        return {'id': partner.id, 'name': partner.name, 'phone': partner.phone, 'mobile': partner.mobile,
                'email': partner.email, 'address': partner.street, 'countryId': partner.country_id.id,
                'provinceId': partner.state_id.id, 'birthdate': partner.birthdate or False,
                'image': partner.image or False,
                'gender': partner.gender or False,
                'videoUrl': partner.videoUrl or False}

    @api.multi
    def updateProfile(self, vals):
        self.ensure_one()
        self.user_id.partner_id.write({'name': vals['name'], 'phone': vals['phone'], 'mobile': vals['mobile'],
                                       'email': vals['email'], 'street': vals['address'],
                                       'country_id': vals['countryId'],
                                       'state_id': vals['provinceId'],
                                       'birthdate': vals['birthdate'] if 'birthdate' in vals else None,
                                       'image': vals['image'] if 'image' in vals else None,
                                       'gender': vals['gender'] if 'gender' in vals else None,
                                       'videoUrl': vals['videoUrl'] if 'videoUrl' in vals else None
                                       })
        return True

    @api.multi
    def getWorkExperience(self):
        self.ensure_one()
        expList = []
        for exp in self.experience_ids:
            expList.append({'id': exp.id, 'title': exp.title, 'employer': exp.employer, 'startDate': exp.start_date,
                            'endDate': exp.end_date,
                            'current': exp.current, 'categoryIdList': list(exp.cat_ids.ids),
                            'countryId': exp.country_id.id, 'provinceId': exp.province_id.id,
                            'description': exp.description, 'positionId': exp.position_id.id})
        return expList

    @api.multi
    def addWorkExperience(self, vals):
        self.ensure_one()
        catIdList = vals['categoryIdList']
        exp = self.env['career.work_experience'].create({'title': vals['title'], 'employer': vals['employer'],
                                                         'start_date': 'startDate' in vals and vals['startDate'],
                                                         'description': vals['description'],
                                                         'end_date': 'endDate' in vals and vals['endDate'],
                                                         'current': vals['current'],
                                                         'cat_ids': [(6, 0, catIdList)],
                                                         'country_id': 'countryId' in vals and int(vals['countryId']),
                                                         'province_id': 'provinceId' in vals and int(vals['provinceId']),
                                                         'position_id': 'positionId' in vals and int(vals['positionId']),
                                                         'employee_id': self.id})
        return exp.id

    @api.multi
    def updateWorkExperience(self, vals):
        self.ensure_one()
        for exp in self.env['career.work_experience'].browse(int(vals['id'])):
            if exp.employee_id.id == self.id:
                return exp.updateWorkExperience(vals)
        return False

    @api.multi
    def removeWorkExperience(self, id):
        self.ensure_one()
        for exp in self.env['career.work_experience'].browse(id):
            if exp.employee_id.id == self.id:
                return exp.removeWorkExperience()
        return False


    @api.multi
    def getEducationHistory(self):
        self.ensure_one()
        eduList = []
        for edu in self.education_ids:
            eduList.append(
                {'id': edu.id, 'program': edu.program, 'institute': edu.institute, 'finishDate': edu.complete_date,
                 'status': edu.status, 'levelId': edu.level_id.id})
        return eduList

    @api.multi
    def addEducationHistory(self, vals):
        self.ensure_one()
        edu = self.env['career.education_history'].create({'program': vals['program'], 'institute': vals['institute'],
                                                           'complete_date': vals['finishDate'],
                                                           'status': vals['status'],
                                                           'level_id': int(vals['levelId']), 'employee_id': self.id})
        return edu.id

    @api.multi
    def updateEducationHistory(self, vals):
        self.ensure_one()
        for edu in self.env['career.education_history'].browse(int(vals['id'])):
            if edu.employee_id.id == self.id:
                return edu.updateEducationHistory(vals)
        return False

    @api.multi
    def removeEducationHistory(self, id):
        self.ensure_one()
        for edu in self.env['career.education_history'].browse(id):
            if edu.employee_id.id == self.id:
                return edu.removeEducationHistory()
        return False

    @api.multi
    def applyJob(self, assignmentId, letter):
        self.ensure_one()
        for assignment in self.env['hr.job'].browse(assignmentId):
            if assignment.isEnabled():
                if not assignment.survey_ids:
                    candidate = self.env['hr.applicant'].search(
                        [('email_from', '=', self.user_id.login), ('job_id', '=', assignment.id)])
                    if not candidate:
                        applicant_id = self.env['hr.applicant'].create(
                            {'name': self.name, 'email_from': self.user_id.login, 'job_id': assignment.id,
                             'company_id': assignment.company_id.id, 'letter': letter})
                        self.env['career.mail_service'].sendCoverLetter(applicant_id)
                    return True
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
                             ('interview_id', '=', survey.id)])
                        if not candidate:
                            applicant_id = self.env['hr.applicant'].create(
                                {'name': self.name, 'email_from': self.user_id.login, 'job_id': assignment.id,
                                 'company_id': assignment.company_id.id, 'response_id': user_input.id,
                                 'interview_id': survey.id, 'letter': letter})
                            self.env['career.mail_service'].sendCoverLetter(applicant_id)
                        return True
        return False

    @api.multi
    def getApplicantHistory(self):
        self.ensure_one()
        applicationList = []
        applicants = self.env['hr.applicant'].search([('email_from', '=', self.user_id.login)])
        for applicant in applicants:
            interview_link = False
            if applicant.response_id:
                interview_link = "https://vietinterview.com/interview?code=%s&" % applicant.response_id.token
            applicationList.append(
                {'id': applicant.id, 'title': applicant.job_id.name, 'company': applicant.company_id.name,
                 'interview': applicant.interview_id.title, 'round': applicant.interview_id.round,
                 'deadline': applicant.job_id.deadline, 'applyDate': applicant.create_date,
                 'interview_link': interview_link})
        return applicationList

    @api.multi
    def getCertificate(self):
        self.ensure_one()
        certList = []
        for cert in self.certificate_ids:
            certList.append({'id': cert.id, 'title': cert.title, 'issuer': cert.issuer, 'issueDate': cert.issue_date})
        return certList

    @api.multi
    def addCertificate(self, vals):
        self.ensure_one()
        cert = self.env['career.certificate'].create({'title': vals['title'], 'issuer': vals['issuer'],
                                                      'issue_date': vals['issueDate'], 'employee_id': self.id})
        return cert.id

    @api.multi
    def updateCertificate(self, vals):
        self.ensure_one()
        for cert in self.env['career.certificate'].browse(int(vals['id'])):
            if cert.employee_id.id == self.id:
                return cert.updateCertificate(vals)
        return False

    @api.multi
    def removeCertificate(self, id):
        self.ensure_one()
        for cert in self.env['career.certificate'].browse(id):
            if cert.employee_id.id == self.id:
                return cert.removeCertificate()
        return False

    @api.multi
    def getDocument(self):
        self.ensure_one()
        docList = []
        documents = self.env['ir.attachment'].search([('res_model', '=', 'career.employee'), ('res_id', '=', self.id)])
        for doc in documents:
            docList.append({'id': doc.id, 'title': doc.name, 'filename': doc.datas_fname, 'filedata': doc.store_fname})
        return docList

    @api.multi
    def addDocument(self, title, filename, file_location):
        self.ensure_one()
        doc = self.env['ir.attachment'].create(
            {'name': title, 'description': title, 'res_model': 'career.employee', 'res_id': self.id,
             'type': 'binary', 'store_fname': file_location, 'datas_fname': filename})
        return doc.id


    @api.multi
    def removeDocument(self, id):
        self.ensure_one()
        for doc in self.env['ir.attachment'].browse(id):
            if doc.res_model == self._name and doc.res_id == self.id:
                return doc.unlink()
        return False