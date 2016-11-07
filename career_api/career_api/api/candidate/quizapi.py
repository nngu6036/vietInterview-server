
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import  interview_session
import json, os, datetime
from werkzeug.utils import secure_filename
import base64



@app.route('/quiz', methods=['GET'],endpoint='quiz')
@interview_session
def quiz(applicant):
    try:
         if request.method == 'GET':
            interview = applicant.interview_id.getInterview()
            history = applicant.getInterviewHistory()
            candidate = applicant.getCandidateInfo()
            return jsonify(result=True,interview=interview,history=history,candidate=candidate)
    except Exception as exc:
        print(exc)
        print 'Quiz interview error '
        print request.values
        return jsonify(result=False)


@app.route('/quiz/question', methods=['GET'],endpoint='quiz-question')
@interview_session
def question(applicant):
    try:
         if request.method == 'GET':
            questionList = applicant.interview_id.getInterviewQuestion()
            if not isinstance(questionList, list):
                questionList = [questionList]
            return jsonify(result=True,questionList=questionList)
    except Exception as exc:
        print(exc)
        print 'Quiz question error '
        print request.values
        return jsonify(result=False)


@app.route('/quiz/start', methods=['POST'],endpoint='quiz-start')
@interview_session
def startInterview(applicant):
    try:
         if request.method == 'POST':
            result  = applicant.startInterview()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Quiz start error '
        print request.values
        return jsonify(result=False)

@app.route('/quiz/finish', methods=['POST'],endpoint='quiz-finish')
@interview_session
def finishInterview(applicant):
    try:
         if request.method == 'POST':
            result  = applicant.stopInterview()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Quiz stop error '
        print request.values
        return jsonify(result=False)



@app.route('/quiz/answer', methods=['POST'],endpoint='quiz-answer')
@interview_session
def submitAnswer(applicant):
    try:
         if request.method == 'POST':
            questionId  = int(request.values['questionId'])
            optionId = int(request.values['optionId'])
            result  = applicant.submitQuizAnswer(questionId,optionId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Quiz answer error '
        print request.values
        return jsonify(result=False)

