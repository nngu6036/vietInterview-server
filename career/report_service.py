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
from datetime import date, timedelta



class ReportService(osv.AbstractModel):
    _name = 'career.report_service'

    @api.model
    def getAssessmentSummaryReport(self,candidateId):
      applicant = self.env['hr.applicant'].browse(candidateId)
      content_pdf = self.env['report'].get_pdf(applicant, 'career.report_assessment_summary')
      encoded_content = base64.b64encode(content_pdf)
      return encoded_content
