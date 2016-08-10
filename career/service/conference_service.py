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
	def openMeeting(self,conferenceId):
		for conference in self.env['career.conference'].browse(conferenceId):
			api_url = self.env['ir.config_parameter'].get_param('conference.server.api')
			secret = self.env['ir.config_parameter'].get_param('conference.server.api.secret')
			bbb_service = BBB_API(api_url,secret)
			mod_pw = conference.mod_access_code
			interviewee_pw = conference.access_code
			create_meeting_request = CreateMettingRequest(conference.name,conference.meeting_id,interviewee_pw,mod_pw)
			bbb_service.call('create',create_meeting_request)
			return True
		return False


	@api.model
	def joinMeeting(self,meetingId,):
		pass

	@api.model
	def leaveMeeting(self):
		pass

	@api.model
	def endMeeting(self):
		pass

	@api.model
	def meetingStatus(self):
		pass

	@api.model
	def getMeeting(self):
		pass

	@api.model
	def getMeetingInfo(self):
		pass


class CreateMettingRequest(object):
	def __init__(self, name, meetingId, attendeePW, moderatorPW):
		self.name = name
		self.meetingId = meetingId
		self.attendeePW = attendeePW
		self.moderatorPW = moderatorPW

	def urlString(self):
		return 'name=%s&meetingID=%s&attendeePW=%s&moderatorPW=%s' % (self.name, self.meetingId, self.attendeePW, self.moderatorPW)


class CreateMettingResponse(object):
	def __init__(self, xmlString):
		xmldoc = minidom.parseString(xmlString)
		self.returnCode = xmldoc.getElementsByTagName('returncode')[0]
		self.meeting = xmldoc.getElementsByTagName('meeting')[0]


class JoinMettingRequest(object):
	def __init__(self, fullName, meetingId, password):
		self.fullName = fullName
		self.meetingId = meetingId
		self.password = password

	def urlString(self):
		return 'fullName=%s&meetingID=%s&password=%s' % (self.fullName, self.meetingId, self.password)


class JoinMettingResponse(object):
	def __init__(self, xmlString):
		xmldoc = minidom.parseString(xmlString)


class BBB_API(object):
	def __init__(self, endpoint, secret):
		self.endpoint = endpoint
		self.secret = secret

	def call(self,method,request):
		print request.urlString()
		hash_object = hashlib.sha1('%s%s' %(method,request.urlString()))
		checkSum = hash_object.hexdigest()
		print checkSum
		url_str = '%s/%s?%s&checksum=%s' %(self.endpoint,method,request.urlString(),checkSum)
		print url_str
		rsp = urllib2.urlopen(url_str)
		content = rsp.read()
		print content
		return True