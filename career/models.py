# -*- coding: utf-8 -*-

import util
import time
from openerp import models, fields, api
import datetime
import sys
import re



class Session(models.Model):
    _name = 'career.session'

    token = fields.Char(string='Token')
    user = fields.Char(string='Login')
    password = fields.Char(string='Password')
    db = fields.Char(string='Database')
    uid = fields.Integer(string='User ID')

    @api.model
    def create(self, vals):
        vals['token'] = util.id_generator(24)
        session = super(Session, self).create(vals)
        return session

    _sql_constraints = [
        ('token_unique', 'unique (token)', 'The token must be unique within an application!')
    ]

class Conpany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    license_instance_id = fields.Many2one('career.license_instance',string='License')
    expire_date = fields.Date(string='License expire date',related='license_instance_id.expire_date')

class EmployerUser(models.Model):
    _name = 'career.employer'
    _inherits = {'res.users':'user_id'}

    user_id = fields.Many2one('res.users',string='User',required=True)
    login = fields.Char(string='Login name',related='user_id.login')
    password = fields.Char(string='Password',related='user_id.password')
    name = fields.Char(string='Name',related='user_id.name')

class License(models.Model):
    _name = 'career.license'

    name = fields.Char(string='Name', required=True)
    assignment = fields.Integer(string='Assignment limit')
    email = fields.Integer(string='Email limit')


class LicenseInstance(models.Model):
    _name = 'career.license_instance'

    license_id = fields.Many2one('career.license', string="License")
    expire_date = fields.Date(string="Expired date")
    effect_date = fields.Date(string="Effective date ")
    state = fields.Selection([('initial', 'Initial state'), ('suspend', 'Suspended state'), ('active', 'Active state'),
                              ('closed', 'Closed state')], default='initial')

    @api.one
    def isEnabled(self):
        if not self.expire_date:
            return True
        expire_date = datetime.datetime.strptime(self.expire_date, "%Y-%m-%d")
        if self.state != 'active' and expire_date < datetime.datetime.now():
            return False
        return True


class QuestionCategory(models.Model):
    _name = 'career.question_category'
    title = fields.Text(string="Title",translate=True)

class Question(models.Model):
    _name = 'career.question'
    title = fields.Text(string="Title",translate=True)
    content = fields.Text(string="Content",translate=True)
    videoUrl = fields.Text(string="VIdeo")
    category_id = fields.Many2one('career.question_category', string="Category")


class JobCategory(models.Model):
    _name = 'career.job_category'
    title = fields.Text(string="Title",translate=True)

class JobPosition(models.Model):
    _name = 'career.job_position'
    title = fields.Text(string="Title",translate=True)


class Assignment(models.Model):
    _name = 'hr.job'
    _inherit = 'hr.job'

    status = fields.Selection([('initial', 'Initial status'), ('published', 'Published status'),  ('closed', 'Closed status')], default='initial')
    deadline = fields.Date(string="Application deadline")
    category_id = fields.Many2one('career.job_category', string="Category")
    position_id = fields.Many2one('career.job_position', string="Position")
    country_id = fields.Many2one(string='Country',related='address_id.country_id')
    province_id = fields.Many2one(string='Province ',related='address_id.state_id')

    @api.one
    def isEnabled(self):
        if self.status =='closed':
            return False
        if not self.deadline:
            return True
        deadline = datetime.datetime.strptime(self.deadline, "%Y-%m-%d")
        if deadline < datetime.datetime.now():
            return False
        return True


class Interview(models.Model):
    _name = 'survey.survey'
    _inherit = 'survey.survey'

    response = fields.Integer(string="Response time limit for one question")
    retry = fields.Integer(string="Number of attempts for one question, -1 means unlimited")
    introUrl = fields.Text(string="Introduction Video URL")
    exitUrl = fields.Text(string="Thank you Video URL")
    aboutUsUrl = fields.Text(string="About Us Video URL")
    language = fields.Char(string="Language",default="en")

class InterviewQuestion(models.Model):
    _name = 'survey.question'
    _inherit = 'survey.question'

    response = fields.Integer(string="Response time limit for one question")
    retry = fields.Integer(string="Number of attempts for one question, -1 means unlimited")
    prepare = fields.Integer(string="Prepare time for one question, -1 means unlimited",default=1)
    source = fields.Selection([('manual', 'User-defined'), ('system', 'System question')], default='system')
    mode = fields.Selection([('text', 'Reading'), ('video', 'Watching')], default='video')
    videoUrl = fields.Text(string="Question Video URL")


class InterviewAnswer(models.Model):
    _name = 'survey.user_input_line'
    _inherit = 'survey.user_input_line'
    answer_type = fields.Selection([('text', 'Text'), ('number', 'Number'),('date', 'Date'),('free_text', 'Free Text'),
                                    ('suggestion', 'Suggestion'),('url', 'URL')])
    value_video_url= fields.Text(string="URL Video reponse")



class InterviewAssessment(models.Model):
    _name = 'hr.evaluation.interview'
    _inherit = 'hr.evaluation.interview'

    applicant_id = fields.Many2one('hr.applicant',tring='Applicant ')
    rating =  fields.Integer(string="Rating")
    note_summary =  fields.Text(string="Comment")

class InterviewHistory(models.Model):
    _name = 'survey.user_input'
    _inherit = 'survey.user_input'

    wrap_up = fields.Boolean(string="Wrap-up completed")


class EmployeeUser(models.Model):
    _name = 'career.employee'
    _inherits = {'res.users':'user_id'}

    user_id = fields.Many2one('res.users',string='User',required=True)
    login = fields.Char(string='Login name',related='user_id.login')
    password = fields.Char(string='Password',related='user_id.password')
    name = fields.Char(string='Name',related='user_id.name')
    experience_ids = fields.One2many('career.work_experience', 'employee_id',string="Working experience")
    education_ids = fields.One2many('career.education_history', 'employee_id',string="Education history")
    certificate_ids = fields.One2many('career.certificate', 'employee_id',string="Certificate")

class WorkExperience(models.Model):
    _name = 'career.work_experience'

    title = fields.Text(string="Title")
    employer = fields.Text(string="Employer")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    leave_reason = fields.Text(string="Reason to leave")
    description = fields.Text(string="Description")
    current = fields.Boolean(string='Is current')
    country_id = fields.Many2one('res.country', string="Country ")
    province_id = fields.Many2one('res.country.state', string="Province ")
    employee_id = fields.Many2one('career.employee', string="Employee")


class EducationHistory(models.Model):
    _name = 'career.education_history'

    institute = fields.Text(string="Institute")
    start_date = fields.Date(string="Start date")
    complete_date = fields.Date(string="Complete date")
    program = fields.Text(string="Program")
    status = fields.Selection([('graduated', 'Graduated'), ('enrolled', 'Current enrolled')])
    level_id = fields.Many2one('hr.recruitment.degree', string="Degree ")
    employee_id = fields.Many2one('career.employee', string="Employee")


class Certificate(models.Model):
    _name = 'career.certificate'

    title = fields.Text(string="Title")
    issuer = fields.Text(string="Issuer")
    issue_date = fields.Date(string="Date of issuer")
    employee_id = fields.Many2one('career.employee', string="Employee")
