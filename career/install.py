# -*- coding: utf-8 -*-

from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
from datetime import date, datetime, timedelta
class Career(osv.AbstractModel):
    _name = 'career.career'

    @api.model
    def install(self):
        root_user = self.env.ref("base.user_root")
        admin_group = self.env.ref('career.admin_group')
        root_user.write({'groups_id':[(4,admin_group.id)]})
        company = self.env.ref('base.main_company')
        company.write({'name':'Administrator'})

        # Set up cron task
        now = datetime.now()
        tomorrow = now.replace(hour=0, minute=0, second=1, microsecond=0)
        next_call = '%d-%d-%d %d:%d:%d' % (
        tomorrow.year, tomorrow.month, tomorrow.day, tomorrow.hour, tomorrow.minute, tomorrow.second)
        self.env['ir.cron'].create(
            {'name': 'DAILY_TASK', 'interval_number': 1, 'interval_type': 'days', 'numbercall': -1,
             'model': 'career.career_task', 'function': 'runDaily', 'nextcall': next_call})



class CronTask(osv.AbstractModel):
    _name = 'career.career_task'

    @api.model
    def runDaily(self):
        for job in self.env['hr.job'].search([('status','=','published')]):
            if not job.isEnabled():
                job.write({'status':'closed'})
        license_service = self.env['career.license_service']
        for company in self.env['res.company']:
            if company.license_instance_id :
                if not license_service.validateLicense(company.id):
                    license_service.deactivateLicense(company.id)
        return True

    @api.model
    def runHourly(self):
        return True

    @api.model
    def runWeekly(self):
        return True

    @api.model
    def runMonthly(self):
        # Check to create fiscal year

        return True