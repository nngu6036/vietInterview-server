import json

from career_api.proxy import Session,admin_service, license_obj, company_obj,company_user_obj,license_service,assignment_obj,user_obj
from career_api.proxy import admin_session,work_exp_obj,edu_hist_obj,certificate_obj,document_obj
from flask import jsonify, request
import base64
from career_api import app
import os
import datetime

@app.route('/admin/account/login', methods=['POST'], endpoint='admin-account-login')
def login():
    try:
        login = request.values['login']
        password = request.values['password']
        token = Session.start(login, password, 'admin')
        if token:
            return jsonify(result=True, token=token)
        raise Exception('Invalid account %s or password %s' % (login, password))
    except Exception as exc:
        print(exc)
        print 'Login error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/account/logout', methods=['POST'], endpoint='admin-logout')
def logout():
    try:
        Session.stop(request.values['token'])
        return jsonify(result=True)
    except Exception as exc:
        print(exc)
        print 'Logout error '
        print request.values
        return jsonify(result=True)


@app.route('/admin/license', methods=['GET', 'POST'], endpoint='admin-license')
@admin_session
def license(session):
    try:
        if request.method == 'GET':
            licenseList = license_obj.getLicense()
            return jsonify(result=True, licenseList=licenseList)
        if request.method == 'POST':
            license = json.loads(request.values['license'])
            licenseId = license_obj.createLicense(license)
            return jsonify(result=True, licenseId=licenseId)
    except Exception as exc:
        print(exc)
        print 'License error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/company', methods=['GET', 'PUT', 'POST'], endpoint='admin-company')
@admin_session
def company(session):
    try:
        if request.method == 'GET':
            companyList = company_obj.getCompany()
            return jsonify(result=True, companyList=companyList)
        if request.method == 'PUT':
            company = json.loads(request.values['company'])
            company_obj.updateCompany(int(company['id']), company)
            return jsonify(result=True)
        if request.method == 'POST':
            company = json.loads(request.values['company'])
            companyId = company_obj.createCompany(company)
            if companyId:
                return jsonify(result=True, employerId=companyId)
            else:
                return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Company  error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/company/user', methods=['GET', 'PUT', 'POST'], endpoint='admin-company-user')
@admin_session
def companyUser(session):
    try:
        if request.method == 'GET':
            companyId = int(request.values['companyId'])
            userList = company_obj.get(companyId).getCompanyUser()
            return jsonify(result=True, userList=userList)
        if request.method == 'PUT':
            user = json.loads(request.values['user'])
            company_user_obj.updateCompanyUser(int(user['id']), user)
            return jsonify(result=True)
        if request.method == 'POST':
            user = json.loads(request.values['user'])
            companyId = int(request.values['companyId'])
            userId = company_obj.get(companyId).createCompanyUser(user)
            if userId:
                return jsonify(result=True, userId=userId)
            else:
                return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Company user  error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/company/license', methods=['GET', 'POST'], endpoint='admin-company-license')
