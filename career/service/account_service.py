# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime
import time
import string
from datetime import date, datetime, timedelta
import string
from .. import util


class AccountService(osv.AbstractModel):
    _name = 'career.account_service'

    @api.model
    def changePass(self, db, login, oldpass, newpass):
        uid = common.exp_authenticate(db, login, oldpass, {})
        if not uid:
            print ("Invalid username %s or password %s" % (login, oldpass))
            return False
        users = self.env['res.users'].browse(uid)
        for user in users:
            user.write({'password': newpass})
        return True

    @api.model
    def generateNewPass(self, token):
        otks = self.env['career.otk'].search(
            [('token', '=', token), ('date_expired', '<=', datetime.now().strftime("%Y-%m-%d"))])
        for otk in otks:
            users = self.env['res.users'].search([('login', '=', otk.email)])
            for user in users:
                new_pass = util.id_generator(6, chars=string.digits)
                user.write({'password': new_pass})
                return new_pass
        return False

    @api.model
    def setNewPass(self, token, newpass):
        otks = self.env['career.otk'].search(
            [('token', '=', token), ('date_expired', '>=', datetime.now().strftime("%Y-%m-%d"))])
        for otk in otks:
            users = self.env['res.users'].search([('login', '=', otk.email)])
            for user in users:
                if user.write({'password': newpass}):
                    return True
        return False

    @api.model
    def requestResetPass(self,email):
        return self.env['career.mail_service'].sendResetPasswordInstructionMail(email)