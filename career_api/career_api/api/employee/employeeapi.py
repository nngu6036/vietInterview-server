
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import session_service,ErpInstance,common_service,admin_service
import json, base64, os, datetime
from werkzeug.utils import secure_filename

@app.route('/employee/account/register', methods=['POST'],endpoint='employee-account-register')
def register():
    try:
        login = request.values['email']
        password = request.values['password']
        result = admin_service.createEmployee(login,password)
        return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Login error '
        print request.values
        return jsonify(result=False)

@app.route('/employee/account/login', methods=['POST'],endpoint='employee-account-login')
def login():
    try:
        login = request.values['email']
        password = request.values['password']
        token = session_service.login(app.config['ERP_DB'], login, password,'employee')
        if token:
            return jsonify(result=True,token=token)
        raise Exception('Invalid account %s or password %s' % (login, password))
    except Exception as exc:
        print(exc)
        print 'Login error '
        print request.values
        return jsonify(result=False)

@app.route('/employee/account/logout', methods=['POST'],endpoint='employee-logout')
def logout():
    try:
        session_service.logout(request.values['token'])
        return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Logout error '
        print request.values
        return jsonify(result=True)


@app.route('/employee/profile', methods=['GET','PUT'],endpoint='employee-profile')
def userProfile():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employee'])
         employee_service = erpInstance.service('career.employee_service')
         if request.method == 'GET':
            employee  = employee_service.getUserProfile()
            return jsonify(employee=employee)
         if request.method == 'PUT':
            employee  = json.loads(request.values['employee'])
            result = employee_service.updateUserProfile(employee)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'User profile error '
        print request.values
        return jsonify(result=False)



@app.route('/employee/profile/experience', methods=['GET','PUT','POST','DELETE'],endpoint='employee-profile-experience')
def workExperience():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employee'])
         employee_service = erpInstance.service('career.employee_service')
         if request.method == 'GET':
            expList  = employee_service.getWorkExperience()
            return jsonify(expList=expList)
         if request.method == 'POST':
            exp  = json.loads(request.values['exp'])
            expId = employee_service.addWorkExperience(exp)
            return jsonify(expId=expId)
         if request.method == 'PUT':
            exp  = json.loads(request.values['exp'])
            result = employee_service.updateWorkExperience(exp)
            return jsonify(result=result)
         if request.method == 'DELETE':
            expId  = int(request.values['expId'])
            result = employee_service.removeWorkExperience([expId])
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Work experience error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/profile/certificate', methods=['GET','PUT','POST','DELETE'],endpoint='employee-profile-certificate')
def certificate():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employee'])
         employee_service = erpInstance.service('career.employee_service')
         if request.method == 'GET':
            certList  = employee_service.getCertificate()
            return jsonify(certList=certList)
         if request.method == 'POST':
            cert  = json.loads(request.values['cert'])
            certId = employee_service.addCertificate(cert)
            return jsonify(certId=certId)
         if request.method == 'PUT':
            cert  = json.loads(request.values['cert'])
            result = employee_service.updateCertificate(cert)
            return jsonify(result=result)
         if request.method == 'DELETE':
            certId  = int(request.values['certId'])
            result = employee_service.removeCertificate([certId])
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Certificate error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/profile/education', methods=['GET','PUT','POST','DELETE'],endpoint='employee-profile-education')
def educationHistory():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employee'])
         employee_service = erpInstance.service('career.employee_service')
         if request.method == 'GET':
            eduList  = employee_service.getEducationHistory()
            return jsonify(eduList=eduList)
         if request.method == 'POST':
            edu  = json.loads(request.values['edu'])
            eduId = employee_service.addEducationHistory(edu)
            return jsonify(eduId=eduId)
         if request.method == 'PUT':
            edu  = json.loads(request.values['edu'])
            result = employee_service.updateEducationHistory(edu)
            return jsonify(result=result)
         if request.method == 'DELETE':
            eduId  = int(request.values['eduId'])
            result = employee_service.removeEducationHistory([eduId])
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Education history error '
        print request.values
        return jsonify(result=False)



@app.route('/employee/profile/document', methods=['GET','POST','DELETE'],endpoint='employee-profile-document')
def document():
    try:
         token  = request.values['token']
         erpInstance = ErpInstance.fromToken(token,['employee'])
         employee_service = erpInstance.service('career.employee_service')
         if request.method == 'GET':
            docList  = employee_service.getDocument()
            return jsonify(docList=docList)
         if request.method == 'POST':
            doc  = json.loads(request.values['doc'])
            base64FileData  = doc['filedata']
            filename = doc['filename']
            comment = doc['title']
            fileData = base64.urlsafe_b64decode(base64FileData.encode('UTF-8'))
            server_fname = os.path.join(app.config['FILE_UPLOAD_FOLDER'],  '%s%s' %( datetime.datetime.now().strftime('%S%M%H%m%d%Y') , secure_filename(filename)))
            with open(server_fname, 'wb') as theFile:
                theFile.write(fileData)
            docId = employee_service.addDocument(comment, filename, server_fname)
            return jsonify(docId=docId)
         if request.method == 'DELETE':
            docId  = int(request.values['docId'])
            result = employee_service.removeDocument([docId])
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Document error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/profile/application', methods=['GET'],endpoint='employee-profile-application')
def application():
    try:
         token  = request.values['token']
         if request.method == 'GET':
            sessionInfo = session_service.validateToken(token,['employee'])
            applicationList  = common_service.getApplicantHistory(sessionInfo['uid'])
            return jsonify(applicationList=applicationList)
    except Exception as exc:
        print(exc)
        print 'Application history error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/apply', methods=['POST'],endpoint='employee-apply')
def applyJob():
    try:
         token  = request.values['token']
         if request.method == 'POST':
            sessionInfo = session_service.validateToken(token,['employee'])
            assignmentId = int( request.values['assignmentId'])
            result = common_service.applyJob(sessionInfo['uid'],assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Apply job error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/company', methods=['GET'],endpoint='employee-company')
def company():
    try:
         if request.method == 'GET':
            assignmentId = int( request.values['assignmentId'])
            company = common_service.getCompanyInfo(assignmentId)
            return jsonify(company=company)
    except Exception as exc:
        print(exc)
        print 'Get company error '
        print request.values
        return jsonify(result=False)
