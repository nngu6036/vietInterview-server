# -*- coding: utf-8 -*-

from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime
import util

# monkey patching to allow scr not to be remove in html clean
# see openerp.tools.mail.py
import lxml.html.clean as clean
import re
clean._is_javascript_scheme = re.compile(
         r'(?:javascript|jscript|livescript|vbscript|about|mocha):',
         re.I).search
from jinja2.sandbox import SandboxedEnvironment
mako_template_env = SandboxedEnvironment(
    block_start_string="<%",
    block_end_string="%>",
    variable_start_string="${",
    variable_end_string="}",
    comment_start_string="<%doc>",
    comment_end_string="</%doc>",
    line_statement_prefix="%",
    line_comment_prefix="##",
    trim_blocks=True,               # do not output newline after blocks
    lstrip_blocks =True,
    autoescape=True,                # XML/HTML automatic escaping
)
from datetime import date, timedelta


class SessionService(osv.AbstractModel):
    _name = 'career.session_service'

    @api.model
    def login(self,db, account,password,role):
        uid = common.exp_authenticate(db,account,password,{})
        if not uid:
            print ("Invalid username %s or password %s" % (account, password))
            return False
        user = self.env['res.users'].browse(uid)
        if not self.validateUser(user,role):
            return False
        session = self.env['career.session'].create({'uid':user.id,'db':db,'user':account,'password':password})
        return session.token


    @api.model
    def logout(self, token):
        sessions = self.env['career.session'].search([('token', '=', token)])
        sessions.unlink()
        return True


    @api.model
    def validateUser(self,user,role):
          if role == 'admin':
              admin_group = self.env.ref('career.admin_group')
              if admin_group.id in user.groups_id.ids:
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
    def validateToken(self,token,roles):
        for session in self.env['career.session'].search([('token','=',token)]):
            user = self.env['res.users'].browse(session.uid)
            for role in roles:
                if self.validateUser(user,role):
                  return {'uid':session.uid,'user':session.user,'password':session.password,'db':session.db}
        return False

    @api.model
    def changePass(self,login,oldpass,newpass):
        user = self.env['res.users'].search([('login','=',login)])
        if user.write({'password':newpass}):
            return True
        return False