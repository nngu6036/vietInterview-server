
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import Session,company_obj,company_user_obj, assessment_obj,question_category_obj,interview_obj, interview_question_obj,interview_history_obj,interview_answer_obj,assignment_obj,question_obj,account_obj, common_service,mail_service,report_service
from career_api.proxy import employer_session, edu_hist_obj, document_obj, certificate_obj, user_obj, work_exp_obj,conference_obj
import json
import base64
import os
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
def company(session):
    try:
         user = company_user_obj.get([('user_id','=',session.info['uid'])])
         if request.method == 'GET':
            company = user.getCompanyInfo()
            return jsonify(result=True,company=company)
         if request.method == 'PUT':
            company  = json.loads(request.values['company'])
            company_obj.get(int(company['id'])).updateCompany(company)
            return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Company error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/company/license', methods=['GET'],endpoint='employer-company-license')
@employer_session
def companyLicense(session):
    try:
         user = company_user_obj.get([('user_id','=',session.info['uid'])])
         if request.method == 'GET':
            licenseInfo = user.user_id.company_id.getLicenseStatistic()
            return jsonify(result=True, licenseInfo=licenseInfo)
    except Exception as exc:
        print(exc)
        print 'Company license error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment', methods=['GET','PUT','POST','DELETE'],endpoint='employer-assignment')
@employer_session
def assignment(session):
    try:
         user = company_user_obj.get([('user_id','=',session.info['uid'])])
         if request.method == 'GET':
            assignmentList = user.user_id.company_id.getAssignment()
            return jsonify(result=True,assignmentList=assignmentList)
         if request.method == 'PUT':
            assignment  = json.loads(request.values['assignment'])
            assignment_obj.get(int(assignment['id'])).updateAssignment(assignment)
            return jsonify(result=True)
         if request.method == 'POST':
            assignment  = json.loads(request.values['assignment'])
            assignmentId = user.createAssignment(assignment)
            if assignmentId:
                return jsonify(result=True,assignmentId=assignmentId)
            else:
                return jsonify(result=False)
         if request.method == 'DELETE':
            assignmentId  = int(request.values['assignmentId'])
            result = assignment_obj.get(assignmentId).deleteAssignment()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Assignment error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/open', methods=['POST'],endpoint='employer-assignment-open')
@employer_session
def assignmentOpen(session):
    try:
         if request.method == 'POST':
            assignmentId  = int(request.values['assignmentId'])
            result = assignment_obj.get(assignmentId).action_open()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Open Assignment error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/stats', methods=['GET'],endpoint='employer-assignment-interview-stats')
@employer_session
def interviewStatistics(session):
    try:
         if request.method == 'GET':
            interviewId  = int(request.values['interviewId'])
            stats = interview_obj.get(interviewId).getInterviewStatistic()
            return jsonify(result=True,stats=stats)
    except Exception as exc:
        print(exc)
        print 'Assignment stats error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/close', methods=['POST'],endpoint='employer-assignment-close')
@employer_session
def assignmentClose(session):
    try:
         if request.method == 'POST':
            assignmentId  = int(request.values['assignmentId'])
            result = assignment_obj.get(assignmentId).action_close()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Close Assignment error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/open', methods=['POST'],endpoint='employer-assignment-interview-open')
@employer_session
def interviewOpen(session):
    try:
         if request.method == 'POST':
            interviewId  = int(request.values['interviewId'])
            result = interview_obj.get(interviewId).action_open()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Open Interview error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/close', methods=['POST'],endpoint='employer-assignment-interview-close')
@employer_session
def interviewClose(session):
    try:
         if request.method == 'POST':
            interviewId  = int(request.values['interviewId'])
            result = interview_obj.get(interviewId).action_close()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Close Interview error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview', methods=['GET','PUT','POST','DELETE'],endpoint='employer-assignment-interview')
@employer_session
def interview(session):
    try:
         user = company_user_obj.get([('user_id','=',session.info['uid'])])
         if request.method == 'GET':
            assignmentId = int(request.values['assignmentId'])
            interviewList = assignment_obj.get(assignmentId).getInterview()
            return jsonify(result=True,interviewList=interviewList)
         if request.method == 'PUT':
            interview  = json.loads(request.values['interview'])
            interview_obj.get(int(interview['id'])).updateInterview(interview)
            return jsonify(result=True)
         if request.method == 'POST':
            interview  = json.loads(request.values['interview'])
            interviewId = user.createInterview(int(request.values['assignmentId']),interview)
            if interviewId:
                return jsonify(result=True,interviewId=interviewId)
            else:
                return jsonify(result=False)
         if request.method == 'DELETE':
             interviewId = int(request.values['interviewId'])
             result = interview_obj.get(interviewId).deleteInterview()
             return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/question', methods=['GET','PUT','POST','DELETE'],endpoint='employer-assignment-interview-question')
@employer_session
def interviewQuestion(session):
    try:
         if request.method == 'GET':
            questionList = interview_obj.get(int(request.values['interviewId'])).getInterviewQuestion()
            return jsonify(result=True,questionList=questionList)
         if request.method == 'PUT':
            jQuestions  = json.loads(request.values['questionList'])
            interview_question_obj.updateInterviewQuestion(jQuestions)
            return jsonify(result=True)
         if request.method == 'POST':
            jQuestions  = json.loads(request.values['questionList'])
            questionIds = interview_obj.get(int(request.values['interviewId'])).addInterviewQuestion(jQuestions)
            if questionIds:
                return jsonify(result=True,questionIds=questionIds)
            else:
                return jsonify(result=False)
         if request.method == 'DELETE':
            jQuestionIds  = json.loads(request.values['questionIds'])
            interview_question_obj.removeInterviewQuestion(jQuestionIds)
            return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Interview question error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/conference', methods=['GET'],endpoint='employer-assignment-interview-conference')
