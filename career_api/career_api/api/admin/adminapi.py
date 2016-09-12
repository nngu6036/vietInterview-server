import json
from werkzeug.utils import secure_filename
from career_api.proxy import Session,admin_service, license_obj, company_obj,company_user_obj,license_service
from career_api.proxy import admin_session, work_exp_obj, certificate_obj, edu_hist_obj, document_obj
from career_api.proxy import assignment_obj,user_obj, license_category_obj, admin_obj
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


@app.route('/admin/account', methods=['GET', 'PUT', 'POST'], endpoint='admin-account')
@admin_session
def account(session):
    try:
        if request.method == 'GET':
            adminList = admin_obj.getAdmins()
            return jsonify(result=True, companyList=adminList)
        if request.method == 'PUT':
            admin = json.loads(request.values['admin'])
            admin_obj.updateAdmin(admin)
            return jsonify(result=True)
        if request.method == 'POST':
            admin = json.loads(request.values['admin'])
            adminId = admin_obj.createAdmin(admin)
            if adminId:
                return jsonify(result=True, employerId=adminId)
            else:
                return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Admin account error '
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


@app.route('/admin/license/category', methods=['GET', 'POST'], endpoint='admin-license-category')
@admin_session
def licenseCategory(session):
    try:
        if request.method == 'GET':
            licenseCategoryList = license_category_obj.getLicenseCategory()
            return jsonify(result=True, licenseCategoryList=licenseCategoryList)
        if request.method == 'POST':
            licenseCategory = json.loads(request.values['licenseCategory'])
            licenseCategoryId = license_category_obj.createLicenseCategory(licenseCategory)
            return jsonify(result=True, licenseCategoryId=licenseCategoryId)
    except Exception as exc:
        print(exc)
        print 'License category error '
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
            company_obj.get(int(company['id'])).updateCompany( company)
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


@app.route('/admin/company/renewlicense', methods=['PUT'], endpoint='admin-company-renewlicense')
@admin_session
def renewlicense(session):
    try:
        companyId = int(request.values['companyId'])
        licenseId = int(request.values['licenseId'])
        if license_service.get(int(licenseId)).renewLicense(companyId, licenseId):
            return jsonify(result=True)
        else:
            return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Company renew-license error '
        print request.values
        return jsonify(result=False)


@app.route('/admin/company/addlicense', methods=['PUT'], endpoint='admin-company-addlicense')
@admin_session
def addlicense(session):
    try:
        companyId = int(request.values['companyId'])
        licenseId = int(request.values['licenseId'])
        if license_service.get(int(licenseId)).addLicense(companyId, licenseId):
            return jsonify(result=True)
        else:
            return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Company add-license error'
        print request.values
        return jsonify(result=False)


@app.route('/admin/company/user', methods=['GET', 'PUT', 'POST', 'DELETE'], endpoint='admin-company-user')
@admin_session
def companyUser(session):
    try:
        if request.method == 'GET':
            companyId = int(request.values['companyId'])
            userList = company_obj.get(companyId).getCompanyUser()
            return jsonify(result=True, userList=userList)
        if request.method == 'PUT':
            user = json.loads(request.values['user'])
            company_user_obj.get(int(user['id'])).updateCompanyUser(user)
            return jsonify(result=True)
        if request.method == 'POST':
            user = json.loads(request.values['user'])
            companyId = int(request.values['companyId'])
            userId = company_obj.get(companyId).createCompanyUser(user)
            if userId:
                return jsonify(result=True, userId=userId)
            else:
                return jsonify(result=False)
        if request.method == 'DELETE':
            userId = request.values['userId']
            if company_user_obj.get(int(userId)).deleteCompanyUser(userId):
                return jsonify(result=True)
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
            assignment_obj.get(int(assignment['id'])).updateAssignment( assignment)
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
            if type(expList) is list:
                return jsonify(expList=expList)
            else:
                return jsonify(expList=[expList])
         if request.method == 'POST':
            exp  = json.loads(request.values['exp'])
            expId = user.addWorkExperience(exp)
            return jsonify(expId=expId)
         if request.method == 'PUT':
            exp  = json.loads(request.values['exp'])
            result = work_exp_obj.get(int(exp['id'])).updateWorkExperience(exp)
            return jsonify(result=result)
         if request.method == 'DELETE':
            expId  = int(request.values['expId'])
            result = work_exp_obj.get(expId).removeWorkExperience()
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
            if type(certList) is list:
                return jsonify(certList=certList)
            else:
                return jsonify(certList=[certList])
         if request.method == 'POST':
            cert  = json.loads(request.values['cert'])
            certId = user.addCertificate(cert)
            return jsonify(certId=certId)
         if request.method == 'PUT':
            cert  = json.loads(request.values['cert'])
            result = certificate_obj.get(int(cert['id'])).updateCertificate(cert)
            return jsonify(result=result)
         if request.method == 'DELETE':
            certId  = int(request.values['certId'])
            result = certificate_obj.get(certId).removeCertificate()
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
            if type(eduList) is list:
                return jsonify(eduList=eduList)
            else:
                return jsonify(eduList=[eduList])
         if request.method == 'POST':
            edu  = json.loads(request.values['edu'])
            eduId = user.addEducationHistory(edu)
            return jsonify(eduId=eduId)
         if request.method == 'PUT':
            edu  = json.loads(request.values['edu'])
            result = edu_hist_obj.get(int(edu['id'])).updateEducationHistory(edu)
            return jsonify(result=result)
         if request.method == 'DELETE':
            eduId  = int(request.values['eduId'])
            result = edu_hist_obj.get(eduId).removeEducationHistory()
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
            docId = user.addDocument(comment, filename, server_fname)
            return jsonify(docId=docId)
         if request.method == 'DELETE':
            docId  = int(request.values['docId'])
            result = document_obj.get(docId).removeDocument()
            return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Document error '
        print request.values
        return jsonify(result=False)