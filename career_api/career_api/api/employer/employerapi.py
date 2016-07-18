
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import session_service,ErpInstance
import json

@app.route('/employer/account/login', methods=['POST'],endpoint='employer-account-login')
def login():
    try:
        login = request.values['email']
        password = request.values['password']
        token = session_service.login(app.config['ERP_DB'], login, password,'employer')
        if token:
            return jsonify(result=True,token=token)
        raise Exception('Invalid account %s or password %s' % (login, password))
    except Exception as exc:
        print(exc)
        print 'Login error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/account/logout', methods=['POST'],endpoint='employer-logout')
def logout():
    try:
        session_service.logout(request.values['token'])
        return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Logout error '
        print request.values
        return jsonify(result=True)


@app.route('/employer/company', methods=['GET','PUT'],endpoint='employer-company')
def company():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'GET':
            company = employer_service.getCompany()
            return jsonify(result=True,company=company)
         if request.method == 'PUT':
            company  = json.loads(request.values['company'])
            employer_service.updateCompany(int(company['id']),company)
            return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Company error '
        print request.values
        return jsonify(result=False)




@app.route('/employer/assignment', methods=['GET','PUT','POST'],endpoint='employer-assignment')
def assignment():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'GET':
            assignmentList = employer_service.getAssignment()
            return jsonify(result=True,assignmentList=assignmentList)
         if request.method == 'PUT':
            assignment  = json.loads(request.values['assignment'])
            employer_service.updateAssignment(int(assignment['id']),assignment)
            return jsonify(result=True)
         if request.method == 'POST':
            assignment  = json.loads(request.values['assignment'])
            assignmentId = employer_service.createAssignment(assignment)
            if assignmentId:
                return jsonify(result=True,assignmentId=assignmentId)
            else:
                return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Assignment error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/open', methods=['POST'],endpoint='employer-assignment-open')
def assignmentOpen():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'POST':
            assignmentId  = int(request.values['assignmentId'])
            result = employer_service.openAssignment(assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Open Assignment error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/open', methods=['POST'],endpoint='employer-assignment-close')
def assignmentClose():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'POST':
            assignmentId  = int(request.values['assignmentId'])
            result = employer_service.closeAssignment(assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Open Assignment error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview', methods=['GET','PUT','POST'],endpoint='employer-assignment-interview')
def interview():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'GET':
            interview = employer_service.getInterview(int(request.values['assignmentId']))
            return jsonify(result=True,interview=interview)
         if request.method == 'PUT':
            interview  = json.loads(request.values['interview'])
            employer_service.updateInterview(int(interview['id']),interview)
            return jsonify(result=True)
         if request.method == 'POST':
            interview  = json.loads(request.values['interview'])
            interviewId = employer_service.createInterview(int(request.values['assignmentId']),interview)
            if interviewId:
                return jsonify(result=True,interviewId=interviewId)
            else:
                return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Interview error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/question', methods=['GET','PUT','POST','DELETE'],endpoint='employer-assignment-interview-question')
def question():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'GET':
            questionList = employer_service.getInterviewQuestion(int(request.values['interviewId']))
            return jsonify(result=True,questionList=questionList)
         if request.method == 'PUT':
            jQuestions  = json.loads(request.values['questionList'])
            employer_service.updateInterviewQuestion(jQuestions)
            return jsonify(result=True)
         if request.method == 'POST':
            jQuestions  = json.loads(request.values['questionList'])
            questionIds = employer_service.addInterviewQuestion(int(request.values['interviewId']),jQuestions)
            if questionIds:
                return jsonify(result=True,questionIds=questionIds)
            else:
                return jsonify(result=False)
         if request.method == 'DELETE':
            jQuestionIds  = json.loads(request.values['questionIds'])
            employer_service.removeInterviewQuestion(jQuestionIds)
            return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Interview question error '
        print request.values
        return jsonify(result=False)



@app.route('/employer/assignment/interview/invite', methods=['POST'],endpoint='employer-assignment-interview-invite')
def invitation():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         email_service = erpInstance.service('career.mail_service')
         if request.method == 'POST':
            emails  = json.loads(request.values['candidates'])
            interviewId  = int(request.values['interviewId'])
            subject  = request.values['subject']
            result  = email_service.sendInterviewInvitation(interviewId,emails,subject)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview invitation error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/answer', methods=['GET'],endpoint='employer-assignment-interview-answer')
def candidateAnswer():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'GET':
            interviewId  = int(request.values['interviewId'])
            responseList  = employer_service.getInterviewResponse(interviewId)
            return jsonify(responseList=responseList)
    except Exception as exc:
        print(exc)
        print 'Get answer error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/assessment', methods=['GET','POST'],endpoint='employer-assignment-interview-assessment')
def candidateAssessment():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'GET':
            applicantId  = int(request.values['candidateId'])
            assessmentId  = int(request.values['assessmentId'])
            selfAssessmentResult  = employer_service.getSelfAssessment(assessmentId,applicantId)
            otherAssessmentResultList  = employer_service.getOtherAssessment(assessmentId,applicantId)
            return jsonify(result=True,selfAssessmentResult=selfAssessmentResult,otherAssessmentResultList=otherAssessmentResultList)
         if request.method == 'POST':
            assessmentResult  = json.loads(request.values['assessmentResult'])
            result  = employer_service.submitAssessment(assessmentResult)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Candidate Assessment error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/question', methods=['GET'],endpoint='employer-question')
def question():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         content_service = erpInstance.service('career.content_service')
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            questionList = content_service.getQuestion(lang)
            return jsonify(result=True,questionList=questionList)
         return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Question error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/question/category', methods=['GET'],endpoint='admin-question-employer')
def questionCategory():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         content_service = erpInstance.service('career.content_service')
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            categoryList = content_service.getQuestionCategory(lang)
            return jsonify(result=True,categoryList=categoryList)
         return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Question category error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assessment', methods=['GET'],endpoint='employer-assessment')
def assessment():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employer'])
         content_service = erpInstance.service('career.content_service')
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            assessment  = content_service.getAssessment(lang)
            return jsonify(result=True,assessment=assessment)
    except Exception as exc:
        print(exc)
        print 'Assessment error '
        print request.values
        return jsonify(result=False)



@app.route('/employer/assignment/candidate', methods=['GET'],endpoint='employer-assignment-caandidate')
def candidate():
    try:
         token  = request.values['token']
         assignmentId  = int(request.values['assignmentId'])
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'GET':
            candidateList  = employer_service.getAssignmentCandidate(assignmentId)
            return jsonify(result=True,candidateList=candidateList)
    except Exception as exc:
        print(exc)
        print 'Candidate error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/report/assessment', methods=['GET'],endpoint='employer-report-assessment')
def assessmentReport():
    try:
         token  = request.values['token']
         candidateId  = int(request.values['candidateId'])
         erpInstance = ErpInstance.fromToken(token,['employer'])
         employer_service = erpInstance.service('career.report_service')
         if request.method == 'GET':
            content  = employer_service.getAssessmentSummaryReport(candidateId)
            return jsonify(result=True,content=content)
    except Exception as exc:
        print(exc)
        print 'Candidate error '
        print request.values
        return jsonify(result=False)

