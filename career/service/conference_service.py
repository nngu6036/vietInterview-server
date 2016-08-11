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
		api_url = self.env['ir.config_parameter'].get_param('conference.server.api')
		secret = self.env['ir.config_parameter'].get_param('conference.server.api.secret')
		bbb_service = BBB_API(api_url, secret)
		for conference in self.env['career.conference'].browse(conferenceId):
			result = bbb_service.createMeeting(conference.name, conference.meeting_id, conference.access_code,
											   conference.mod_access_code)
			if result:
				conference.write({'status': 'started'})
				return True
			else:
				return False
		return False

	@api.model
	def moderatorJoinMeeting(self,conference,member):
		api_url = self.env['ir.config_parameter'].get_param('conference.server.api')
		secret = self.env['ir.config_parameter'].get_param('conference.server.api.secret')
		bbb_service = BBB_API(api_url,secret)
		meetting_status = bbb_service.isMeetingRunnung(conference.meeting_id)
		if not meetting_status:
			result = bbb_service.createMeeting(conference.name, conference.meeting_id, conference.access_code,
											   conference.mod_access_code)
			if not result:
				return False
		bbb_service.joinMeeting(member.name,conference.meeting_id,member.access_code)
		return False

	@api.model
	def candidateJoinMeeting(self,conference,member):
		api_url = self.env['ir.config_parameter'].get_param('conference.server.api')
		secret = self.env['ir.config_parameter'].get_param('conference.server.api.secret')
		bbb_service = BBB_API(api_url,secret)
		meetting_status = bbb_service.isMeetingRunnung(conference.meeting_id)
		if not meetting_status:
			return False
		bbb_service.joinMeeting(member.name,conference.meeting_id,member.access_code)
		return False

	@api.model
	def joinMeeting(self,meetingId,memberId):
		for conference in self.env['career.conference'].search([('meeting_id','=',meetingId)]):
			if conference.status =='ended':
				return False
			for member in self.env['career.conference_member'].search([('member_id', '=', memberId)]):
				if member.role=='moderator':
					return self.moderatorJoinMeeting(conference,member)
				if member.role=='candidate':
					return self.candidateJoinMeeting(conference,member)
		return False

	@api.model
	def leaveMeeting(self):
		pass

	@api.model
	def endMeeting(self,meetingId,memberId):
		api_url = self.env['ir.config_parameter'].get_param('conference.server.api')
		secret = self.env['ir.config_parameter'].get_param('conference.server.api.secret')
		bbb_service = BBB_API(api_url, secret)
		for conference in self.env['career.conference'].search([('meeting_id','=',meetingId)]):
			if conference.status =='ended':
				return True
			for member in self.env['career.conference_member'].search([('member_id', '=', memberId)]):
				result = bbb_service.endMeeting(meetingId,member.access_code)
				if result:
					self.env['career.conference'].search([('meeting_id', '=', meetingId)]).write({'status': 'ended'})
					return True
		return False

	@api.model
	def getMeeting(self):
		pass

	@api.model
	def getMeetingInfo(self,meetingId,memberId):
		info = {}
		for conference in self.env['career.conference'].search([('meeting_id','=',meetingId)]):
			info['status']  = conference.status
			if conference.status !='ended':
				api_url = self.env['ir.config_parameter'].get_param('conference.server.api')
				secret = self.env['ir.config_parameter'].get_param('conference.server.api.secret')
				bbb_service = BBB_API(api_url, secret)
				meetting_status = bbb_service.isMeetingRunnung(conference.meeting_id)
				if meetting_status:
					info['runnung'] = True
				else:
					info['runnung'] = 'False'
		return info



class CreateMeetingRequest(object):
	def __init__(self, name, meetingId, attendeePW, moderatorPW):
		self.name = name
		self.meetingId = meetingId
		self.attendeePW = attendeePW
		self.moderatorPW = moderatorPW

	def urlString(self):
		return 'name=%s&meetingID=%s&attendeePW=%s&moderatorPW=%s' % (self.name, self.meetingId, self.attendeePW, self.moderatorPW)


