# -*- coding: utf-8 -*-

from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
import base64
import datetime

# monkey patching to allow scr not to be remove in html clean
# see openerp.tools.mail.py
import lxml.html.clean as clean
from datetime import date, timedelta



class ConferenceService(osv.AbstractModel):
	_name = 'career.conference_service'

	@api.model
	def openMeeting(self):
		pass

	@api.model
	def joinMeeting(self):
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
		return 'name=%s&meetingId=%s&attendeePW=%s&moderatorPW=%s' % (
		self.name, self.meetingId, self.attendeePW, self.moderatorPW)


class CreateMettingResponse(object):
	def __init__(self, xmlString):
		pass

class BBB_API(object):
	def __init__(self, endpoint, secret):
		self.endpoint = endpoint
		self.secret = secret
