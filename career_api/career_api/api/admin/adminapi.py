import json

from career_api.proxy import ErpInstance, session_service
from flask import jsonify, request

from career_api import app


@app.route('/admin/account/login', methods=['POST'], endpoint='admin-account-login')
def login():
  try:
    login = request.values['login']
    password = request.values['password']
    token = session_service.login(app.config['ERP_DB'], login, password, 'admin')
    if token:
      return jsonify(result=True, token=token)
    raise Exception('Invalid account %s or password %s' % (login, password))
  except Exception as exc:
    print(exc)
    print 'Login error '
    print request.values
    return jsonify(result=False)


@app.route('/admin/license', methods=['GET', 'PUT'], endpoint='admin-license')
def license():
  try:
    token = request.values['token']
    erpInstance = ErpInstance.fromToken(token, ['admin'])
    admin_service = erpInstance.service('career.admin_service')
    if request.method == 'GET':
      licenseList = admin_service.getLicense()
      return jsonify(result=True, licenseList=licenseList)
    if request.method == 'PUT':
      license = json.loads(request.values['license'])
      admin_service.updateLicense(int(license['id']), license)
      return jsonify(result=True)
  except Exception as exc:
    print(exc)
    print 'License error '
    print request.values
    return jsonify(result=False)


@app.route('/admin/company', methods=['GET', 'PUT', 'POST'], endpoint='admin-company')
def company():
  try:
    token = request.values['token']
    erpInstance = ErpInstance.fromToken(token, ['admin'])
    admin_service = erpInstance.service('career.admin_service')
    if request.method == 'GET':
      companyList = admin_service.getCompany()
      return jsonify(result=True, companyList=companyList)
    if request.method == 'PUT':
      company = json.loads(request.values['company'])
      admin_service.updateCompany(int(company['id']), company)
      return jsonify(result=True)
    if request.method == 'POST':
      company = json.loads(request.values['company'])
      companyId = admin_service.createCompany(company)
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
def companyUser():
  try:
    token = request.values['token']
    erpInstance = ErpInstance.fromToken(token, ['admin'])
    admin_service = erpInstance.service('career.admin_service')
    if request.method == 'GET':
      companyId = int(request.values['companyId'])
      userList = admin_service.getCompanyUser(companyId)
      return jsonify(result=True, userList=userList)
    if request.method == 'PUT':
      user = json.loads(request.values['user'])
      admin_service.updateCompanyUser(int(user['id']), user)
      return jsonify(result=True)
    if request.method == 'POST':
      user = json.loads(request.values['user'])
      companyId = int(request.values['companyId'])
      userId = admin_service.createCompanyUser(companyId, user)
      if userId:
        return jsonify(result=True, userId=userId)
      else:
        return jsonify(result=False)
  except Exception as exc:
    print(exc)
    print 'Company user  error '
    print request.values
    return jsonify(result=False)



@app.route('/admin/company/license', methods=['GET','POST'], endpoint='admin-company-license')
def companyLicense():
  try:
    token = request.values['token']
    erpInstance = ErpInstance.fromToken(token, ['admin'])
    license_service = erpInstance.service('career.license_service')
    if request.method == 'GET':
      companyId = int(request.values['companyId'])
      licenseInfo = license_service.getLicenseStatistic(companyId)
      return jsonify(result=True, licenseInfo=licenseInfo)
    if request.method == 'POST':
      companyId = int(request.values['companyId'])
      action = request.values['action']
      result = False
      if action=='activate':
        result = license_service.activateLicense(companyId)
      if action=='deactivate':
        result = license_service.deactivateLicense(companyId)
      return jsonify(result=result)
  except Exception as exc:
    print(exc)
    print 'Company license  error '
    print request.values
    return jsonify(result=False)





@app.route('/admin/account/logout', methods=['POST'], endpoint='admin-logout')
def logout():
  try:
    session_service.logout(request.values['token'])
    return jsonify(result=True)
  except Exception as exc:
    print(exc)
    print 'Logout error '
    print request.values
    return jsonify(result=True)


@app.route('/admin/question', methods=['GET', 'POST', 'PUT'], endpoint='admin-question')
def question():
  try:
    token = request.values['token']
    erpInstance = ErpInstance.fromToken(token, ['admin'])
    content_service = erpInstance.service('career.content_service')
    if request.method == 'GET':
      lang = request.values['lang'] if 'lang' in request.values else False
      questionList = content_service.getQuestion(lang)
      return jsonify(result=True, questionList=questionList)
    if request.method == 'POST':
      question = json.loads(request.values['question'])
      lang = request.values['lang']
      if lang:
        result = content_service.createQuestionTranslation(question, lang)
        return jsonify(result=result)
      else:
        questionId = content_service.createQuestion(question)
        return jsonify(result=True, questionId=questionId)
    if request.method == 'PUT':
      question = json.loads(request.values['question'])
      lang = request.values['lang']
      if lang:
        result = content_service.updateQuestionTranslation(question, lang)
        return jsonify(result=result)
      else:
        result = content_service.updateQuestion(question)
        return jsonify(result=result)
    return jsonify(result=False)
  except Exception as exc:
    print(exc)
    print 'Question error '
    print request.values
    return jsonify(result=False)


@app.route('/admin/question/category', methods=['GET','POST','PUT'], endpoint='admin-question-category')
def questionCategory():
  try:
    token = request.values['token']
    erpInstance = ErpInstance.fromToken(token, ['admin'])
    content_service = erpInstance.service('career.content_service')
    if request.method == 'GET':
      lang = request.values['lang'] if 'lang' in request.values else False
      categoryList = content_service.getQuestionCategory(lang)
      return jsonify(result=True, categoryList=categoryList)
    if request.method == 'POST':
      category = json.loads(request.values['category'])
      lang = request.values['lang']
      if lang:
        result = content_service.createQuestionCategoryTranslation(category, lang)
        return jsonify(result=result)
      else:
        categoryId = content_service.createQuestionCategory(category)
        return jsonify(result=True, categoryId=categoryId)
    if request.method == 'PUT':
      category = json.loads(request.values['category'])
      lang = request.values['lang']
      if lang:
        result = content_service.updateQuestionCategoryTranslation(category, lang)
        return jsonify(result=result)
      else:
        result = content_service.updateQuestionCategory(category)
        return jsonify(result=result)
    return jsonify(result=False)
  except Exception as exc:
    print(exc)
    print 'Question category error '
    print request.values
    return jsonify(result=False)


@app.route('/admin/assessment', methods=['GET'], endpoint='admin-assessment')
def assessment():
  try:
    token = request.values['token']
    erpInstance = ErpInstance.fromToken(token, ['admin'])
    content_service = erpInstance.service('career.content_service')
    if request.method == 'GET':
      lang = request.values['lang'] if 'lang' in request.values else False
      assessment = content_service.getAssessment(lang)
      return jsonify(result=True, assessment=assessment)
  except Exception as exc:
    print(exc)
    print 'Assessment error '
    print request.values
    return jsonify(result=False)
