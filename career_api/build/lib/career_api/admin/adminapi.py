
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import ErpInstance,session_service
import json

@app.route('/admin/account/login', methods=['POST'],endpoint='admin-account-login')
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


@app.route('/admin/license', methods=['GET','PUT'],endpoint='admin-license')
def license():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['admin'])
         admin_service = erpInstance.service('career.admin_service')
         if request.method == 'GET':
            licenseList = admin_service.getLicense()
            return jsonify(result=True,licenseList=licenseList)
         if request.method == 'PUT':
            license  = json.loads(request.values['license'])
            admin_service.updateLicense(int(license['id']),license)
            return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'License error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/employer', methods=['GET','PUT','POST'],endpoint='admin-employer')
def employer():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['admin'])
         admin_service = erpInstance.service('career.admin_service')
         if request.method == 'GET':
            employerList = admin_service.getEmployer()
            return jsonify(result=True,employerList=employerList)
         if request.method == 'PUT':
            employer  = json.loads(request.values['employer'])
            admin_service.updateEmployer(int(employer['id']),employer)
            return jsonify(result=True)
         if request.method == 'POST':
            employer  = json.loads(request.values['employer'])
            employerId = admin_service.createEmployer(employer)
            if employerId:
                return jsonify(result=True,employerId=employerId)
            else:
                return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Employer  error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/account/logout', methods=['POST'],endpoint='admin-logout')
def logout():
    try:
        session_service.logout(request.values['token'])
        return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Logout error '
        print request.values
        return jsonify(result=True)



@app.route('/admin/question', methods=['GET'],endpoint='admin-question')
def question():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['admin'])
         admin_service = erpInstance.service('career.admin_service')
         if request.method == 'GET':
            questionList = admin_service.getQuestion()
            return jsonify(result=True,questionList=questionList)
         return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Question error '
        print request.values
        return jsonify(result=False)

@app.route('/admin/question/category', methods=['GET'],endpoint='admin-question-category')
def questionCategory():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['admin'])
         admin_service = erpInstance.service('career.admin_service')
         if request.method == 'GET':
            categoryist = admin_service.getQuestionCategory()
            return jsonify(result=True,categoryist=categoryist)
         return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Question category error '
        print request.values
        return jsonify(result=False)