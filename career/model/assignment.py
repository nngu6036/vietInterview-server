from openerp import models, fields, api, tools
from openerp.osv import osv
from openerp.service import common
from .. import util
import datetime
from datetime import date, timedelta


class JobCategory(models.Model):
    _name = 'career.job_category'
    title = fields.Text(string="Title", translate=True)

    @api.model
    def getJobCategory(self, lang):
        lang = util.lang_resolver(lang)
        context = {'lang': lang}
        categories = self.env['career.job_category'].with_context(context).search([])
        categoryList = [{'id': c.id, 'title': c.title} for c in categories]
        return categoryList


class JobPosition(models.Model):
    _name = 'career.job_position'
    title = fields.Text(string="Title", translate=True)

    @api.model
    def getJobPosition(self, lang):
        lang = util.lang_resolver(lang)
        context = {'lang': lang}
        positions = self.env['career.job_position'].with_context(context).search([])
        positionList = [{'id': p.id, 'title': p.title} for p in positions]
        return positionList


class Assignment(models.Model):
    _name = 'hr.job'
    _inherit = 'hr.job'

    status = fields.Selection(
        [('initial', 'Initial status'), ('published', 'Published status'), ('closed', 'Closed status')],
        default='initial')
    deadline = fields.Date(string="Application deadline")
    category_ids = fields.Many2many('career.job_category', string="Category List")
    position_id = fields.Many2one('career.job_position', string="Position")
    country_id = fields.Many2one(string='Country', related='address_id.country_id')
    province_id = fields.Many2one(string='Province ', related='address_id.state_id')
    survey_ids = fields.One2many('survey.survey', 'job_id', string="Interview rounds")

    @api.one
    def isEnabled(self):
        if self.state != 'recruit':
            return False
        if not self.deadline:
            return True
        deadline = datetime.datetime.strptime(self.deadline, "%Y-%m-%d")
        if deadline < datetime.datetime.now():
            return False
        return True



    @api.model
    def getAssignment(self):
        assignments = self.env['hr.job'].search([])
        assignmentList = [
            {'id': a.id, 'name': a.name, 'description': a.description, 'deadline': a.deadline, 'status': a.status,
             'requirements': a.requirements, 'approved': a.state == 'recruit',
             'company': a.company_id.name, 'companyId': a.company_id.id,
             'countryId': a.country_id.id, 'provinceId': a.province_id.id,
             'createDate': a.create_date,
             'categoryIdList': list(a.category_ids.ids), 'positionId': a.position_id.id} for a in assignments]
        return assignmentList

    @api.one
    def updateAssignment(self, vals):
        catIdList = vals['categoryIdList']
        self.write({'deadline': vals['deadline'], 'description': vals['description'], 'name': vals['name'],
                          'requirements': vals['requirements'],
                          'category_ids': [(6, 0, catIdList)] or False,
                          'position_id': int(vals['positionId']) or False})
        self.address_id.write({'country_id': int(vals['countryId']) or False, 'state_id': int(vals['provinceId']) or False})
        return True

    @api.one
    def deleteAssignment(self):
        if self.status == 'initial':
            self.unlink()
            return True
        return False

    @api.one
    def getCompanyInfo(self):
        return {'id': self.company_id.id, 'name': self.company_id.name, 'image': self.company_id.logo or False}

    @api.one
    def getInterview(self):
        interviewList = []
        for interview in self.survey_ids:
            interviewList.append({'id': interview.id, 'name': interview.title,
                                  'response': interview.response,
                                  'retry': interview.retry, 'introUrl': interview.introUrl,
                                  'exitUrl': interview.exitUrl,
                                  'conferenceId': interview.conference_id.id,
                                  'aboutUsUrl': interview.aboutUsUrl, 'language': interview.language,
                                  'prepare': interview.prepare, 'job_id': self.id, 'round': interview.round,
                                  'mode': interview.mode, 'status': interview.status})
        return interviewList
