'''
Created on Sep 9, 2016

@author: QuangN
'''

from flask import Flask,render_template,session,request
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect,send
import os
from career_socket import socketio


@socketio.on('connect', namespace='/conference')
def connect():
	print('Client connected')
	print request.sid


@socketio.on('disconnect', namespace='/conference')
def disconnect():
	print('Client disconnected')
	print request.sid

@socketio.on('test', namespace='/conference')
def test(message):
	print message['data']

@socketio.on('join', namespace='/conference')
def join(message):
	print 'Client join'
	print message['data']
