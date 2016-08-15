'''
Created on Sep 9, 2016

@author: QuangN
'''
from tinydb import TinyDB,Query
from tinydb.storages import MemoryStorage
from flask import Flask,render_template,session,request
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect,send
import os, json
from career_socket import socketio

db = TinyDB(storage=MemoryStorage)

@socketio.on('connect', namespace='/conference')
def connect():
	print 'Client connected %s' % request.sid


@socketio.on('disconnect', namespace='/conference')
def disconnect():
	Member = Query()
	table = db.table('member')
	if table.search(Member.sid.exists()) and table.search(Member.sid == request.sid):
		table.remove(Member.sid == request.sid)

@socketio.on('test', namespace='/conference')
def test(message):
	print message['data']

@socketio.on('join', namespace='/conference')
def join(message):
	join_message =  message['data']
	print join_message
	join_room(join_message['meetingId'])
	Member = Query()
	table = db.table('member')
	if not table.search(Member.memberid.exists()) or not table.search(Member.memberid==join_message['memberId']):
		table.insert({'sid':request.sid,'meetingid':join_message['meetingId'],'memberid':join_message['memberId'],
					  'name':join_message['name'],'role':join_message['role'],'avail':True})
	socketio.emit('userJoinEvent',{'memberId':join_message['memberId'],
					  'name':join_message['name'],'role':join_message['role']},room=join_message['meetingId'],namespace='/conference')

@socketio.on('leave', namespace='/conference')
def leave(message):
	leave_message =  message['data']
	print leave_message
	leave_room(leave_message['meetingId'])
	Member = Query()
	table = db.table('member')
	if  table.search(Member.memberid.exists()) and table.search(Member.memberid==leave_message['memberId']):
		table.remove(Member.meetingid == leave_message['memberId'])
	if not table.all():
		close_room(leave_message['meetingId'])
	socketio.emit('userLeaveEvent',{'memberId':leave_message['memberId']},room=leave_message['meetingId'],namespace='/conference')

# Video Call Signaling
@socketio.on('signal', namespace='/conference')
def signal(message):
	signal_message =  message['data']
	print signal_message
	if signal_message.type=='availUpdate':
		Member = Query()
		table = db.table('member')
		if  table.search((Member.memberid==signal_message['memberId']) &(Member.meetingid==signal_message['meetingId'])):
			table.update({'status':signal_message['status']},(Member.memberid==signal_message['memberId']) &(Member.meetingid==signal_message['meetingId']))
			socketio.emit('signal',{'type':'memberAvailEvent','memberId':signal_message['memberId'],'status':signal_message['status']},
							room=signal_message['meetingId'],namespace='/conference')
	if signal_message.type == 'availRequest':
		Member = Query()
		table = db.table('member')
		member = table.get((Member.memberid==signal_message['memberId']) &(Member.meetingid==signal_message['meetingId']))
		if member:
			socketio.emit('signal',
						  {'type':'memberAvailEvent','memberId': signal_message['memberId'], 'status': member.status},
						  room=signal_message['meetingId'], namespace='/conference')
		else:
			socketio.emit('signal', {'type':'memberAvailEvent','memberId': signal_message['memberId'], 'status': False},
						  room=signal_message['meetingId'], namespace='/conference')
	if signal_message.type=='candidate':
		signal_message['type'] = 'candidateEvent'
		socketio.emit('signal',signal_message,room=signal_message['meetingId'],namespace='/conference')

@socketio.on('list', namespace='/conference')
def list(message):
	list_message =  message['data']
	print list_message
	Member = Query()
	table = db.table('member')
	memberList =   table.search(Member.meetingid ==list_message['meetingId'])
	socketio.emit('listEvent',[{'memberId':member['memberid'], 'name':member['name'],'role':member['role']}
									   for member in memberList],room=list_message['meetingId'],namespace='/conference')

@socketio.on('chat', namespace='/conference')
def chat(message):
	chat_message =  message['data']
	print chat_message
	socketio.emit('chatEvent',{'text':chat_message['text'],'memberId':chat_message['memberId']},room=chat_message['meetingId'],namespace='/conference')

@socketio.on('question', namespace='/conference')
def question(message):
	question_message =  message['data']
	print question_message
	socketio.emit('questionEvent',{'data':{'title':question_message['title'],'videoUrl':question_message['videoUrl']}},
				  room=question_message['meetingId'],namespace='/conference')