@admin_session
def companyLicense(session):
    try:
        if request.method == 'GET':
            companyId = int(request.values['companyId'])
            licenseInfo = company_obj.get(companyId).getLicenseStatistic()
            return jsonify(result=True, licenseInfo=licenseInfo)
        if request.method == 'POST':
            companyId = int(request.values['companyId'])
            action = request.values['action']
            result = False
            if action == 'activate':
                result = license_service.activateLicense(companyId)
            if action == 'deactivate':
                result = license_service.deactivateLicense(companyId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Company license  error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/assignment/approve', methods=['POST'], endpoint='admin-assignment-approve')
@admin_session
def assignmentApprove(session):
    try:
        if request.method == 'POST':
            assignmentId = int(request.values['assignmentId'])
            result = admin_service.approveAssignment(assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Approve Assignment error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/assignment', methods=['GET', 'PUT', 'POST', 'DELETE'], endpoint='admin-assignment')
@admin_session
def assignment(session):
    try:
        if request.method == 'GET':
            assignmentList = assignment_obj.getAssignment()
            return jsonify(result=True, assignmentList=assignmentList)
        if request.method == 'PUT':
            assignment = json.loads(request.values['assignment'])
            assignment_obj.updateAssignment(int(assignment['id']), assignment)
            return jsonify(result=True)
        if request.method == 'POST':
            companyId = int(request.values['companyId'])
            assignment = json.loads(request.values['assignment'])
            assignmentId = admin_service.createAssignment(companyId, assignment)
            if assignmentId:
                return jsonify(result=True, assignmentId=assignmentId)
            else:
                return jsonify(result=False)
        if request.method == 'DELETE':
            assignmentId = int(request.values['assignmentId'])
            result = admin_service.deleteAssignment(assignmentId)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Assignment error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/employee', methods=['GET', 'PUT', 'POST'], endpoint='admin-employee')
@admin_session
def employee(session):
    try:
        if request.method == 'GET':
            employeeList = user_obj.getEmployee()
            return jsonify(result=True, companyList=employeeList)
        if request.method == 'POST':
            login = request.values['email']
            password = request.values['password']
            employeeId = user_obj.createEmployee(login,password)
            if employeeId:
                return jsonify(result=True, employeeId=employeeId)
            else:
                return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Company  error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/employee/profile', methods=['GET','PUT'],endpoint='admin-employee-profile')
@admin_session
def employeeProfile(session):
    try:
         user = user_obj.get(int(request.values['employeeId']))
         if request.method == 'GET':
            employee  = user.getProfile()
            return jsonify(employee=employee)
         if request.method == 'PUT':
            employee  = json.loads(request.values['employee'])
            result = user.updateProfile(employee)
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'User profile error '
        print request.values
        return jsonify(result=False)



@app.route('/admin/employee/profile/experience', methods=['GET','PUT','POST','DELETE'],endpoint='admin-employee-profile-experience')
@admin_session
def workExperience(session):
    try:
         user = user_obj.get(int(request.values['employeeId']))
         if request.method == 'GET':
            expList  = user.getWorkExperience()
            return jsonify(expList=expList)
         if request.method == 'POST':
            exp  = json.loads(request.values['exp'])
            expId = user.addWorkExperience(exp)
            return jsonify(expId=expId)
         if request.method == 'PUT':
            exp  = json.loads(request.values['exp'])
            result = work_exp_obj.updateWorkExperience(exp)
            return jsonify(result=result)
         if request.method == 'DELETE':
            expId  = int(request.values['expId'])
            result = work_exp_obj.removeWorkExperience([expId])
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Work experience error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/employee/profile/certificate', methods=['GET','PUT','POST','DELETE'],endpoint='admin-employee-profile-certificate')
@admin_session
def certificate(session):
    try:
         user = user_obj.get(int(request.values['employeeId']))
         if request.method == 'GET':
            certList  = user.getCertificate()
            return jsonify(certList=certList)
         if request.method == 'POST':
            cert  = json.loads(request.values['cert'])
            certId = user.addCertificate(cert)
            return jsonify(certId=certId)
         if request.method == 'PUT':
            cert  = json.loads(request.values['cert'])
            result = certificate_obj.updateCertificate(cert)
            return jsonify(result=result)
         if request.method == 'DELETE':
            certId  = int(request.values['certId'])
            result = certificate_obj.removeCertificate([certId])
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Certificate error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/employee/profile/education', methods=['GET','PUT','POST','DELETE'],endpoint='admin-employee-profile-education')
@admin_session
def educationHistory(session):
    try:
         user = user_obj.get(int(request.values['employeeId']))
         if request.method == 'GET':
            eduList  = user.getEducationHistory()
            return jsonify(eduList=eduList)
         if request.method == 'POST':
            edu  = json.loads(request.values['edu'])
            eduId = user.addEducationHistory(edu)
            return jsonify(eduId=eduId)
         if request.method == 'PUT':
            edu  = json.loads(request.values['edu'])
            result = edu_hist_obj.updateEducationHistory(edu)
            return jsonify(result=result)
         if request.method == 'DELETE':
            eduId  = int(request.values['eduId'])
            result = edu_hist_obj.removeEducationHistory([eduId])
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Education history error '
        print request.values
        return jsonify(result=False)



@app.route('/admin/employee/profile/document', methods=['GET','POST','DELETE'],endpoint='admin-employee-profile-document')
@admin_session
def document(session):
    try:
         user = user_obj.get(int(request.values['employeeId']))
         if request.method == 'GET':
            docList  = user.getDocument()
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
            docId = user.addDocument(comment, filename, server_fname)
            return jsonify(docId=docId)
         if request.method == 'DELETE':
            docId  = int(request.values['docId'])
            result = document_obj.removeDocument([docId])
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Document error '
        print request.values
        return jsonify(result=False)