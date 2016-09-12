# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime
import time
import string
from datetime import date, datetime, timedelta
from .. import util


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

    @api.model
    def login(self, db, account, password, role):
        uid = common.exp_authenticate(db, account, password, {})
        if not uid:
            print ("Invalid username %s or password %s" % (account, password))
            return False
        user = self.env['res.users'].browse(uid)
        if not self.validateUser(user, role):
            return False
        session = self.env['career.session'].create({'uid': user.id, 'db': db, 'user': account, 'password': password})
        return session.token

    @api.model
    def logout(self, token):
        sessions = self.env['career.session'].search([('token', '=', token)])
        sessions.unlink()
        return True

    @api.model
    def validateUser(self, user, role):
        if role == 'admin':
            admin_group = self.env.ref('career.admin_group')
            if admin_group.id in user.groups_id.ids:
                return True
        if role == 'cc':
            cc_group = self.env.ref('career.cc_group')
            if cc_group.id in user.groups_id.ids:
                return True
        if role == 'employer':
            employer_group = self.env.ref('career.employer_group')
            if employer_group.id in user.groups_id.ids:
                return True
        if role == 'employee':
            employee_group = self.env.ref('career.employee_group')
            if employee_group.id in user.groups_id.ids:
                return True
        return False

    @api.model
    def validateToken(self, token, roles):
        for session in self.env['career.session'].search([('token', '=', token)]):
            user = self.env['res.users'].browse(session.uid)
            for role in roles:
                if self.validateUser(user, role):
                    return {'uid': session.uid, 'user': session.user, 'password': session.password, 'db': session.db}
        return False


class OTK(models.Model):
    _name = 'career.otk'
    token = fields.Char(string='One Time Token')
    email = fields.Char(string='Login')
    date_expired = fields.Date(string='Expired Date', default=(date.today() + timedelta(days=1)).strftime('%Y-%m-%d'))
    url = fields.Char(string='URL to reset password')

    @api.model
    def create(self, vals):
        vals['token'] = util.id_generator(24)
        otk = super(OTK, self).create(vals)
        return otk

    _sql_constraints = [
        ('token_unique', 'unique (token)', 'The token must be unique within an application!')
    ]


