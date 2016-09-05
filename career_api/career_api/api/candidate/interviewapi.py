
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import  interview_session
import json, os, datetime
from werkzeug.utils import secure_filename
import base64



@app.route('/interview', methods=['GET'],endpoint='interview')
@interview_session
def interview(applicant):
    try:
         if request.method == 'GET':
            interview = applicant.interview_id.getInterview()
            history = applicant.getInterviewHistory()
            candidate = applicant.getCandidateInfo()
            return jsonify(result=True,interview=interview,history=history,candidate=candidate)
    except Exception as exc:
        print(exc)
        print 'Candidate interview error '
        print request.values
        return jsonify(result=False)


@app.route('/interview/question', methods=['GET'],endpoint='interview-question')
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
        print 'Interview question error '
        print request.values
        return jsonify(result=False)


@app.route('/interview/start', methods=['POST'],endpoint='interview-start')
@interview_session
def startInterview(applicant):
    try:
         if request.method == 'POST':
            result  = applicant.startInterview()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview start error '
        print request.values
        return jsonify(result=False)

@app.route('/interview/finish', methods=['POST'],endpoint='interview-finish')
@interview_session
def finishInterview(applicant):
    try:
         if request.method == 'POST':
            result  = applicant.stopInterview()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview start error '
        print request.values
        return jsonify(result=False)



@app.route('/interview/answer', methods=['POST'],endpoint='interview-answer')
@interview_session
def submitAnswer(applicant):
    try:
         if request.method == 'POST':
            questionId  = int(request.values['questionId'])
            videoUrl = request.values['videoUrl']
            result  = applicant.submitInterviewAnswer(questionId,videoUrl)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview answer error '
        print request.values
        return jsonify(result=False)

@app.route('/interview/document', methods=['POST'],endpoint='interview-document')
@interview_session
def attachDocument(applicant):
    try:
         if request.method == 'POST':
            base64FileData  = request.values['file']
            filename = request.values['filename']
            comment = request.values['comment']
            fileData = base64.urlsafe_b64decode(base64FileData.encode('UTF-8'))
            server_fname = os.path.join(app.config['FILE_UPLOAD_FOLDER'],  '%s%s' %( datetime.datetime.now().strftime('%S%M%H%m%d%Y') , secure_filename(filename)))
            with open(server_fname, 'wb') as theFile:
                theFile.write(fileData)
            result  = applicant.attachDocument(filename,server_fname,comment)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Attach document error '
        print request.values
        return jsonify(result=False)
