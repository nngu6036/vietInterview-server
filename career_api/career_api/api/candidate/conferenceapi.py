
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import interview_service, employer_session,conference_session,conference_service
import json, os, datetime
from werkzeug.utils import secure_filename
import base64



@app.route('/conference', methods=['GET'],endpoint='conference')
@conference_session
def conference(meetingId,memberId):
    try:
         if request.method == 'GET':
            conferenceInfo = conference_service.getMeetingInfo(meetingId,memberId)
            return jsonify(result=True,info=conferenceInfo)
    except Exception as exc:
        print(exc)
        print 'Conference error '
        print request.values
        return jsonify(result=False)


@app.route('/conference/question', methods=['GET'],endpoint='conference-question')
@conference_session
def question(meetingId,memberId):
    try:
         if request.method == 'GET':
            questionList = conference_service.getInterviewQuestion(meetingId)
            return jsonify(result=True,questionList=questionList)
    except Exception as exc:
        print(exc)
        print 'Conference question error '
        print request.values
        return jsonify(result=False)


@app.route('/conference/open', methods=['POST'],endpoint='conference-open')
@employer_session
def openConference(session):
    try:
         if request.method == 'POST':
            conferenceId =  int(request.values['conferenceId'])
            result  = conference_service.openMeeting(conferenceId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Conference open error '
        print request.values
        return jsonify(result=False)

@app.route('/conference/end', methods=['POST'],endpoint='conference-end')
@conference_session
def endConference(meetingId,memberId):
    try:
         if request.method == 'POST':
            result  = conference_service.endMeeting(meetingId,memberId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Conference end error '
        print request.values
        return jsonify(result=False)