class CreateMeetingResponse(object):
	def __init__(self, xmlString):
		xmldoc = minidom.parseString(xmlString)
		self.returncode = xmldoc.getElementsByTagName('returncode')[0].firstChild.data


class JoinMeetingRequest(object):
	def __init__(self, fullName, meetingId, password):
		self.fullName = fullName
		self.meetingId = meetingId
		self.password = password

	def urlString(self):
		return 'fullName=%s&meetingID=%s&password=%s' % (self.fullName, self.meetingId, self.password)


class JoinMeetingResponse(object):

	def __init__(self, xmlString):
		pass

class MeetingStatusRequest(object):
	def __init__(self, meetingId):
		self.meetingId = meetingId

	def urlString(self):
		return 'meetingID=%s' % ( self.meetingId)


class MeetingStatusResponse(object):

	def __init__(self, xmlString):
		xmldoc = minidom.parseString(xmlString)
		self.returncode = xmldoc.getElementsByTagName('returncode')[0].firstChild.data
		self.running = xmldoc.getElementsByTagName('running')[0].firstChild.data

class EndMeetingRequest(object):
	def __init__(self, meetingId,password):
		self.meetingId = meetingId
		self.password = password

	def urlString(self):
		return 'meetingID=%s&password=%s' % ( self.meetingId,self.password)


class EndMeetingResponse(object):

	def __init__(self, xmlString):
		xmldoc = minidom.parseString(xmlString)
		self.returncode = xmldoc.getElementsByTagName('returncode')[0].firstChild.data

class GetMeetingInfoRequest(object):
	def __init__(self, meetingId,password):
		self.meetingId = meetingId
		self.password = password

	def urlString(self):
		return 'meetingID=%s&password=%s' % ( self.meetingId,self.password)

class GetMeetingInfoResponse(object):

	def __init__(self, xmlString):
		xmldoc = minidom.parseString(xmlString)
		self.returncode = xmldoc.getElementsByTagName('returncode')[0].firstChild.data

class GetMeetingRequest(object):
	def __init__(self):
		pass

	def urlString(self):
		return ''

class GetMeetingResponse(object):

	def __init__(self, xmlString):
		xmldoc = minidom.parseString(xmlString)
		self.returncode = xmldoc.getElementsByTagName('returncode')[0].firstChild.data

class BBB_API(object):
	def __init__(self, endpoint, secret):
		self.endpoint = endpoint
		self.secret = secret

	def call(self,method,request):
		try:
			hash_object = hashlib.sha1('%s%s%s' %(method,request.urlString(),self.secret))
			checkSum = hash_object.hexdigest()
			url_str = '%s/%s?%s&checksum=%s' %(self.endpoint,method,request.urlString(),checkSum)
			print url_str
			content = urllib2.urlopen(url_str).read()
			print content
			return content
		except Exception as exc:
			print exc
			return False

	def createMeeting(self,name,meetingId,attendPw,moderatorPw):
		create_meeting_request = CreateMeetingRequest(name, meetingId, attendPw, moderatorPw)
		content = self.call('create', create_meeting_request)
		create_meeting_response =  CreateMeetingResponse(content)
		if create_meeting_response.returncode =='SUCCESS':
			return True
		return False

	def joinMeeting(self,name,meetingId,password):
		join_meeting_request = JoinMeetingRequest(name, meetingId, password)
		self.call('join', join_meeting_request)
		return True

	def isMeetingRunnung(self,meetingId):
		meeting_status_request = MeetingStatusRequest( meetingId,)
		content = self.call('isMeetingRunning', meeting_status_request)
		meeting_status_response =  MeetingStatusResponse(content)
		return meeting_status_response.returncode=='SUCCESS' and meeting_status_response.running=='true'

	def endMeeting(self, meetingId, password):
		end_meeting_request = EndMeetingRequest( meetingId, password)
		content = self.call('join', end_meeting_request)
		end_meeting_response = EndMeetingResponse(content)
		if end_meeting_response.returncode =='SUCCESS':
			return True
		return False