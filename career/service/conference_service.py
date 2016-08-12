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
				for member in self.env['career.conference_member'].search([('member_id', '=', memberId)]):
					info['profile'] = {'name':member.name,'role':member.role,'memberId':member.member_id,'meetingId':member.conference_id.meeting_id}
		return info


