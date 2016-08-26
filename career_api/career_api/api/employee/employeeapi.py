
from flask import jsonify, request, abort
from career_api import app
from career_api.proxy import Session,common_service,user_obj
from career_api.proxy import employee_session,account_service
import json, base64, os, datetime
from werkzeug.utils import secure_filename

@app.route('/employee/account/register', methods=['POST'],endpoint='employee-account-register')
def register():
    try:
        login = request.values['email']
        password = request.values['password']
        result = user_obj.createEmployee(login,password)
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
        token = Session.start( login, password,'employee')
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
        Session.stop(request.values['token'])
        return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Logout error '
        print request.values
        return jsonify(result=True)


@app.route('/employee/profile', methods=['GET','PUT'],endpoint='employee-profile')
@employee_session
def userProfile(employee):
    try:
         if request.method == 'GET':
            profile  = employee.getProfile()
            return jsonify(employee=profile)
         if request.method == 'PUT':
            profile  = json.loads(request.values['employee'])
            result = employee.updateProfile(profile)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'User profile error '
        print request.values
        return jsonify(result=False)



@app.route('/employee/profile/experience', methods=['GET','PUT','POST','DELETE'],endpoint='employee-profile-experience')
@employee_session
def workExperience(employee):
    try:
         if request.method == 'GET':
            expList  = employee.getWorkExperience()
            if type(expList) is list:
                return jsonify(expList=expList)
            else:
                return jsonify(expList=[expList])
         if request.method == 'POST':
            exp  = json.loads(request.values['exp'])
            expId = employee.addWorkExperience(exp)
            return jsonify(expId=expId)
         if request.method == 'PUT':
            exp  = json.loads(request.values['exp'])
            result = employee.updateWorkExperience(exp)
            return jsonify(result=result)
         if request.method == 'DELETE':
            expId  = int(request.values['expId'])
            result = employee.removeWorkExperience(expId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Work experience error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/profile/certificate', methods=['GET','PUT','POST','DELETE'],endpoint='employee-profile-certificate')
@employee_session
def certificate(employee):
    try:
         if request.method == 'GET':
            certList  = employee.getCertificate()
            if type(certList) is list:
                return jsonify(certList=certList)
            else:
                return jsonify(certList=[certList])
         if request.method == 'POST':
            cert  = json.loads(request.values['cert'])
            certId = employee.addCertificate(cert)
            return jsonify(certId=certId)
         if request.method == 'PUT':
            cert  = json.loads(request.values['cert'])
            result = employee.updateCertificate(cert)
            return jsonify(result=result)
         if request.method == 'DELETE':
            certId  = int(request.values['certId'])
            result = employee.removeCertificate(certId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Certificate error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/profile/education', methods=['GET','PUT','POST','DELETE'],endpoint='employee-profile-education')
@employee_session
def educationHistory(employee):
    try:
         if request.method == 'GET':
            eduList  = employee.getEducationHistory()
            if type(eduList) is list:
                return jsonify(eduList=eduList)
            else:
                return jsonify(eduList=[eduList])
         if request.method == 'POST':
            edu  = json.loads(request.values['edu'])
            eduId = employee.addEducationHistory(edu)
            return jsonify(eduId=eduId)
         if request.method == 'PUT':
            edu  = json.loads(request.values['edu'])
            result = employee.updateEducationHistory(edu)
            return jsonify(result=result)
         if request.method == 'DELETE':
            eduId  = int(request.values['eduId'])
            result = employee.removeEducationHistory(eduId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Education history error '
        print request.values
        return jsonify(result=False)



@app.route('/employee/profile/document', methods=['GET','POST','DELETE'],endpoint='employee-profile-document')
@employee_session
def document(employee):
    try:
         if request.method == 'GET':
            docList  = employee.getDocument()
            if type(docList) is list:
                return jsonify(docList=docList)
            else:
                return jsonify(docList=[docList])
         if request.method == 'POST':
            doc  = json.loads(request.values['doc'])
            base64FileData  = doc['filedata']
            filename = doc['filename']
            comment = doc['title']
            fileData = base64.urlsafe_b64decode(base64FileData.encode('UTF-8'))
            server_fname = os.path.join(app.config['FILE_UPLOAD_FOLDER'],  '%s%s' %( datetime.datetime.now().strftime('%S%M%H%m%d%Y') , secure_filename(filename)))
            with open(server_fname, 'wb') as theFile:
                theFile.write(fileData)
            docId = employee.addDocument(comment, filename, server_fname)
            return jsonify(docId=docId)
         if request.method == 'DELETE':
            docId  = int(request.values['docId'])
            result = employee.removeDocument(docId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Document error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/profile/application', methods=['GET'],endpoint='employee-profile-application')
@employee_session
def application(employee):
    try:
         if request.method == 'GET':
            applicationList  = employee.getApplicantHistory()
            if type(applicationList) is list:
                return jsonify(applicationList=applicationList)
            else:
                return jsonify(applicationList=[applicationList])
    except Exception as exc:
        print(exc)
        print 'Application history error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/apply', methods=['POST'],endpoint='employee-apply')
@employee_session
def applyJob(employee):
    try:
         if request.method == 'POST':
            assignmentId = int( request.values['assignmentId'])
            result = employee.applyJob(assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Apply job error '
        print request.values
        return jsonify(result=False)


@app.route('/employee/account/changepass', methods=['POST'],endpoint='employee-account-changepass')
@employee_session
def changePass(employee):
    try:
        oldpass = request.values['oldpass']
        newpass = request.values['newpass']
        result = account_service.changePass( app.config['ERP_DB'],employee.user_id.login,oldpass,newpass)
        return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Change pass error '
        print request.values
        return jsonify(result=False)
