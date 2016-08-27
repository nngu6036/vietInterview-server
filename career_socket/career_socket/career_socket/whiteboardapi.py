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


@socketio.on('whiteboard', namespace='/conference')
def whiteboard(message):
	wb_message =  message['data']
	print 'obj', wb_message
	socketio.emit('whiteboardEvent',{'object':wb_message['object'],'event':wb_message['event'],'memberId':wb_message['memberId']},room=wb_message['meetingId'],namespace='/conference')