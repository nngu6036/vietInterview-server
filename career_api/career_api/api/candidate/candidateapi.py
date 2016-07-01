
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import guest_service
import json, os, datetime
from werkzeug.utils import secure_filename
import base64



@app.route('/candidate/interview', methods=['GET'],endpoint='candidate-interview')
def interview():
    try:
         inviteCode  = request.values['code']
         if request.method == 'GET':
            interview = guest_service.getInterview(inviteCode)
            history = guest_service.getInterviewHistory(inviteCode)
            candidate = guest_service.getCandidate(inviteCode)
            return jsonify(result=True,interview=interview,history=history,candidate=candidate)
    except Exception as exc:
        print(exc)
        print 'Candidate interview error '
        print request.values
        return jsonify(result=False)


@app.route('/candidate/interview/question', methods=['GET'],endpoint='candidate-interview-question')
def question():
    try:
         inviteCode  = request.values['code']
         if request.method == 'GET':
            questionList = guest_service.getInterviewQuestion(inviteCode)
            return jsonify(result=True,questionList=questionList)
    except Exception as exc:
        print(exc)
        print 'Interview question error '
        print request.values
        return jsonify(result=False)



@app.route('/candidate/interview/start', methods=['POST'],endpoint='candidate-interview-start')
def startInterview():
    try:
         inviteCode  = request.values['code']
         if request.method == 'POST':
            result  = guest_service.startInterview(inviteCode)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview start error '
        print request.values
        return jsonify(result=False)

@app.route('/candidate/interview/finish', methods=['POST'],endpoint='candidate-interview-finish')
def finishInterview():
    try:
         inviteCode  = request.values['code']
         if request.method == 'POST':
            result  = guest_service.finishInterview(inviteCode)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview start error '
        print request.values
        return jsonify(result=False)



@app.route('/candidate/interview/answer', methods=['POST'],endpoint='candidate-interview-answer')
def submitAnswer():
    try:
         inviteCode  = request.values['code']
         if request.method == 'POST':
            questionId  = int(request.values['questionId'])
            videoUrl = request.values['videoUrl']
            result  = guest_service.submitInterviewAnswer(inviteCode,questionId,videoUrl)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview answer error '
        print request.values
        return jsonify(result=False)

@app.route('/candidate/interview/document', methods=['POST'],endpoint='candidate-interview-document')
def attachDocument():
    try:
         inviteCode  = request.values['code']
         if request.method == 'POST':
            base64FileData  = request.values['file']
            filename = request.values['filename']
            comment = request.values['comment']
            fileData = base64.urlsafe_b64decode(base64FileData.encode('UTF-8'))
            server_fname = os.path.join(app.config['FILE_UPLOAD_FOLDER'],  '%s%s' %( datetime.datetime.now().strftime('%S%M%H%m%d%Y') , secure_filename(filename)))
            with open(server_fname, 'wb') as theFile:
                theFile.write(fileData)
            result  = guest_service.attachDocument(inviteCode,filename,server_fname,comment)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Attach document error '
        print request.values
        return jsonify(result=False)
