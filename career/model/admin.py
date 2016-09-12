from openerp import models, fields, api, tools

class Admin(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    @api.model
    def createAdmin(self, login, password, role):
        user = self.env['res.users'].search([('login', '=', login)])
        if user:
            print ("Admin %s already exist" % login)
            return False
        admin_group = False
        if role == 'admin':
            admin_group = self.env.ref('career.admin_group')
        if role == 'cc':
            admin_group = self.env.ref('career.cc_group')
        if admin_group:
            hr_group = self.env.ref('base.group_hr_manager')
            survey_group = self.env.ref('base.group_survey_manager')
            man_group = self.env.ref('base.group_erp_manager')
            user = self.env['res.users'].create(
                {'login': login, 'password': password, 'name': login, 'notify_email': 'none',
                 'email': login, 'groups_id': [(6, 0, [admin_group.id, hr_group.id, survey_group.id, man_group.id])]})
            return user.id
        return False

    @api.model
    def updateAdmin(self, login, password, role):
        users = self.env['res.users'].search([('login', '=', login)])
        for user in users:
            if user.write({'password': password}):
                return True
        return False

    @api.model
    def getAdmins(self):
        adminList = []
        users = self.env['res.users'].search()
        admin_group = self.env.ref('career.admin_group')
        cc_group = self.env.ref('career.cc_group')
        for user in users:
            if admin_group.id in user.groups_id.ids or cc_group.id in user.groups_id.ids:
                admin['login'] = user.login
                admin['role'] = user.groups_id.name
                return True
        return False