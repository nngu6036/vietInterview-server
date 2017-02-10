import datetime
from datetime import date, timedelta

from openerp import models, fields, api

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
    position_id = fields.Many2one('career.job_position', string='Job position')
    license_id = fields.Many2one('career.license', string='License')
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
            {'name': vals['name'], 'email': int(vals['email']), 'point': int(vals['point']),
             'assignment': int(vals['assignment']),
             'validity': int(vals['validity']), 'cat_id': int(vals['categoryId'])})
        return license.id

    @api.model
    def getLicense(self):
        licenses = self.env['career.license'].search([])
        licenseList = [
            {'id': l.id, 'name': l.name, 'point': l.point, 'email': l.email, 'assignment': l.assignment,
             'validity': l.validity,
             'createDate': l.create_date, 'categoryId': l.cat_id.id} for l in licenses]
        return licenseList


class LicenseInstance(models.Model):
    _name = 'career.license_instance'

    assignment = fields.Integer(string='Assignment limit')
    email = fields.Integer(string='Email limit')
    point = fields.Integer(string='Point limit')
    cat_id = fields.Many2one('career.license_category', string='License category')
    rule_ids = fields.One2many('career.license_rule', 'license_id', 'License rule')
    license_id = fields.Many2one('career.license', string="License")
    expire_date = fields.Date(string="Expired date")
    effect_date = fields.Date(string="Effective date ")
    state = fields.Selection([('initial', 'Initial state'), ('suspend', 'Suspended state'), ('active', 'Active state'),
                              ('closed', 'Closed state')])
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
    cost = fields.Integer(string='View cost ')
    company_id = fields.Many2one('res.company', related='employer_id.company_id')
    employer_id = fields.Many2one('career.employer', string='Employer user')
    license_instance_id = fields.Many2one('career.license_instance', string='Applied license')


class Conpany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    license_instance_id = fields.Many2one('career.license_instance', string='License')
    expire_date = fields.Date(string='License expire date', related='license_instance_id.expire_date')
    url = fields.Char(string='Company URL', related='partner_id.url')

    @api.model
    def createCompany(self, vals):
        default_url = self.env['ir.config_parameter'].get_param('company.url')
        license = self.env['career.license'].browse(int(vals['licenseId']))
        expiryDdate = date.today() + timedelta(days=license.validity)
        license_instance = self.env['career.license_instance'].create({'license_id': license.id,
                                                                       'expire_date': '%d-%d-%d ' % (
                                                                           expiryDdate.year, expiryDdate.month,
                                                                           expiryDdate.day), 'email': license.email,
                                                                       'point': license.point,
                                                                       'assignment': license.assignment,
                                                                       'cat_id': license.cat_id.id,
                                                                       'rule_ids': license.rule_ids})
        company = self.env['res.company'].create(
            {'name': vals['name'], 'logo': vals['image'] if 'image' in vals else False,
             'url': vals['url'] if 'url' in vals else default_url,
             'license_instance_id': license_instance.id})
        company.partner_id.write({'email': vals['email']})
        hr_eval_plan = self.env['hr_evaluation.plan'].create({'name': 'Assessment', 'company_id': company.id})
        assessment_form = self.env.ref('career.assessment_form')
        self.env['hr_evaluation.plan.phase'].create(
            {'name': 'Assessment', 'company_id': company.id, 'plan_id': hr_eval_plan.id,
             'action': 'final', 'survey_id': assessment_form.id})
        return company.id

    @api.one
    def updateCompany(self, vals):
        self.write({'name': vals['name'], 'logo': vals['image'] if 'image' in vals else False})
        self.partner_id.write({'email': vals['email'], 'videoUrl': vals['videoUrl'] if 'videoUrl' in vals else False,
                               'description': vals['description'] if 'description' in vals else False,
                               'street': vals['street'] if 'street' in vals else None,
                               'street2': vals['street2'] if 'street2' in vals else None,
                               'city': vals['city'] if 'city' in vals else None,
                               'zip': vals['zip'] if 'zip' in vals else None,
                               'country_id': int(vals['countryId']) if 'countryId' in vals else None,
                               'state_id': int(vals['stateId']) if 'stateId' in vals else None,
                               'vat': vals['vat'] if 'vat' in vals else None,
                               'phone': vals['phone'] if 'phone' in vals else None})
        return True

    @api.model
    def getCompany(self):
        main_compnay = self.env.ref('base.main_company')
        companys = self.env['res.company'].search([('id', '!=', main_compnay.id)])
        companyList = [{'id': c.id, 'name': c.name, 'image': c.logo or False,'url':c.website, 'videoUrl': c.partner_id.videoUrl,
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
        new_employer = self.env['career.employer'].create({'user_id': user.id, 'is_admin': False,'auto_approve':vals['autoApproved'] if 'autoApproved' in vals else False})
        return new_employer.id

    @api.one
    def getCompanyUser(self):
        userList = []
        for employer in self.env['career.employer'].search([('company_id', '=', self.id)]):
            userList.append({'id': employer.id, 'name': employer.name, 'email': employer.login,'autoApproved':employer.auto_approve})
        return userList

    @api.one
    def getAssignment(self,start=None,length=None,count=False):
        if count:
            assignmentList = self.env['hr.job'].search_count([('company_id', '=', self.id)])
        else:
            assignments = self.env['hr.job'].search([('company_id', '=', self.id)],limit=length, offset=start)
            assignmentList = [
                {'id': a.id, 'name': a.name, 'description': a.description, 'deadline': a.deadline, 'status': a.status,
                 'requirements': a.requirements, 'approved': a.state == 'recruit',
                 'countryId': a.country_id.id, 'provinceId': a.province_id.id,
                 'createDate': a.create_date,
                 'categoryIdList': list(a.category_ids.ids), 'positionId': a.position_id.id} for a in assignments]
        return assignmentList

    @api.one
    def getLicenseStatistic(self):
        stats = {'email': 0, 'point': 0, 'license': False}
        remain_point = 0
        if self.license_instance_id:
            stats['email'] = self.env['career.email.history'].search_count(
                [('license_instance_id', '=', self.license_instance_id.id)])
            for employeeHistory in self.env['career.employee.history'].search(
                    [('license_instance_id', '=', self.license_instance_id.id)]):
                remain_point += employeeHistory.cost
            stats['point'] = remain_point
            stats['license'] = {'name': self.license_instance_id.license_id.name,
                                'email': self.license_instance_id.email,
                                'assignment': self.license_instance_id.assignment,
                                'point': self.license_instance_id.point,
                                'expireDate': self.license_instance_id.expire_date,
                                'state': self.license_instance_id.state,
                                'code': self.license_instance_id.license_id.cat_id.code}
        return stats