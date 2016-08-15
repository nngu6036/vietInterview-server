#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.

from career_socket import app, socketio
import erppeek
from flask import jsonify, abort, request,render_template
import time
from threading import Thread
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',port=5000,debug=True)