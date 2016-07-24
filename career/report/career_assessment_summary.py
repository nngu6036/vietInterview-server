# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import  datetime

class career_assessment_summary(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(career_assessment_summary, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'assessmentResult': self._assessmentResult
        })

    def _assessmentResult(self,candidateId,lang='vi_VN'):
        assessmentResultList = []
        assessment_obj = self.pool.get('hr.evaluation.interview')
        for assessmentId in assessment_obj.search(self.cr,  self.uid,[('applicant_id','=',candidateId)]):
            hr_interview_assessment =  assessment_obj.browse(self.cr,  self.uid,assessmentId,{'lang':lang})
            pages = {}
            for answer in hr_interview_assessment.request_id.user_input_line_ids:
                if not answer.question_id.page_id.title in pages:
                    pages[answer.question_id.page_id.title] = []
                pages[answer.question_id.page_id.title].append(answer)
            assessmentResultList.append({'details':pages,'general':hr_interview_assessment})
        return assessmentResultList


class report_assessment_summary(osv.AbstractModel):
    _name = 'report.career.report_assessment_summary'
    _inherit = 'report.abstract_report'
    _template = 'career.report_assessment_summary'
    _wrapped_report_class = career_assessment_summary

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