@employer_session
def interviewConference(session):
    try:
         if request.method == 'GET':
            conference = conference_obj.get(int(request.values['conferenceId'])).getConference()
            memberList = conference_obj.get(int(request.values['conferenceId'])).getConferenceMember()
            return jsonify(result=True,conference=conference,memberList=memberList)
    except Exception as exc:
        print(exc)
        print 'Interview conference error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/invite', methods=['POST'],endpoint='employer-assignment-interview-invite')
@employer_session
def invitation(session):
    try:
         user = company_user_obj.get([('user_id', '=', session.info['uid'])])
         if request.method == 'POST':
            emails  = json.loads(request.values['candidates'])
            interviewId  = int(request.values['interviewId'])
            subject  = request.values['subject']
            schedules = json.loads(request.values['schedule'])if 'schedule' in request.values else False
            result  = user.inviteCandidate(emails,subject,schedules,interviewId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Interview invitation error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assignment/interview/answer', methods=['GET'],endpoint='employer-assignment-interview-answer')
@employer_session
def candidateAnswer(session):
    try:
         if request.method == 'GET':
            interviewId  = int(request.values['interviewId'])
            responseList  = interview_obj.get(interviewId).getInterviewResponse()
            return jsonify(responseList=responseList)
    except Exception as exc:
        print(exc)
        print 'Get answer error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/assessment', methods=['GET','POST'],endpoint='employer-assignment-interview-assessment')
@employer_session
def candidateAssessment(session):
    try:
         user = company_user_obj.get([('user_id','=',session.info['uid'])])
         if request.method == 'GET':
            applicantId  = int(request.values['candidateId'])
            assessmentId  = int(request.values['assessmentId'])
            selfAssessmentResult  = user.getSelfAssessment(assessmentId,applicantId)
            otherAssessmentResultList  = user.getOtherAssessment(assessmentId,applicantId)
            return jsonify(result=True,selfAssessmentResult=selfAssessmentResult,otherAssessmentResultList=otherAssessmentResultList)
         if request.method == 'POST':
            assessmentResult  = json.loads(request.values['assessmentResult'])
            assessmentId  = user.submitAssessment(assessmentResult)
            return jsonify(result=True,assessmentId=assessmentId)
    except Exception as exc:
        print(exc)
        print 'Candidate Assessment error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/shortlist', methods=['POST'],endpoint='employer-assignment-interview-shortlist')
@employer_session
def candidateShortlist(session):
    try:
         user = company_user_obj.get([('user_id','=',session.info['uid'])])
         if request.method == 'POST':
            applicantId  = int(request.values['candidateId'])
            result  = user.shortlistCandidate(applicantId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Candidate shortlist error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/question', methods=['GET'],endpoint='employer-question')
@employer_session
def question(session):
    try:
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            questionList = question_obj.getQuestion(lang)
            return jsonify(result=True,questionList=questionList)
         return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Question error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/question/category', methods=['GET'],endpoint='admin-question-employer')
@employer_session
def questionCategory(session):
    try:
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            categoryList = question_category_obj.getQuestionCategory(lang)
            return jsonify(result=True,categoryList=categoryList)
         return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Question category error '
        print request.values
        return jsonify(result=False)


@app.route('/employer/assessment', methods=['GET'],endpoint='employer-assessment')
@employer_session
def assessment(session):
    try:
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            assessment  = assessment_obj.getAssessment(lang)
            return jsonify(result=True,assessment=assessment)
    except Exception as exc:
        print(exc)
        print 'Assessment error '
        print request.values
        return jsonify(result=False)



@app.route('/employer/interview/candidate', methods=['GET'],endpoint='employer-interview-caandidate')
@employer_session
def candidate(session):
    try:
         interviewId  = int(request.values['interviewId'])
         if request.method == 'GET':
            candidateList  = interview_obj.get(interviewId).getCandidate()
            return jsonify(result=True,candidateList=candidateList)
    except Exception as exc:
        print(exc)
        print 'Candidate error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/report/assessment', methods=['GET'],endpoint='employer-report-assessment')
@employer_session
def assessmentReport(session):
    try:
         candidateId  = int(request.values['candidateId'])
         if request.method == 'GET':
            content  = report_service.getAssessmentSummaryReport(candidateId)
            return jsonify(result=True,content=content)
    except Exception as exc:
        print(exc)
        print 'Candidate error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/account/changepass', methods=['POST'],endpoint='common-account-changepass')
@employer_session
def changePass(session):
    try:
        oldpass = request.values['oldpass']
        newpass = request.values['newpass']
        result = account_obj.changePass( app.config['ERP_DB'],session.info['user'],oldpass,newpass)
        return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Change pass error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/conference/launch', methods=['POST'],endpoint='employer-assignment-interview-conference-launch')
@employer_session
def conferenceLaunch(session):
    try:
         if request.method == 'POST':
            conferenceId  = int(request.values['conferenceId'])
            result = conference_obj.get(conferenceId).action_launch()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Launch conference error '
        print request.values
        return jsonify(result=False)

@app.route('/employer/assignment/interview/conference', methods=['GET'],endpoint='employer-assignment-interview-conference')
@employer_session
def conference(session):
    try:
         if request.method == 'GET':
            conferenceList = conference_obj.getConference()
            return jsonify(result=True,conferenceList=conferenceList)
    except Exception as exc:
        print(exc)
        print 'Conference error '
        print request.values
        return jsonify(result=False)
