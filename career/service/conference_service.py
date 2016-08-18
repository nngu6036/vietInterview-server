# -*- coding: utf-8 -*-

from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime
import hashlib
from xml.dom import minidom
import lxml.html.clean as clean
from datetime import date, timedelta
import urllib, urllib2


class ConferenceService(osv.AbstractModel):
	_name = 'career.conference_service'

	@api.model
	def openMeeting(self, conferenceId):
		for conference in self.env['career.conference'].browse(conferenceId):
			conference.write({'status': 'started'})
			return True
		return False

	@api.model
	def endMeeting(self,meetingId,memberId):
		for conference in self.env['career.conference'].search([('meeting_id','=',meetingId)]):
			conference.write({'status': 'ended'})
			return True
		return False


	@api.model
	def getMeetingInfo(self,meetingId,memberId):
		info = {}
		for conference in self.env['career.conference'].search([('meeting_id','=',meetingId)]):
			info['status']  = conference.status
			if conference.status !='ended':
				for member in self.env['career.conference_member'].search([('member_id', '=', memberId),('role','=','moderator')]):
					info['moderator'] = {'name':member.name,'role':member.role,'memberId':member.member_id,'meetingId':member.conference_id.meeting_id}
					questions = self.env['survey.question'].search([('survey_id', '=', conference.interview_id.id)])
					info['questionList'] = [{'id': q.id, 'title': q.question, 'response': q.response, 'retry': q.retry,
											 'prepare': q.prepare, 'videoUrl': q.videoUrl,	 'source': q.source,
											 'type': q.mode, 'order': q.sequence} for q in questions]
				for member in self.env['career.conference_member'].search([('role', '=', 'candidate')]):
					info['candidate'] = {'name': member.name, 'role': member.role, 'memberId': member.member_id,  'meetingId': member.conference_id.meeting_id}
				job =  conference.interview_id.job_id
				info['job']= {'name': job.name, 'description': job.description, 'deadline': job.deadline, 'status': job.status,
							  'requirements': job.requirements,  'company': job.company_id.name, 'country': job.country_id.name,
							  'province': job.province_id.name, 'createDate': job.create_date}
		return info


