
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import Session, employer_session,account_service
import json

@app.route('/employer/account/login', methods=['POST'],endpoint='employer-account-login')
def login():
    try:
        login = request.values['email']
        password = request.values['password']
        token = Session.start( login, password,'employer')
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
        Session.stop(request.values['token'])
        return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Logout error '
        print request.values
        return jsonify(result=True)




@app.route('/employer/company', methods=['GET','PUT'],endpoint='employer-company')
@employer_session
def company(employer):
    try:
         if request.method == 'GET':
            company = employer.getCompanyInfo()
            return jsonify(result=True,company=company)
         if request.method == 'PUT':
            company  = json.loads(request.values['company'])
            employer.company_id.updateCompany(company)
            return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Company error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/company/license', methods=['GET'],endpoint='employer-company-license')
@employer_session
def companyLicense(employer):
    try:
         if request.method == 'GET':
            licenseInfo = employer.company_id.getLicenseStatistic()
            return jsonify(result=True, licenseInfo=licenseInfo)
    except Exception as exc:
        print(exc)
        print 'Company license error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment', methods=['GET','PUT','POST','DELETE'],endpoint='employer-assignment')
@employer_session
def assignment(employer):
    try:
         if request.method == 'GET':
            assignmentList = employer.company_id.getAssignment()
            return jsonify(result=True,assignmentList=assignmentList)
         if request.method == 'PUT':
            assignment  = json.loads(request.values['assignment'])
            result = employer.updateAssignment(assignment)
            return jsonify(result=result)
         if request.method == 'POST':
            assignment  = json.loads(request.values['assignment'])
            assignmentId = employer.createAssignment(assignment)
            if assignmentId:
                return jsonify(result=True,assignmentId=assignmentId)
            else:
                return jsonify(result=False)
         if request.method == 'DELETE':
            assignmentId  = int(request.values['assignmentId'])
            result = employer.deleteAssignment(assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Assignment error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/open', methods=['POST'],endpoint='employer-assignment-open')
@employer_session
def assignmentOpen(employer):
    try:
         if request.method == 'POST':
            assignmentId  = int(request.values['assignmentId'])
            result = employer.openAssignment(assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Open Assignment error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/stats', methods=['GET'],endpoint='employer-assignment-interview-stats')
@employer_session
def interviewStatistics(employer):
    try:
         if request.method == 'GET':
            interviewId  = int(request.values['interviewId'])
            stats = employer.getInterviewStatistic(interviewId)
            return jsonify(result=True,stats=stats)
    except Exception as exc:
        print(exc)
        print 'Assignment stats error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/close', methods=['POST'],endpoint='employer-assignment-close')
@employer_session
def assignmentClose(employer):
    try:
         if request.method == 'POST':
            assignmentId  = int(request.values['assignmentId'])
            result = employer.closeAssignment(assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Close Assignment error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/open', methods=['POST'],endpoint='employer-assignment-interview-open')
@employer_session
def interviewOpen(employer):
    try:
         if request.method == 'POST':
            interviewId = int(request.values['interviewId'])
            result = employer.openInterview(interviewId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Open Interview error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/close', methods=['POST'],endpoint='employer-assignment-interview-close')
@employer_session
def interviewClose(employer):
    try:
         if request.method == 'POST':
            interviewId  = int(request.values['interviewId'])
            result = employer.closeInterview(interviewId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Close Interview error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview', methods=['GET','PUT','POST','DELETE'],endpoint='employer-assignment-interview')
@employer_session
def interview(employer):
    try:
         if request.method == 'GET':
            assignmentId = int(request.values['assignmentId'])
            interviewList = employer.getInterviewList(assignmentId)
            return jsonify(result=True,interviewList=interviewList)
         if request.method == 'PUT':
            interview  = json.loads(request.values['interview'])
            result = employer.updateInterview(interview)
            return jsonify(result=result)
         if request.method == 'POST':
            interview  = json.loads(request.values['interview'])
            interviewId = employer.createInterview(int(request.values['assignmentId']),interview)
            if interviewId:
                return jsonify(result=True,interviewId=interviewId)
            else:
                return jsonify(result=False)
         if request.method == 'DELETE':
             interviewId = int(request.values['interviewId'])
             result = employer.deleteInterview(interviewId)
             return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/question', methods=['GET','PUT','POST','DELETE'],endpoint='employer-assignment-interview-question')
@employer_session
def interviewQuestion(employer):
    try:
         if request.method == 'GET':
            questionList = employer.get().getInterviewQuestion(int(request.values['interviewId']))
            return jsonify(result=True,questionList=questionList)
         if request.method == 'PUT':
            jQuestions  = json.loads(request.values['questionList'])
            employer.updateInterviewQuestion(jQuestions)
            return jsonify(result=True)
         if request.method == 'POST':
            jQuestions  = json.loads(request.values['questionList'])
            questionIds = employer.addInterviewQuestion(int(request.values['interviewId']),jQuestions)
            if questionIds:
                return jsonify(result=True,questionIds=questionIds)
            else:
                return jsonify(result=False)
         if request.method == 'DELETE':
             jQuestionIds  = json.loads(request.values['questionIds'])
             employer.removeInterviewQuestion(jQuestionIds)
             return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Interview question error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/invite', methods=['POST'],endpoint='employer-assignment-interview-invite')
@employer_session
def invitation(employer):
    try:
         if request.method == 'POST':
            candidateList  = json.loads(request.values['candidateList'])
            interviewId  = int(request.values['interviewId'])
            subject  = request.values['subject']
            result  = employer.inviteCandidate(candidateList,subject,interviewId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview invitation error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/answer', methods=['GET'],endpoint='employer-assignment-interview-answer')
@employer_session
def candidateAnswer(employer):
    try:
         if request.method == 'GET':
            interviewId  = int(request.values['interviewId'])
            responseList  = employer.getInterviewResponse(interviewId)
            return jsonify(responseList=responseList)
    except Exception as exc:
        print(exc)
        print 'Get answer error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/assessment', methods=['GET','POST'],endpoint='employer-assignment-interview-assessment')
@employer_session
def candidateAssessment(employer):
    try:
         if request.method == 'GET':
            applicantId  = int(request.values['candidateId'])
            assessmentId  = int(request.values['assessmentId'])
            selfAssessmentResult  = employer.getSelfAssessment(assessmentId,applicantId)
            otherAssessmentResultList  = employer.getOtherAssessment(assessmentId,applicantId)
            return jsonify(result=True,selfAssessmentResult=selfAssessmentResult,otherAssessmentResultList=otherAssessmentResultList)
         if request.method == 'POST':
            assessmentResult  = json.loads(request.values['assessmentResult'])
            assessmentId  = employer.submitAssessment(assessmentResult)
            return jsonify(result=True,assessmentId=assessmentId)
    except Exception as exc:
        print(exc)
        print 'Candidate Assessment error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/shortlist', methods=['POST'],endpoint='employer-assignment-interview-shortlist')
@employer_session
def candidateShortlist(employer):
    try:
         if request.method == 'POST':
            applicantId  = int(request.values['candidateId'])
            result  = employer.shortlistCandidate(applicantId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Candidate shortlist error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/interview/candidate', methods=['GET'],endpoint='employer-interview-caandidate')
@employer_session
def candidate(employer):
    try:
         interviewId  = int(request.values['interviewId'])
         if request.method == 'GET':
            candidateList  = employer.getCandidate(interviewId)
            return jsonify(result=True,candidateList=candidateList)
    except Exception as exc:
        print(exc)
        print 'Candidate error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/report/assessment', methods=['GET'],endpoint='employer-report-assessment')
@employer_session
def assessmentReport(employer):
    try:
         candidateId  = int(request.values['candidateId'])
         if request.method == 'GET':
            content  = employer.getAssessmentSummaryReport(candidateId)
            return jsonify(result=True,content=content)
    except Exception as exc:
        print(exc)
        print 'Candidate error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/account/changepass', methods=['POST'],endpoint='common-account-changepass')
@employer_session
def changePass(employer):
    try:
        oldpass = request.values['oldpass']
        newpass = request.values['newpass']
        result = account_service.changePass( app.config['ERP_DB'],employer.user_id.login,oldpass,newpass)
        return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Change pass error '
        print request.values
        return jsonify(result=False)



@app.route('/employer/assignment/interview/conference', methods=['GET'],endpoint='employer-assignment-interview-conference')
@employer_session
def conference(employer):
    try:
         if request.method == 'GET':
            conferenceList = employer.getConference()
            return jsonify(result=True,conferenceList=conferenceList)
    except Exception as exc:
        print(exc)
        print 'Conference error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/conference/open', methods=['POST'],endpoint='employer-assignment-interview-conference-open')
@employer_session
def openConference(employer):
    try:
         if request.method == 'POST':
            conferenceId =  int(request.values['conferenceId'])
            result  = employer.openConference(conferenceId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Conference open error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/conference/end', methods=['POST'],endpoint='employer-assignment-interview-conference-end')
@employer_session
def endConference(employer):
    try:
         if request.method == 'POST':
             conferenceId = int(request.values['conferenceId'])
             result = employer.closeConference(conferenceId)
             return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Conference end error '
        print request.values
        return jsonify(result=False)
