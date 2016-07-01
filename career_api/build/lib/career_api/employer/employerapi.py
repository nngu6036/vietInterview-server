
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import session_service,ErpInstance
import json

@app.route('/employer/account/login', methods=['POST'],endpoint='employer-account-login')
def login():
    try:
        login = request.values['login']
        password = request.values['password']
        token = session_service.login(app.config['ERP_DB'], login, password)
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
         erpInstance = ErpInstance.fromToken(token,['admin'])
         employer_service = erpInstance.service('career.employer_service')
         if request.method == 'GET':
            company = employer_service.getUserCompany()
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
         erpInstance = ErpInstance.fromToken(token,['admin'])
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
        print 'Company error '
        print request.values
        return jsonify(result=False)