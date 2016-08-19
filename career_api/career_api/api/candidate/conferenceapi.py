
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import conference_session
import json, os, datetime
from werkzeug.utils import secure_filename
import base64



@app.route('/conference', methods=['GET'],endpoint='conference')
@conference_session
def conference(member):
    try:
         if request.method == 'GET':
            conferenceInfo = member.getMeetingInfo()
            return jsonify(result=True,info=conferenceInfo)
    except Exception as exc:
        print(exc)
        print 'Conference error '
        print request.values
        return jsonify(result=False)



@app.route('/conference/answer', methods=['POST'],endpoint='conference-answer')
@conference_session
def submitAnswer(member):
    try:
         if request.method == 'POST':
            questionId  = int(request.values['questionId'])
            videoUrl = request.values['videoUrl']
            candidateMemberId = request.values['candidateMemberId']
            result  = member.submitInterviewAnswer(candidateMemberId,questionId,videoUrl)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview answer error '
        print request.values
        return jsonify(result=False)



@app.route('/conference/assessment', methods=['GET','POST'],endpoint='conference-assessment')
@conference_session
def candidateAssessment(member):
    try:
         if request.method == 'POST':
            candidateMemberId = request.values['candidateMemberId']
            assessmentResult  = json.loads(request.values['assessmentResult'])
            assessmentId  = member.submitAssessment(candidateMemberId,assessmentResult)
            return jsonify(result=True,assessmentId=assessmentId)
    except Exception as exc:
        print(exc)
        print 'Candidate Assessment error '
        print request.values
        return jsonify(result=False)