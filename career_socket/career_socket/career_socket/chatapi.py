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



@socketio.on('chat', namespace='/conference')
def chat(message):
	chat_message =  message['data']
	print 'chat', chat_message
	socketio.emit('chatEvent',{'text':chat_message['text'],'memberId':chat_message['memberId']},room=chat_message['meetingId'],namespace='/conference')
